use std::any::Any;
use std::collections::HashMap;
use std::{i64, str};

use anyhow::Result;
use blockifier::block_context::BlockContext;
use blockifier::state::cached_state::CachedState;
use blockifier::test_utils::DictStateReader;
use blockifier::transaction::account_transaction::AccountTransaction;
use blockifier::transaction::transaction_utils_for_protostar::{
    declare_tx_default, deploy_account_tx,
};
use blockifier::transaction::transactions::{DeclareTransaction, ExecutableTransaction};
use cairo_felt::Felt252;
use cairo_lang_casm::hints::{Hint, ProtostarHint, StarknetHint};
use cairo_lang_starknet::contract_class::ContractClass;
use cairo_lang_starknet::casm_contract_class::CasmContractClass;
use blockifier::execution::contract_class::{
    ContractClass as BlockifierContractClass, ContractClassV1,
};
use cairo_lang_casm::operand::ResOperand;
use cairo_lang_sierra::ids::FunctionId;
use cairo_vm::hint_processor::hint_processor_definition::{HintProcessor, HintReference};
use cairo_vm::serde::deserialize_program::ApTracking;
use cairo_vm::types::exec_scope::ExecutionScopes;
use cairo_vm::types::relocatable::Relocatable;
use cairo_vm::vm::errors::hint_errors::HintError;
use cairo_vm::vm::errors::vm_errors::VirtualMachineError;
use cairo_vm::vm::vm_core::VirtualMachine;
use starknet_api::transaction::Fee;
use num_traits::cast::ToPrimitive;
use num_traits::Zero;

use cairo_lang_runner::short_string::as_cairo_short_string;
use cairo_lang_runner::{
  Arg,
  RunResultValue,
  SierraCasmRunner,
  StarknetState,
  insert_value_to_cellref,
  deduct_gas,
  fail_syscall,
  casm_run::{
    execute_core_hint_base,
    get_val,
    extract_buffer,
    get_ptr,
    vm_get_range,
    MemBuffer,
    SyscallResult,
    cell_ref_to_relocatable,
    keccak,
    secp256k1_new,
    secp256k1_add,
    secp256k1_mul,
    secp256r1_add,
    secp256r1_new,
    secp256k1_get_xy,
    secp256k1_get_point_from_x,
    secp256r1_mul,
    secp256r1_get_point_from_x,
    secp256r1_get_xy,
    VMWrapper,
    segment_with_data,
    read_array_result_as_vec,
  },
};



/// HintProcessor for Cairo compiler hints.
pub struct CairoHintProcessor<'a> {
  /// The Cairo runner.
  #[allow(dead_code)]
  pub runner: Option<&'a SierraCasmRunner>,
  // A mapping from a string that represents a hint to the hint object.
  pub string_to_hint: HashMap<String, Hint>,
  // The starknet state.
  pub starknet_state: StarknetState,
  pub blockifier_state: Option<CachedState<DictStateReader>>,
}


