use std::any::Any;
use std::collections::HashMap;
use std::i64;

use anyhow::Result;
use blockifier::block_context::BlockContext;
use blockifier::execution::contract_class::{
    ContractClass as BlockifierContractClass, ContractClassV1,
};
use blockifier::state::cached_state::CachedState;
use blockifier::test_utils::DictStateReader;
use blockifier::transaction::account_transaction::AccountTransaction;
use blockifier::transaction::transaction_utils_for_protostar::{
    declare_tx_default, deploy_account_tx,
};
use blockifier::transaction::transactions::{DeclareTransaction, ExecutableTransaction};
use cairo_felt::Felt252;
use cairo_lang_starknet::casm_contract_class::CasmContractClass;
use cairo_lang_starknet::contract_class::ContractClass;
use cairo_vm::hint_processor::hint_processor_definition::HintProcessor;
use cairo_vm::types::exec_scope::ExecutionScopes;
use cairo_vm::vm::errors::hint_errors::HintError;
use cairo_vm::vm::vm_core::VirtualMachine;
use num_traits::cast::ToPrimitive;
use starknet_api::transaction::Fee;

use cairo_lang_casm::hints::Hint;
use cairo_lang_casm::hints::ProtostarHint;
use cairo_lang_runner::short_string::as_cairo_short_string;
use cairo_lang_runner::{
    casm_run::{cell_ref_to_relocatable, extract_buffer, get_ptr, get_val},
    insert_value_to_cellref, CairoHintProcessor as OriginalCairoHintProcessor,
};
use cairo_vm::hint_processor::hint_processor_definition::HintReference;
use cairo_vm::serde::deserialize_program::ApTracking;
use cairo_vm::vm::errors::vm_errors::VirtualMachineError;

pub struct CairoHintProcessor<'a> {
    pub original_cairo_hint_processor: OriginalCairoHintProcessor<'a>,
    pub blockifier_state: Option<CachedState<DictStateReader>>,
}

impl HintProcessor for CairoHintProcessor<'_> {
    fn execute_hint(
        &mut self,
        vm: &mut VirtualMachine,
        exec_scopes: &mut ExecutionScopes,
        hint_data: &Box<dyn Any>,
        constants: &HashMap<String, Felt252>,
    ) -> Result<(), HintError> {
        let maybe_extended_hint = hint_data.downcast_ref::<Hint>();
        if let Some(Hint::Protostar(hint)) = maybe_extended_hint {
            let blockifier_state = self
                .blockifier_state
                .as_mut()
                .expect("blockifier state is needed for executing hints");
            return execute_cheatcode_hint(vm, exec_scopes, hint, blockifier_state);
        }
        self.original_cairo_hint_processor
            .execute_hint(vm, exec_scopes, hint_data, constants)
    }

    /// Trait function to store hint in the hint processor by string.
    fn compile_hint(
        &self,
        hint_code: &str,
        _ap_tracking_data: &ApTracking,
        _reference_ids: &HashMap<String, usize>,
        _references: &HashMap<usize, HintReference>,
    ) -> Result<Box<dyn Any>, VirtualMachineError> {
        Ok(Box::new(
            self.original_cairo_hint_processor.string_to_hint[hint_code].clone(),
        ))
    }
}

