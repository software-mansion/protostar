use anyhow::{anyhow, Context, Result};
use camino::{Utf8Path, Utf8PathBuf};
use itertools::chain;
use scarb_metadata::{Metadata, PackageId};
use walkdir::WalkDir;
use std::collections::HashMap;
use cairo_lang_casm::hints::Hint;
use cairo_lang_casm::instructions::Instruction;
use cairo_vm::serde::deserialize_program::HintParams;
use cairo_lang_runner::casm_run::hint_to_hint_params;

use cairo_lang_protostar::casm_generator::TestConfig;
use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{SierraCasmRunner, StarknetState};
use cairo_lang_sierra::program::Program;
use cairo_lang_sierra_to_casm::metadata::MetadataComputationConfig;
use cairo_lang_utils::ordered_hash_map::OrderedHashMap;

use blockifier::transaction::transaction_utils_for_protostar::create_state_with_trivial_validation_account;

use crate::test_stats::TestsStats;

pub mod pretty_printing;
mod protostar_hint_processor;
mod test_stats;

use cairo_lang_runner::CairoHintProcessor as OriginalCairoHintProcessor;
use crate::protostar_hint_processor::CairoHintProcessor;

struct TestsFromFile {
    sierra_program: Program,
    tests_configs: Vec<TestConfig>,
    relative_path: Utf8PathBuf,
}

/// Builds hints_dict required in cairo_vm::types::program::Program from instructions.
pub fn build_hints_dict<'b>(
    instructions: impl Iterator<Item = &'b Instruction>,
) -> (HashMap<usize, Vec<HintParams>>, HashMap<String, Hint>) {
    let mut hints_dict: HashMap<usize, Vec<HintParams>> = HashMap::new();
    let mut string_to_hint: HashMap<String, Hint> = HashMap::new();

    let mut hint_offset = 0;

    for instruction in instructions {
        if !instruction.hints.is_empty() {
            // Register hint with string for the hint processor.
            for hint in instruction.hints.iter() {
                string_to_hint.insert(hint.to_string(), hint.clone());
            }
            // Add hint, associated with the instruction offset.
            hints_dict
                .insert(hint_offset, instruction.hints.iter().map(hint_to_hint_params).collect());
        }
        hint_offset += instruction.body.op_size();
    }
    (hints_dict, string_to_hint)
}

fn collect_tests_from_directory(
    input_path: &Utf8PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
    corelib_path: Option<&Utf8PathBuf>,
) -> Result<Vec<TestsFromFile>> {
    let test_files = find_cairo_files_in_directory(input_path)?;
    internal_collect_tests(input_path, linked_libraries, test_files, corelib_path)
}

fn find_cairo_files_in_directory(input_path: &Utf8PathBuf) -> Result<Vec<Utf8PathBuf>> {
    let mut test_files: Vec<Utf8PathBuf> = vec![];

    for entry in WalkDir::new(input_path).sort_by(|a, b| a.file_name().cmp(b.file_name())) {
        let entry =
            entry.with_context(|| format!("Failed to read directory at path = {input_path}"))?;
        let path = entry.path();

        if path.is_file() && path.extension().unwrap_or_default() == "cairo" {
            test_files.push(
                Utf8Path::from_path(path)
                    .with_context(|| format!("Failed to convert path = {path:?} to utf-8"))?
                    .to_path_buf(),
            );
        }
    }
    Ok(test_files)
}

fn internal_collect_tests(
    input_path: &Utf8PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
    test_files: Vec<Utf8PathBuf>,
    corelib_path: Option<&Utf8PathBuf>,
) -> Result<Vec<TestsFromFile>> {
    let builtins = vec!["GasBuiltin", "Pedersen", "RangeCheck", "bitwise", "ec_op"];

    let linked_libraries = linked_libraries;

    let mut tests = vec![];
    for ref test_file in test_files {
        let (sierra_program, tests_configs) = collect_tests(
            test_file.as_str(),
            None,
            linked_libraries.clone(),
            Some(builtins.clone()),
            corelib_path.map(|corelib_path| corelib_path.as_str()),
        )?;
        let relative_path = test_file.strip_prefix(input_path)?.to_path_buf();
        tests.push(TestsFromFile {
            sierra_program,
            tests_configs,
            relative_path,
        });
    }

    Ok(tests)
}

pub fn run_test_runner(
    input_path: &Utf8PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
    corelib_path: Option<&Utf8PathBuf>,
) -> Result<()> {
    let tests = collect_tests_from_directory(input_path, linked_libraries, corelib_path)?;

    pretty_printing::print_collected_tests_count(
        tests.iter().map(|tests| tests.tests_configs.len()).sum(),
        tests.len(),
    );

    let mut tests_stats = TestsStats::default();
    for tests_from_file in tests {
        run_tests(tests_from_file, &mut tests_stats)?;
    }
    pretty_printing::print_test_summary(tests_stats);

    Ok(())
}