impl HintProcessor for CairoHintProcessor<'_> {
  /// Trait function to execute a given hint in the hint processor.
  fn execute_hint(
      &mut self,
      vm: &mut VirtualMachine,
      exec_scopes: &mut ExecutionScopes,
      hint_data: &Box<dyn Any>,
      _constants: &HashMap<String, Felt252>,
  ) -> Result<(), HintError> {
      let hint = hint_data.downcast_ref::<Hint>().unwrap();
      let hint = match hint {
          Hint::Core(core_hint_base) => {
              return execute_core_hint_base(vm, exec_scopes, core_hint_base);
          }
          Hint::Protostar(hint) => {
              let blockifier_state = self
                  .blockifier_state
                  .as_mut()
                  .expect("blockifier state is needed for executing hints");
              return execute_protostar_hint(vm, exec_scopes, hint, blockifier_state);
          }
          Hint::Starknet(hint) => hint,
      };
      match hint {
          StarknetHint::SystemCall { system } => {
              self.execute_syscall(system, vm, exec_scopes)?;
          }
          StarknetHint::SetBlockNumber { value } => {
              self.starknet_state.exec_info.block_info.block_number = get_val(vm, value)?;
          }
          StarknetHint::SetSequencerAddress { value } => {
              self.starknet_state.exec_info.block_info.sequencer_address = get_val(vm, value)?;
          }
          StarknetHint::SetBlockTimestamp { value } => {
              self.starknet_state.exec_info.block_info.block_timestamp = get_val(vm, value)?;
          }
          StarknetHint::SetCallerAddress { value } => {
              self.starknet_state.exec_info.caller_address = get_val(vm, value)?;
          }
          StarknetHint::SetContractAddress { value } => {
              self.starknet_state.exec_info.contract_address = get_val(vm, value)?;
          }
          StarknetHint::SetVersion { value } => {
              self.starknet_state.exec_info.tx_info.version = get_val(vm, value)?;
          }
          StarknetHint::SetAccountContractAddress { value } => {
              self.starknet_state.exec_info.tx_info.account_contract_address =
                  get_val(vm, value)?;
          }
          StarknetHint::SetMaxFee { value } => {
              self.starknet_state.exec_info.tx_info.max_fee = get_val(vm, value)?;
          }
          StarknetHint::SetTransactionHash { value } => {
              self.starknet_state.exec_info.tx_info.transaction_hash = get_val(vm, value)?;
          }
          StarknetHint::SetChainId { value } => {
              self.starknet_state.exec_info.tx_info.chain_id = get_val(vm, value)?;
          }
          StarknetHint::SetNonce { value } => {
              self.starknet_state.exec_info.tx_info.nonce = get_val(vm, value)?;
          }
          StarknetHint::SetSignature { start, end } => {
              let (cell, offset) = extract_buffer(start);
              let start = get_ptr(vm, cell, &offset)?;
              let (cell, offset) = extract_buffer(end);
              let end = get_ptr(vm, cell, &offset)?;
              self.starknet_state.exec_info.tx_info.signature = vm_get_range(vm, start, end)?;
          }
          StarknetHint::PopLog {
              value,
              opt_variant,
              keys_start,
              keys_end,
              data_start,
              data_end,
          } => {
              let contract_address = get_val(vm, value)?;
              let mut res_segment = MemBuffer::new_segment(vm);
              let logs = self.starknet_state.logs.entry(contract_address).or_default();

              if let Some((keys, data)) = logs.pop_front() {
                  let keys_start_ptr = res_segment.ptr;
                  res_segment.write_data(keys.iter())?;
                  let keys_end_ptr = res_segment.ptr;

                  let data_start_ptr = res_segment.ptr;
                  res_segment.write_data(data.iter())?;
                  let data_end_ptr = res_segment.ptr;

                  // Option::Some variant
                  insert_value_to_cellref!(vm, opt_variant, 0)?;
                  insert_value_to_cellref!(vm, keys_start, keys_start_ptr)?;
                  insert_value_to_cellref!(vm, keys_end, keys_end_ptr)?;
                  insert_value_to_cellref!(vm, data_start, data_start_ptr)?;
                  insert_value_to_cellref!(vm, data_end, data_end_ptr)?;
              } else {
                  // Option::None variant
                  insert_value_to_cellref!(vm, opt_variant, 1)?;
              }
          }
      };
      Ok(())
  }

  /// Trait function to store hint in the hint processor by string.
  fn compile_hint(
      &self,
      hint_code: &str,
      _ap_tracking_data: &ApTracking,
      _reference_ids: &HashMap<String, usize>,
      _references: &HashMap<usize, HintReference>,
  ) -> Result<Box<dyn Any>, VirtualMachineError> {
      Ok(Box::new(self.string_to_hint[hint_code].clone()))
  }
}

