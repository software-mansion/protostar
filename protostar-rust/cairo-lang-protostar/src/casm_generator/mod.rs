//! Basic runner for running a Sierra program on the vm.
use std::collections::HashMap;

use cairo_felt::Felt252;
use cairo_lang_casm::instructions::Instruction;
use cairo_lang_casm::{casm, casm_extend};
use cairo_lang_sierra::extensions::bitwise::BitwiseType;
use cairo_lang_sierra::extensions::core::{CoreLibfunc, CoreType};
use cairo_lang_sierra::extensions::ec::EcOpType;
use cairo_lang_sierra::extensions::gas::GasBuiltinType;
use cairo_lang_sierra::extensions::pedersen::PedersenType;
use cairo_lang_sierra::extensions::range_check::RangeCheckType;
use cairo_lang_sierra::extensions::segment_arena::SegmentArenaType;
use cairo_lang_sierra::extensions::starknet::syscalls::SystemType;
use cairo_lang_sierra::extensions::{ConcreteType, NamedType};
use cairo_lang_sierra::program::Function;
use cairo_lang_sierra::program_registry::{ProgramRegistry, ProgramRegistryError};
use cairo_lang_sierra_ap_change::{calc_ap_changes, ApChangeError};
use cairo_lang_sierra_gas::gas_info::GasInfo;
use cairo_lang_sierra_to_casm::compiler::{CairoProgram, CompilationError};
use cairo_lang_sierra_to_casm::metadata::{calc_metadata, Metadata, MetadataError};
use cairo_lang_utils::bigint::{deserialize_big_uint, serialize_big_uint, BigUintAsHex};
use cairo_lang_sierra_type_size::{get_type_size_map, TypeSizeMap};
use cairo_vm::vm::errors::vm_errors::VirtualMachineError;
use itertools::chain;
use num_bigint::BigUint;
use num_integer::Integer;
use num_traits::{Num, Signed};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum GeneratorError {
    #[error("Failed calculating gas usage, it is likely a call for `get_gas` is missing.")]
    FailedGasCalculation,
    #[error("Function with suffix `{suffix}` to run not found.")]
    MissingFunction { suffix: String },
    #[error("Function expects arguments of size {expected} and received {actual} instead.")]
    ArgumentsSizeMismatch { expected: usize, actual: usize },
    #[error(transparent)]
    ProgramRegistryError(#[from] Box<ProgramRegistryError>),
    #[error(transparent)]
    SierraCompilationError(#[from] CompilationError),
    #[error(transparent)]
    ApChangeError(#[from] ApChangeError),
    #[error(transparent)]
    VirtualMachineError(#[from] Box<VirtualMachineError>),
    #[error("At least one test expected but none detected.")]
    NoTestsDetected,
}

#[derive(Default, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TestEntrypoint {
    pub offset: usize,
    pub name: String,
}

#[derive(Debug, PartialEq, Clone)]
pub struct TestConfig {
    pub name: String,
    pub available_gas: Option<usize>,
}

#[derive(Default, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProtostarCasm {
    #[serde(serialize_with = "serialize_big_uint", deserialize_with = "deserialize_big_uint")]
    pub prime: BigUint,
    pub bytecode: Vec<BigUintAsHex>,
    pub hints: Vec<(usize, Vec<String>)>,
    pub test_entry_points: Vec<TestEntrypoint>,
}

pub struct SierraCasmGenerator {
    /// The sierra program.
    sierra_program: cairo_lang_sierra::program::Program,
    /// Program registry for the Sierra program.
    sierra_program_registry: ProgramRegistry<CoreType, CoreLibfunc>,
    /// The casm program matching the Sierra code.
    casm_program: CairoProgram,
    /// Program registry for the Sierra program.
    type_sizes: TypeSizeMap,
}

impl SierraCasmGenerator {
    pub fn new(
        sierra_program: cairo_lang_sierra::program::Program,
    ) -> Result<Self, GeneratorError> {
        let metadata = create_metadata(&sierra_program, true)?;
        let sierra_program_registry =
            ProgramRegistry::<CoreType, CoreLibfunc>::new(&sierra_program)?;
        let casm_program =
            cairo_lang_sierra_to_casm::compiler::compile(&sierra_program, &metadata, true)
                .expect("Compilation failed.");
        let type_sizes = get_type_size_map(&sierra_program, &sierra_program_registry).unwrap();
        Ok(Self { sierra_program, sierra_program_registry, casm_program, type_sizes })
    }

    pub fn build_casm(
        &self,
        collected_tests: &Vec<TestConfig>,
    ) -> Result<ProtostarCasm, GeneratorError> {
        if collected_tests.is_empty() {
            return Err(GeneratorError::NoTestsDetected);
        }
        let mut entry_codes_offsets = Vec::new();
        for test in collected_tests {
            let func = self.find_function(&test.name)?;
            let initial_gas =
                if let Some(config_gas) = test.available_gas { config_gas } else { usize::MAX };
            let (_, _, offset) = self.create_entry_code(func, &vec![], initial_gas, 0)?;
            entry_codes_offsets.push(offset);
        }

        let mut entry_codes = Vec::new();
        let mut acc = entry_codes_offsets.iter().sum();
        acc -= entry_codes_offsets[0];
        let mut i = 0;
        for test in collected_tests {
            let func = self.find_function(&test.name)?;
            let initial_gas =
                if let Some(config_gas) = test.available_gas { config_gas } else { usize::MAX };
            let (proper_entry_code, _, _) =
                self.create_entry_code(func, &vec![], initial_gas, acc)?;
            if entry_codes_offsets.len() > i + 1 {
                acc -= entry_codes_offsets[i + 1];
                i += 1;
            }
            entry_codes.push(proper_entry_code);
        }

        let footer = self.create_code_footer();
        let prime = BigUint::from_str_radix(
            "800000000000011000000000000000000000000000000000000000000000001",
            16,
        )
        .unwrap();

        let mut bytecode = vec![];
        let mut hints = vec![];

        for entry_code in &entry_codes {
            for instruction in entry_code {
                if !instruction.hints.is_empty() {
                    hints.push((
                        bytecode.len(),
                        instruction.hints.iter().map(|hint| hint.to_string()).collect(),
                    ))
                }
                bytecode.extend(instruction.assemble().encode().iter().map(|big_int| {
                    let (_q, reminder) = big_int.magnitude().div_rem(&prime);

                    BigUintAsHex {
                        value: if big_int.is_negative() { &prime - reminder } else { reminder },
                    }
                }))
            }
        }

        for instruction in chain!(self.casm_program.instructions.iter(), footer.iter()) {
            if !instruction.hints.is_empty() {
                hints.push((
                    bytecode.len(),
                    instruction.hints.iter().map(|hint| hint.to_string()).collect(),
                ))
            }
            bytecode.extend(instruction.assemble().encode().iter().map(|big_int| {
                let (_q, reminder) = big_int.magnitude().div_rem(&prime);

                BigUintAsHex {
                    value: if big_int.is_negative() { &prime - reminder } else { reminder },
                }
            }))
        }

        let mut test_entry_points = Vec::new();
        let mut acc = 0;
        for (test, entry_code_offset) in collected_tests.iter().zip(entry_codes_offsets.iter()) {
            test_entry_points.push(TestEntrypoint { offset: acc, name: test.name.to_string() });
            acc += entry_code_offset;
        }
        Ok(ProtostarCasm { prime, bytecode, hints, test_entry_points })
    }

    // Copied from crates/cairo-lang-runner/src/lib.rs
    /// Finds first function ending with `name_suffix`.
    pub fn find_function(&self, name_suffix: &str) -> Result<&Function, GeneratorError> {
        self.sierra_program
            .funcs
            .iter()
            .find(|f| {
                if let Some(name) = &f.id.debug_name { name.ends_with(name_suffix) } else { false }
            })
            .ok_or_else(|| GeneratorError::MissingFunction { suffix: name_suffix.to_owned() })
    }

    // Copied from crates/cairo-lang-runner/src/lib.rs
    /// Returns the instructions to add to the beginning of the code to successfully call the main
    /// function, as well as the builtins required to execute the program.
    fn create_entry_code(
        &self,
        func: &Function,
        args: &[Felt252],
        initial_gas: usize,
        entry_offset: usize,
    ) -> Result<(Vec<Instruction>, Vec<String>, usize), GeneratorError> {
        let mut arg_iter = args.iter();
        let mut expected_arguments_size = 0;
        let mut ctx = casm! {};
        // The builtins in the formatting expected by the runner.
        let builtins: Vec<_> = ["pedersen", "range_check", "bitwise", "ec_op"]
            .map(&str::to_string)
            .into_iter()
            .collect();
        // The offset [fp - i] for each of this builtins in this configuration.
        let builtin_offset: HashMap<cairo_lang_sierra::ids::GenericTypeId, i16> = HashMap::from([
            (PedersenType::ID, 6),
            (RangeCheckType::ID, 5),
            (BitwiseType::ID, 4),
            (EcOpType::ID, 3),
        ]);
        if func
            .signature
            .param_types
            .iter()
            .any(|ty| self.get_info(ty).long_id.generic_id == SegmentArenaType::ID)
        {
            casm_extend! {ctx,
                // SegmentArena segment.
                %{ memory[ap + 0] = segments.add() %}
                // Infos segment.
                %{ memory[ap + 1] = segments.add() %}
                ap += 2;
                [ap + 0] = 0, ap++;
                // Write Infos segment, n_constructed (0), and n_destructed (0) to the segment.
                [ap - 2] = [[ap - 3]];
                [ap - 1] = [[ap - 3] + 1];
                [ap - 1] = [[ap - 3] + 2];
            }
        }
        for (i, ty) in func.signature.param_types.iter().enumerate() {
            let info = self.get_info(ty);
            let generic_ty = &info.long_id.generic_id;
            let ty_size = self.type_sizes[ty];
            if let Some(offset) = builtin_offset.get(generic_ty) {
                casm_extend! {ctx,
                    [ap + 0] = [fp - offset], ap++;
                }
            } else if generic_ty == &SystemType::ID {
                casm_extend! {ctx,
                    %{ memory[ap + 0] = segments.add() %}
                    ap += 1;
                }
            } else if generic_ty == &GasBuiltinType::ID {
                casm_extend! {ctx,
                    [ap + 0] = initial_gas, ap++;
                }
            } else if generic_ty == &SegmentArenaType::ID {
                let offset = -(i as i16) - 3;
                casm_extend! {ctx,
                    [ap + 0] = [ap + offset] + 3, ap++;
                }
            } else {
                let arg_size = ty_size;
                expected_arguments_size += arg_size as usize;
                for _ in 0..arg_size {
                    if let Some(value) = arg_iter.next() {
                        casm_extend! {ctx,
                            [ap + 0] = (value.to_bigint()), ap++;
                        }
                    }
                }
            }
        }
        if expected_arguments_size != args.len() {
            return Err(GeneratorError::ArgumentsSizeMismatch {
                expected: expected_arguments_size,
                actual: args.len(),
            });
        }
        let before_final_call = ctx.current_code_offset;
        let final_call_size = 3;

        let offset = final_call_size
            + entry_offset
            + self.casm_program.debug_info.sierra_statement_info[func.entry_point.0].code_offset;

        casm_extend! {ctx,
            call rel offset;
            ret;
        }
        assert_eq!(before_final_call + final_call_size, ctx.current_code_offset);
        Ok((ctx.instructions, builtins, ctx.current_code_offset))
    }

    // Copied from crates/cairo-lang-runner/src/lib.rs
    /// Creates a list of instructions that will be appended to the program's bytecode.
    pub fn create_code_footer(&self) -> Vec<Instruction> {
        casm! {
            // Add a `ret` instruction used in libfuncs that retrieve the current value of the `fp`
            // and `pc` registers.
            ret;
        }
        .instructions
    }

    pub fn get_info(
        &self,
        ty: &cairo_lang_sierra::ids::ConcreteTypeId,
    ) -> &cairo_lang_sierra::extensions::types::TypeInfo {
        self.sierra_program_registry.get_type(ty).unwrap().info()
    }
}

fn create_metadata(
    sierra_program: &cairo_lang_sierra::program::Program,
    calc_gas: bool,
) -> Result<Metadata, GeneratorError> {
    if calc_gas {
        calc_metadata(sierra_program, Default::default()).map_err(|err| match err {
            MetadataError::ApChangeError(err) => GeneratorError::ApChangeError(err),
            MetadataError::CostError(_) => GeneratorError::FailedGasCalculation,
        })
    } else {
        Ok(Metadata {
            ap_change_info: calc_ap_changes(sierra_program, |_, _| 0)?,
            gas_info: GasInfo {
                variable_values: Default::default(),
                function_costs: Default::default(),
            },
        })
    }
}