#[allow(unused, clippy::too_many_lines)]
fn execute_cheatcode_hint(
    vm: &mut VirtualMachine,
    exec_scopes: &mut ExecutionScopes,
    hint: &ProtostarHint,
    blockifier_state: &mut CachedState<DictStateReader>,
) -> Result<(), HintError> {
    match hint {
        &ProtostarHint::StartRoll { .. } => todo!(),
        &ProtostarHint::StopRoll { .. } => todo!(),
        &ProtostarHint::StartWarp { .. } => todo!(),
        &ProtostarHint::StopWarp { .. } => todo!(),
        ProtostarHint::Declare {
            contract,
            result,
            err_code,
        } => {
            let contract_value = get_val(vm, contract)?;

            let contract_value_as_short_str =
                as_cairo_short_string(&contract_value).expect("conversion to short string failed");
            let current_dir = std::env::current_dir().expect("failed to obtain current dir");
            let paths = std::fs::read_dir(format!("{}/target/dev", current_dir.to_str().unwrap()))
                .expect("failed to read the file maybe build failed");
            let mut maybe_sierra_path: Option<String> = None;
            for path in paths {
                let path_str = path
                    .expect("path not resolved properly")
                    .path()
                    .to_str()
                    .expect("failed to convert path to string")
                    .to_string();
                if path_str.contains(&contract_value_as_short_str[..])
                    && path_str.contains(".sierra.json")
                {
                    maybe_sierra_path = Some(path_str);
                }
            }
            let file = std::fs::File::open(
                maybe_sierra_path.expect("no valid path to sierra file detected"),
            )
            .expect("file should open read only");
            let sierra_contract_class: ContractClass =
                serde_json::from_reader(file).expect("file should be proper JSON");

            let casm_contract_class =
                CasmContractClass::from_contract_class(sierra_contract_class, true)
                    .expect("sierra to casm failed");
            let casm_serialized =
                serde_json::to_string_pretty(&casm_contract_class).expect("serialization failed");

            let contract_class = ContractClassV1::try_from_json_string(&casm_serialized)
                .expect("error reading contract class from json");
            let contract_class = BlockifierContractClass::V1(contract_class);

            let declare_tx = declare_tx_default();
            let tx = DeclareTransaction {
                tx: starknet_api::transaction::DeclareTransaction::V1(declare_tx),
                contract_class,
            };
            let account_tx = AccountTransaction::Declare(tx);
            let block_context = &BlockContext::create_for_account_testing();

            let actual_execution_info = account_tx
                .execute(blockifier_state, block_context)
                .expect("error executing transaction declare");

            let class_hash = actual_execution_info
                .validate_call_info
                .as_ref()
                .expect("error reading validate call info of transaction")
                .call
                .class_hash
                .expect("error reading class hash of transaction");
            let class_hash_int =
                i64::from_str_radix(&class_hash.to_string().replace("0x", "")[..], 16)
                    .expect("error converting hex string to int");

            insert_value_to_cellref!(vm, result, Felt252::from(class_hash_int))?;
            // TODO https://github.com/software-mansion/protostar/issues/2024
            // in case of errors above, consider not panicking, set an error and return it here
            // instead
            insert_value_to_cellref!(vm, err_code, Felt252::from(0))?;
            Ok(())
        }
        &ProtostarHint::DeclareCairo0 { .. } => todo!(),
        &ProtostarHint::StartPrank { .. } => todo!(),
        &ProtostarHint::StopPrank { .. } => todo!(),
        &ProtostarHint::Invoke { .. } => todo!(),
        &ProtostarHint::MockCall { .. } => todo!(),
        ProtostarHint::Deploy {
            prepared_contract_address,
            prepared_class_hash,
            prepared_constructor_calldata_start,
            prepared_constructor_calldata_end,
            deployed_contract_address,
            panic_data_start,
            panic_data_end,
        } => {
            let contract_address = get_val(vm, prepared_contract_address)?;
            let class_hash = get_val(vm, prepared_class_hash)?;

            let as_relocatable = |vm, value| {
                let (base, offset) = extract_buffer(value);
                get_ptr(vm, base, &offset)
            };
            let mut curr = as_relocatable(vm, prepared_constructor_calldata_start)?;
            let end = as_relocatable(vm, prepared_constructor_calldata_end)?;
            let mut calldata: Vec<Felt252> = vec![];
            while curr != end {
                let value = vm.get_integer(curr)?;
                calldata.push(value.into_owned());
                curr += 1;
            }
            let class_hash_i128 =
                Felt252::to_i128(&class_hash).expect("failed to convert felt to i128");
            let class_hash_str = format!("{class_hash_i128:x}");
            let mut deploy_account_tx = deploy_account_tx(&class_hash_str, None, None);
            deploy_account_tx.max_fee = Fee(0);
            let account_tx = AccountTransaction::DeployAccount(deploy_account_tx);
            let block_context = &BlockContext::create_for_account_testing();
            let actual_execution_info = account_tx
                .execute(blockifier_state, block_context)
                .expect("error executing transaction deploy");

            insert_value_to_cellref!(vm, deployed_contract_address, contract_address)?;
            // todo in case of error, consider filling the panic data instead of packing in rust
            insert_value_to_cellref!(vm, panic_data_start, Felt252::from(0))?;
            insert_value_to_cellref!(vm, panic_data_end, Felt252::from(0))?;

            Ok(())
        }
        &ProtostarHint::Prepare { .. } => todo!(),
        &ProtostarHint::Call { .. } => todo!(),
        ProtostarHint::Print { start, end } => {
            let as_relocatable = |vm, value| {
                let (base, offset) = extract_buffer(value);
                get_ptr(vm, base, &offset)
            };

            let mut curr = as_relocatable(vm, start)?;
            let end = as_relocatable(vm, end)?;

            while curr != end {
                let value = vm.get_integer(curr)?;
                if let Some(shortstring) = as_cairo_short_string(&value) {
                    println!("original value: [{value}], converted to a string: [{shortstring}]",);
                } else {
                    println!("original value: [{value}]");
                }
                curr += 1;
            }

            Ok(())
        }
    }
}