impl<'a> CairoHintProcessor<'a> {
  /// Executes a syscall.
  fn execute_syscall(
      &mut self,
      system: &ResOperand,
      vm: &mut VirtualMachine,
      exec_scopes: &mut ExecutionScopes,
  ) -> Result<(), HintError> {
      let (cell, offset) = extract_buffer(system);
      let system_ptr = get_ptr(vm, cell, &offset)?;
      let mut system_buffer = MemBuffer::new(vm, system_ptr);
      let selector = system_buffer.next_felt252()?.to_bytes_be();
      let mut gas_counter = system_buffer.next_usize()?;
      let mut execute_handle_helper =
          |handler: &mut dyn FnMut(
              // The syscall buffer.
              &mut MemBuffer<'_>,
              // The gas counter.
              &mut usize,
          ) -> Result<SyscallResult, HintError>| {
              match handler(&mut system_buffer, &mut gas_counter)? {
                  SyscallResult::Success(values) => {
                      system_buffer.write(gas_counter)?;
                      system_buffer.write(Felt252::from(0))?;
                      system_buffer.write_data(values.into_iter())?;
                  }
                  SyscallResult::Failure(revert_reason) => {
                      system_buffer.write(gas_counter)?;
                      system_buffer.write(Felt252::from(1))?;
                      system_buffer.write_arr(revert_reason.into_iter())?;
                  }
              }
              Ok(())
          };
      match std::str::from_utf8(&selector).unwrap() {
          "StorageWrite" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.storage_write(
                  gas_counter,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_felt252()?.into_owned(),
              )
          }),
          "StorageRead" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.storage_read(
                  gas_counter,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_felt252()?.into_owned(),
              )
          }),
          "GetBlockHash" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.get_block_hash(gas_counter, system_buffer.next_u64()?)
          }),
          "GetExecutionInfo" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.get_execution_info(gas_counter, system_buffer)
          }),
          "EmitEvent" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.emit_event(gas_counter, system_buffer.next_arr()?, system_buffer.next_arr()?)
          }),
          "SendMessageToL1" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              let _to_address = system_buffer.next_felt252()?;
              let _payload = system_buffer.next_arr()?;
              deduct_gas!(gas_counter, 50);
              Ok(SyscallResult::Success(vec![]))
          }),
          "Keccak" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              keccak(gas_counter, system_buffer.next_arr()?)
          }),
          "Secp256k1New" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256k1_new(
                  gas_counter,
                  system_buffer.next_u256()?,
                  system_buffer.next_u256()?,
                  exec_scopes,
              )
          }),
          "Secp256k1Add" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256k1_add(
                  gas_counter,
                  exec_scopes,
                  system_buffer.next_usize()?,
                  system_buffer.next_usize()?,
              )
          }),
          "Secp256k1Mul" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256k1_mul(
                  gas_counter,
                  system_buffer.next_usize()?,
                  system_buffer.next_u256()?,
                  exec_scopes,
              )
          }),
          "Secp256k1GetPointFromX" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256k1_get_point_from_x(
                  gas_counter,
                  system_buffer.next_u256()?,
                  system_buffer.next_felt252()?.is_zero(),
                  exec_scopes,
              )
          }),
          "Secp256k1GetXy" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256k1_get_xy(gas_counter, system_buffer.next_usize()?, exec_scopes)
          }),
          "Secp256r1New" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256r1_new(
                  gas_counter,
                  system_buffer.next_u256()?,
                  system_buffer.next_u256()?,
                  exec_scopes,
              )
          }),
          "Secp256r1Add" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256r1_add(
                  gas_counter,
                  exec_scopes,
                  system_buffer.next_usize()?,
                  system_buffer.next_usize()?,
              )
          }),
          "Secp256r1Mul" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256r1_mul(
                  gas_counter,
                  system_buffer.next_usize()?,
                  system_buffer.next_u256()?,
                  exec_scopes,
              )
          }),
          "Secp256r1GetPointFromX" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256r1_get_point_from_x(
                  gas_counter,
                  system_buffer.next_u256()?,
                  system_buffer.next_felt252()?.is_zero(),
                  exec_scopes,
              )
          }),
          "Secp256r1GetXy" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              secp256r1_get_xy(gas_counter, system_buffer.next_usize()?, exec_scopes)
          }),
          "Deploy" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.deploy(
                  gas_counter,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_arr()?,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer,
              )
          }),
          "CallContract" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.call_contract(
                  gas_counter,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_arr()?,
                  system_buffer,
              )
          }),
          "LibraryCall" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.library_call(
                  gas_counter,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer.next_arr()?,
                  system_buffer,
              )
          }),
          "ReplaceClass" => execute_handle_helper(&mut |system_buffer, gas_counter| {
              self.replace_class(
                  gas_counter,
                  system_buffer.next_felt252()?.into_owned(),
                  system_buffer,
              )
          }),
          _ => panic!("Unknown selector for system call!"),
      }
  }

  /// Executes the `storage_write_syscall` syscall.
  fn storage_write(
      &mut self,
      gas_counter: &mut usize,
      addr_domain: Felt252,
      addr: Felt252,
      value: Felt252,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 1000);
      if !addr_domain.is_zero() {
          // Only address_domain 0 is currently supported.
          fail_syscall!(b"Unsupported address domain");
      }
      let contract = self.starknet_state.exec_info.contract_address.clone();
      self.starknet_state.storage.entry(contract).or_default().insert(addr, value);
      Ok(SyscallResult::Success(vec![]))
  }

  /// Executes the `storage_read_syscall` syscall.
  fn storage_read(
      &mut self,
      gas_counter: &mut usize,
      addr_domain: Felt252,
      addr: Felt252,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 100);
      if !addr_domain.is_zero() {
          // Only address_domain 0 is currently supported.
          fail_syscall!(b"Unsupported address domain");
      }
      let value = self
          .starknet_state
          .storage
          .get(&self.starknet_state.exec_info.contract_address)
          .and_then(|contract_storage| contract_storage.get(&addr))
          .cloned()
          .unwrap_or_else(|| Felt252::from(0));
      Ok(SyscallResult::Success(vec![value.into()]))
  }

  /// Executes the `get_block_hash_syscall` syscall.
  fn get_block_hash(
      &mut self,
      gas_counter: &mut usize,
      _block_number: u64,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 100);
      // TODO(Arni, 28/5/2023): Replace the temporary return value with the required value.
      //      One design suggestion - to preform a storage read. Have an arbitrary, hardcoded
      //      (For example, addr=1) contain the mapping from block number to block hash.
      fail_syscall!(b"GET_BLOCK_HASH_UNIMPLEMENTED");
  }

  /// Executes the `get_execution_info_syscall` syscall.
  fn get_execution_info(
      &mut self,
      gas_counter: &mut usize,
      vm: &mut dyn VMWrapper,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 50);
      let exec_info = &self.starknet_state.exec_info;
      let block_info = &exec_info.block_info;
      let tx_info = &exec_info.tx_info;
      let mut res_segment = MemBuffer::new_segment(vm);
      let signature_start = res_segment.ptr;
      res_segment.write_data(tx_info.signature.iter().cloned())?;
      let signature_end = res_segment.ptr;
      let tx_info_ptr = res_segment.ptr;
      res_segment.write(tx_info.version.clone())?;
      res_segment.write(tx_info.account_contract_address.clone())?;
      res_segment.write(tx_info.max_fee.clone())?;
      res_segment.write(signature_start)?;
      res_segment.write(signature_end)?;
      res_segment.write(tx_info.transaction_hash.clone())?;
      res_segment.write(tx_info.chain_id.clone())?;
      res_segment.write(tx_info.nonce.clone())?;
      let block_info_ptr = res_segment.ptr;
      res_segment.write(block_info.block_number.clone())?;
      res_segment.write(block_info.block_timestamp.clone())?;
      res_segment.write(block_info.sequencer_address.clone())?;
      let exec_info_ptr = res_segment.ptr;
      res_segment.write(block_info_ptr)?;
      res_segment.write(tx_info_ptr)?;
      res_segment.write(exec_info.caller_address.clone())?;
      res_segment.write(exec_info.contract_address.clone())?;
      Ok(SyscallResult::Success(vec![exec_info_ptr.into()]))
  }

  /// Executes the `emit_event_syscall` syscall.
  fn emit_event(
      &mut self,
      gas_counter: &mut usize,
      keys: Vec<Felt252>,
      data: Vec<Felt252>,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 50);
      let contract = self.starknet_state.exec_info.contract_address.clone();
      self.starknet_state.logs.entry(contract).or_default().push_front((keys, data));
      Ok(SyscallResult::Success(vec![]))
  }

  /// Executes the `deploy_syscall` syscall.
  fn deploy(
      &mut self,
      gas_counter: &mut usize,
      class_hash: Felt252,
      _contract_address_salt: Felt252,
      calldata: Vec<Felt252>,
      _deploy_from_zero: Felt252,
      vm: &mut dyn VMWrapper,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 50);

      // Assign an arbitrary address to the contract.
      let deployed_contract_address = self.starknet_state.get_next_id();

      // Prepare runner for running the constructor.
      let runner = self.runner.expect("Runner is needed for starknet.");
      let Some(contract_info) = runner.starknet_contracts_info.get(&class_hash) else {
          fail_syscall!(b"CLASS_HASH_NOT_FOUND");
      };

      // Call constructor if it exists.
      let (res_data_start, res_data_end) = if let Some(constructor) = &contract_info.constructor {
          // Replace the contract address in the context.
          let old_contract_address = std::mem::replace(
              &mut self.starknet_state.exec_info.contract_address,
              deployed_contract_address.clone(),
          );

          // Run the constructor.
          let res = self.call_entry_point(gas_counter, runner, constructor, calldata, vm);

          // Restore the contract address in the context.
          self.starknet_state.exec_info.contract_address = old_contract_address;
          match res {
              Ok(value) => value,
              Err(mut revert_reason) => {
                  fail_syscall!(revert_reason, b"CONSTRUCTOR_FAILED");
              }
          }
      } else {
          (Relocatable::from((0, 0)), Relocatable::from((0, 0)))
      };

      // Set the class hash of the deployed contract.
      self.starknet_state
          .deployed_contracts
          .insert(deployed_contract_address.clone(), class_hash);
      Ok(SyscallResult::Success(vec![
          deployed_contract_address.into(),
          res_data_start.into(),
          res_data_end.into(),
      ]))
  }

  /// Executes the `call_contract_syscall` syscall.
  fn call_contract(
      &mut self,
      gas_counter: &mut usize,
      contract_address: Felt252,
      selector: Felt252,
      calldata: Vec<Felt252>,
      vm: &mut dyn VMWrapper,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 50);

      // Get the class hash of the contract.
      let Some(class_hash) = self.starknet_state.deployed_contracts.get(&contract_address) else {
          fail_syscall!(b"CONTRACT_NOT_DEPLOYED");
      };

      // Prepare runner for running the ctor.
      let runner = self.runner.expect("Runner is needed for starknet.");
      let contract_info = runner
          .starknet_contracts_info
          .get(class_hash)
          .expect("Deployed contract not found in registry.");

      // Call the function.
      let Some(entry_point) = contract_info.externals.get(&selector) else {
          fail_syscall!(b"ENTRYPOINT_NOT_FOUND");
      };

      // Replace the contract address in the context.
      let old_contract_address = std::mem::replace(
          &mut self.starknet_state.exec_info.contract_address,
          contract_address.clone(),
      );
      let old_caller_address = std::mem::replace(
          &mut self.starknet_state.exec_info.caller_address,
          old_contract_address.clone(),
      );

      let res = self.call_entry_point(gas_counter, runner, entry_point, calldata, vm);

      // Restore the contract address in the context.
      self.starknet_state.exec_info.caller_address = old_caller_address;
      self.starknet_state.exec_info.contract_address = old_contract_address;

      match res {
          Ok((res_data_start, res_data_end)) => {
              Ok(SyscallResult::Success(vec![res_data_start.into(), res_data_end.into()]))
          }
          Err(mut revert_reason) => {
              fail_syscall!(revert_reason, b"ENTRYPOINT_FAILED");
          }
      }
  }

  /// Executes the `library_call_syscall` syscall.
  fn library_call(
      &mut self,
      gas_counter: &mut usize,
      class_hash: Felt252,
      selector: Felt252,
      calldata: Vec<Felt252>,
      vm: &mut dyn VMWrapper,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 50);
      // Prepare runner for running the call.
      let runner = self.runner.expect("Runner is needed for starknet.");
      let contract_info = runner
          .starknet_contracts_info
          .get(&class_hash)
          .expect("Deployed contract not found in registry.");

      // Call the function.
      let Some(entry_point) = contract_info.externals.get(&selector) else {
          fail_syscall!(b"ENTRYPOINT_NOT_FOUND");
      };
      match self.call_entry_point(gas_counter, runner, entry_point, calldata, vm) {
          Ok((res_data_start, res_data_end)) => {
              Ok(SyscallResult::Success(vec![res_data_start.into(), res_data_end.into()]))
          }
          Err(mut revert_reason) => {
              fail_syscall!(revert_reason, b"ENTRYPOINT_FAILED");
          }
      }
  }

  /// Executes the `replace_class_syscall` syscall.
  fn replace_class(
      &mut self,
      gas_counter: &mut usize,
      new_class: Felt252,
      _vm: &mut dyn VMWrapper,
  ) -> Result<SyscallResult, HintError> {
      deduct_gas!(gas_counter, 50);
      // Prepare runner for running the call.
      let address = self.starknet_state.exec_info.contract_address.clone();
      self.starknet_state.deployed_contracts.insert(address, new_class);
      Ok(SyscallResult::Success(vec![]))
  }

  /// Executes the entry point with the given calldata.
  fn call_entry_point(
      &mut self,
      gas_counter: &mut usize,
      runner: &SierraCasmRunner,
      entry_point: &FunctionId,
      calldata: Vec<Felt252>,
      vm: &mut dyn VMWrapper,
  ) -> Result<(Relocatable, Relocatable), Vec<Felt252>> {
      let function = runner
          .sierra_program_registry
          .get_function(entry_point)
          .expect("Entrypoint exists, but not found.");
      let mut res = runner
          .run_function_with_starknet_context(
              function,
              &[Arg::Array(calldata)],
              Some(*gas_counter),
              self.starknet_state.clone(),
          )
          .expect("Internal runner error.");

      *gas_counter = res.gas_counter.unwrap().to_usize().unwrap();
      self.starknet_state = std::mem::take(&mut res.starknet_state);
      match res.value {
          RunResultValue::Success(value) => {
              Ok(segment_with_data(vm, read_array_result_as_vec(&res.memory, &value).into_iter())
                  .expect("failed to allocate segment"))
          }
          RunResultValue::Panic(panic_data) => Err(panic_data),
      }
  }
}

