use std::collections::HashMap;

use anyhow::Result;
use blockifier::transaction::transaction_utils_for_protostar::create_state_with_trivial_validation_account;
use cairo_vm::serde::deserialize_program::HintParams;
use itertools::{chain, Itertools};

use cairo_felt::Felt252;
use cairo_lang_casm::hints::Hint;
use cairo_lang_casm::instructions::Instruction;
use cairo_lang_runner::casm_run::hint_to_hint_params;
use cairo_lang_runner::{
    CairoHintProcessor as CoreCairoHintProcessor, RunResultValue, RunnerError,
};
use cairo_lang_runner::{RunResult, SierraCasmRunner, StarknetState};
use test_collector::TestConfig;

use crate::cheatcodes_hint_processor::CairoHintProcessor;

/// Builds `hints_dict` required in `cairo_vm::types::program::Program` from instructions.
fn build_hints_dict<'b>(
    instructions: impl Iterator<Item = &'b Instruction>,
) -> (HashMap<usize, Vec<HintParams>>, HashMap<String, Hint>) {
    let mut hints_dict: HashMap<usize, Vec<HintParams>> = HashMap::new();
    let mut string_to_hint: HashMap<String, Hint> = HashMap::new();

    let mut hint_offset = 0;

    for instruction in instructions {
        if !instruction.hints.is_empty() {
            // Register hint with string for the hint processor.
            for hint in &instruction.hints {
                string_to_hint.insert(hint.to_string(), hint.clone());
            }
            // Add hint, associated with the instruction offset.
            hints_dict.insert(
                hint_offset,
                instruction.hints.iter().map(hint_to_hint_params).collect(),
            );
        }
        hint_offset += instruction.body.op_size();
    }
    (hints_dict, string_to_hint)
}

pub(crate) fn run_from_test_config(
    runner: &mut SierraCasmRunner,
    config: &TestConfig,
) -> Result<RunResult> {
    let available_gas = if let Some(available_gas) = &config.available_gas {
        Some(*available_gas)
    } else {
        Some(usize::MAX)
    };
    let func = runner.find_function(config.name.as_str())?;
    let initial_gas = runner.get_initial_available_gas(func, available_gas)?;
    let (entry_code, builtins) = runner.create_entry_code(func, &[], initial_gas)?;
    let footer = runner.create_code_footer();
    let instructions = chain!(
        entry_code.iter(),
        runner.get_casm_program().instructions.iter(),
        footer.iter()
    );
    let (hints_dict, string_to_hint) = build_hints_dict(instructions.clone());
    let core_cairo_hint_processor = CoreCairoHintProcessor {
        runner: Some(runner),
        starknet_state: StarknetState::default(),
        string_to_hint,
        blockifier_state: Some(create_state_with_trivial_validation_account()),
    };
    let mut cairo_hint_processor = CairoHintProcessor {
        original_cairo_hint_processor: core_cairo_hint_processor,
        blockifier_state: Some(create_state_with_trivial_validation_account()),
    };

    // TODO(2176) 1: Add custom class wrapping RunResult
    match runner.run_function(
        runner.find_function(config.name.as_str())?,
        &mut cairo_hint_processor,
        hints_dict,
        instructions,
        builtins,
    ) {
        Ok(result) => Ok(result),
        // CairoRunError comes from VirtualMachineError which may come from HintException that originates in the cheatcode processor
        Err(RunnerError::CairoRunError(_)) => Ok(RunResult {
            gas_counter: None,
            memory: vec![],
            // TODO(2176) 2: add the string during creating custom class instance (recover it from the CairoRunError)
            value: RunResultValue::Panic(
                vec![4_417_637, 6_386_787, 7_300_197, 2_123_122, 7_499_634] // "Cheatcode error"
                    .into_iter()
                    .map(Felt252::from)
                    .collect_vec(),
            ),
        }),
        Err(err) => Err(err.into()),
    }
}