fn run_tests(tests: TestsFromFile, tests_stats: &mut TestsStats) -> Result<()> {
    let mut runner = SierraCasmRunner::new(
        tests.sierra_program,
        Some(MetadataComputationConfig::default()),
        OrderedHashMap::default(),
    )
    .context("Failed setting up runner.")?;

    pretty_printing::print_running_tests(&tests.relative_path, tests.tests_configs.len());
    for config in tests.tests_configs {
        let available_gas = if let Some(available_gas) = &config.available_gas {
            Some(*available_gas)
        } else {
            Some(usize::MAX)
        };
        let mutable_runner = &mut runner;
        let func = mutable_runner.find_function(config.name.as_str())?;
        let initial_gas = mutable_runner.get_initial_available_gas(func, available_gas)?;
        let (entry_code, builtins) = mutable_runner.create_entry_code(func, &[], initial_gas)?;
        let footer = mutable_runner.create_code_footer();
        let instructions = chain!(
            entry_code.iter(),
            mutable_runner.casm_program.instructions.iter(),
            footer.iter()
        );
        let blockifier_state = create_state_with_trivial_validation_account();
        let (hints_dict, string_to_hint) = build_hints_dict(instructions.clone());
        let mut original_cairo_hint_processor = OriginalCairoHintProcessor {
            runner: Some(mutable_runner),
            starknet_state: StarknetState::default(),
            string_to_hint,
            blockifier_state: Some(blockifier_state),
        };
        // let blockifier_state = create_state_with_trivial_validation_account();
        let mut cairo_hint_processor = CairoHintProcessor {
            original_cairo_hint_processor: original_cairo_hint_processor,
            blockifier_state: Some(create_state_with_trivial_validation_account()),
        };
        let result = mutable_runner
            .run_function(
                mutable_runner.find_function(config.name.as_str())?,
                // &mut original_cairo_hint_processor, // working
                &mut cairo_hint_processor, // not working
                hints_dict,
                instructions,
                builtins,
            )
            .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;

        tests_stats.update(&result.value);
        pretty_printing::print_test_result(&config.name.clone(), &result.value);
    }
    Ok(())
}

pub fn dependencies_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<(Utf8PathBuf, Vec<LinkedLibrary>)> {
    let compilation_unit = metadata
        .compilation_units
        .iter()
        .filter(|unit| unit.package == *package)
        .min_by_key(|unit| match unit.target.name.as_str() {
            name @ "starknet-contract" => (0, name),
            name @ "lib" => (1, name),
            name => (2, name),
        })
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?;

    let base_path = metadata
        .get_package(package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .root
        .clone();

    let dependencies = compilation_unit
        .components
        .iter()
        .filter(|du| !du.source_path.to_string().contains("core/src"))
        .map(|cu| LinkedLibrary {
            name: cu.name.clone(),
            path: cu.source_root().to_owned().into_std_path_buf(),
        })
        .collect();

    Ok((base_path, dependencies))
}

#[cfg(test)]
mod tests {
    use super::*;
    use assert_fs::fixture::PathCopy;
    use scarb_metadata::MetadataCommand;

    #[test]
    fn get_dependencies_for_package() {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("tests/data/simple_test", &["**/*"]).unwrap();
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()
            .unwrap();

        let (_, dependencies) =
            dependencies_for_package(&scarb_metadata, &scarb_metadata.workspace.members[0])
                .unwrap();

        assert!(!dependencies.is_empty());
        assert!(dependencies.iter().all(|dep| dep.path.exists()));
    }

    #[test]
    fn get_dependencies_for_package_err_on_invalid_package() {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("tests/data/simple_test", &["**/*"]).unwrap();
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()
            .unwrap();

        let result =
            dependencies_for_package(&scarb_metadata, &PackageId::from(String::from("12345679")));
        let err = result.unwrap_err();

        assert!(err
            .to_string()
            .contains("Failed to find metadata for package"));
    }

    #[test]
    fn collecting_tests() {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("tests/data/simple_test", &["**/*"]).unwrap();
        let tests_path = Utf8PathBuf::from_path_buf(temp.to_path_buf()).unwrap();

        let tests = find_cairo_files_in_directory(&tests_path).unwrap();

        assert!(!tests.is_empty());
    }

    #[test]
    fn collecting_tests_err_on_invalid_dir() {
        let tests_path = Utf8PathBuf::from("aaee");

        let result = find_cairo_files_in_directory(&tests_path);
        let err = result.unwrap_err();

        assert!(err.to_string().contains("Failed to read directory at path"));
    }
}