#[allow(unused)]
fn execute_protostar_hint(
    vm: &mut VirtualMachine,
    exec_scopes: &mut ExecutionScopes,
    hint: &cairo_lang_casm::hints::ProtostarHint,
    blockifier_state: &mut CachedState<DictStateReader>,
) -> Result<(), HintError> {
    match hint {
        &ProtostarHint::StartRoll { .. } => todo!(),
        &ProtostarHint::StopRoll { .. } => todo!(),
        &ProtostarHint::StartWarp { .. } => todo!(),
        &ProtostarHint::StopWarp { .. } => todo!(),
        ProtostarHint::Declare { contract, result, err_code } => {
            let contract_value = get_val(vm, contract)?;

            let contract_value_as_short_str =
                as_cairo_short_string(&contract_value).expect("conversion to short string failed");

            let paths = std::fs::read_dir("./target/dev")
                .expect("failed to read ./target/dev, maybe build failed");
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
                contract_class: contract_class.clone(),
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
            let chint = Felt252::to_i128(&class_hash).expect("failed to convert felt to i128");
            let chstr = format!("{:x}", chint);
            let mut deploy_account_tx = deploy_account_tx(&chstr, None, None);
            deploy_account_tx.max_fee = Fee(0);
            let account_tx = AccountTransaction::DeployAccount(deploy_account_tx.clone());
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
                    println!(
                        "original value: [{}], converted to a string: [{}]",
                        value, shortstring
                    );
                } else {
                    println!("original value: [{}]", value);
                }
                curr += 1;
            }

            Ok(())
        }
    }
}
