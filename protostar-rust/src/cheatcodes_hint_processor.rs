use std::any::Any;
use std::collections::hash_map::DefaultHasher;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::path::PathBuf;
use std::{fs, i64};

use anyhow::Result;
use blockifier::block_context::BlockContext;
use blockifier::execution::contract_class::{
    ContractClass as BlockifierContractClass, ContractClassV1,
};
use blockifier::state::cached_state::CachedState;
use blockifier::state::state_api::StateReader;
use blockifier::test_utils::{DictStateReader, TEST_ACCOUNT_CONTRACT_ADDRESS};
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
use starknet_api::transaction::{DeclareTransactionV0V1, Fee};

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
use serde::Deserialize;
use starknet_api::core::{ClassHash, ContractAddress, PatriciaKey};
use starknet_api::hash::{StarkFelt, StarkHash};
use starknet_api::{patricia_key, stark_felt};

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

#[allow(dead_code)]
#[derive(Deserialize)]
struct ScarbStarknetArtifacts {
    version: u32,
    contracts: Vec<ScarbStarknetContract>,
}

#[allow(dead_code)]
#[derive(Deserialize)]
struct ScarbStarknetContract {
    id: String,
    package_name: String,
    contract_name: String,
    artifacts: ScarbStarknetContractArtifact,
}

#[allow(dead_code)]
#[derive(Deserialize)]
struct ScarbStarknetContractArtifact {
    sierra: PathBuf,
    casm: Option<PathBuf>,
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

            let contract_value_as_short_str = as_cairo_short_string(&contract_value)
                .expect("Converting contract name to short string failed");
            let current_dir = std::env::current_dir()
                .expect("Failed to get current directory")
                .join("target/dev");

            let mut paths = std::fs::read_dir(&current_dir)
                .expect("Failed to read ./target/dev, maybe scarb build failed?");

            let starknet_artifacts = &paths
                .find_map(|path| match path {
                    Ok(path) => {
                        let name = path.file_name().into_string().ok()?;
                        name.contains("starknet_artifacts").then_some(path)
                    }
                    Err(_) => None,
                })
                .expect("Failed to find starknet_artifacts.json file");
            let starknet_artifacts = fs::read_to_string(starknet_artifacts.path())
                .expect("Failed to read starknet_artifacts.json contents");
            let starknet_artifacts: ScarbStarknetArtifacts =
                serde_json::from_str(starknet_artifacts.as_str())
                    .expect("Failed to parse starknet_artifacts.json contents");

            let sierra_path = starknet_artifacts.contracts.iter().find_map(|contract| {
                if contract.contract_name == contract_value_as_short_str {
                    return Some(contract.artifacts.sierra.clone());
                }
                None
            }).unwrap_or_else(|| panic!("Failed to find contract {contract_value_as_short_str} in starknet_artifacts.json"));
            let sierra_path = current_dir.join(sierra_path);

            let file = std::fs::File::open(&sierra_path)
                .unwrap_or_else(|_| panic!("Failed to open file at path = {:?}", &sierra_path));
            let sierra_contract_class: ContractClass = serde_json::from_reader(&file)
                .unwrap_or_else(|_| panic!("File to parse json from file = {file:?}"));

            let casm_contract_class =
                CasmContractClass::from_contract_class(sierra_contract_class, true)
                    .expect("sierra to casm failed");
            let casm_serialized = serde_json::to_string_pretty(&casm_contract_class)
                .expect("Failed to serialize contract to casm");

            let contract_class = ContractClassV1::try_from_json_string(&casm_serialized)
                .expect("Failed to read contract class from json");
            let contract_class = BlockifierContractClass::V1(contract_class);

            // TODO(#2134) replace this. Hash should be calculated by the blockifier in the correct manner. This is just a workaround.
            let mut hasher = DefaultHasher::new();
            casm_serialized.hash(&mut hasher);
            let class_hash = hasher.finish();
            let class_hash = ClassHash(stark_felt!(class_hash));

            let nonce = blockifier_state
                .get_nonce_at(ContractAddress(patricia_key!(
                    TEST_ACCOUNT_CONTRACT_ADDRESS
                )))
                .expect("Failed to get nonce");

            let declare_tx = declare_tx_default();
            let declare_tx = DeclareTransactionV0V1 {
                nonce,
                class_hash,
                ..declare_tx
            };
            let tx = DeclareTransaction {
                tx: starknet_api::transaction::DeclareTransaction::V1(declare_tx),
                contract_class,
            };
            let account_tx = AccountTransaction::Declare(tx);
            let block_context = &BlockContext::create_for_account_testing();

            let actual_execution_info = account_tx
                .execute(blockifier_state, block_context)
                .expect("Failed to execute declare transaction");

            let class_hash_int =
                i64::from_str_radix(&class_hash.to_string().replace("0x", "")[..], 16)
                    .expect("Failed to convert hex string to int");

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
