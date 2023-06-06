pub mod pretty_printing;

use crate::pretty_printing::print_test_summary;
use anyhow::{Context, Result};
use cairo_felt::Felt252;
use cairo_lang_protostar::casm_generator::TestConfig;
use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{RunResultValue, SierraCasmRunner};
use cairo_lang_sierra::program::Program;
use camino::{Utf8Path, Utf8PathBuf};
use serde::Deserialize;
use walkdir::WalkDir;

#[derive(Default)]
pub struct TestsStats {
    passed: u32,
    failed: u32,
}

#[derive(Deserialize, Debug)]
pub struct ProtostarTestConfig {
    #[serde(default)]
    exit_first: bool, // TODO Not implemented!
}

fn result_data_to_text(data: Vec<Felt252>) -> String {
    let mut readable_text = String::new();

    for felt in data {
        let felt_bytes = felt.to_bytes_be();
        let felt_text = std::str::from_utf8(&felt_bytes).unwrap_or("");
        readable_text.push_str(felt_text);
    }

    readable_text
}

fn get_result_str_and_update_tests_stats(
    run_result: RunResultValue,
    tests_stats: &mut TestsStats,
) -> String {
    match run_result {
        RunResultValue::Success(result_data) => {
            tests_stats.passed += 1;
            result_data_to_text(result_data)
        }
        RunResultValue::Panic(result_data) => {
            tests_stats.failed += 1;
            result_data_to_text(result_data)
        }
    }
}

fn collect_tests_in_directory(input_path: &Utf8PathBuf) -> Result<Vec<Utf8PathBuf>> {
    let mut test_directories: Vec<Utf8PathBuf> = vec![];

    for entry in WalkDir::new(input_path) {
        let entry =
            entry.with_context(|| format!("Failed to read directory at path = {}", input_path))?;
        let path = entry.path();

        if path.is_file() && path.extension().unwrap_or_default() == "cairo" {
            test_directories.push(
                Utf8Path::from_path(path)
                    .with_context(|| format!("Failed to convert path = {:?} to utf-8", path))?
                    .to_path_buf(),
            );
        }
    }

    Ok(test_directories)
}

pub fn run_test_runner(
    input_path: Utf8PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
    config: &ProtostarTestConfig,
) -> Result<()> {
    let test_directories = collect_tests_in_directory(&input_path)?;

    let mut tests_vector = vec![];

    let builtins = vec!["GasBuiltin", "Pedersen", "RangeCheck", "bitwise", "ec_op"];
    for test_dir in test_directories {
        let tests = collect_tests(
            test_dir.as_str(),
            None,
            linked_libraries.clone(),
            Some(builtins.clone()),
        )?;
        tests_vector.push(tests);
    }

    pretty_printing::print_collected_tests(
        tests_vector
            .iter()
            .fold(0, |acc, (_, e)| acc + e.len() as u32),
        tests_vector.len() as u32,
    );
    let mut tests_stats = TestsStats::default();
    for (sierra_program, test_configs) in tests_vector {
        run_tests(sierra_program, test_configs, &mut tests_stats)?;
    }
    print_test_summary(tests_stats);

    Ok(())
}

fn run_tests(
    sierra_program: Program,
    test_configs: Vec<TestConfig>,
    tests_stats: &mut TestsStats,
) -> Result<()> {
    let runner =
        SierraCasmRunner::new(sierra_program, Some(Default::default()), Default::default())
            .context("Failed setting up runner.")?;

    for config in &test_configs {
        let result = runner
            .run_function(
                runner.find_function(config.name.as_str())?,
                &[],
                if let Some(available_gas) = &config.available_gas {
                    Some(*available_gas)
                } else {
                    Some(usize::MAX)
                },
                Default::default(),
            )
            .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;

        let passed_before = tests_stats.passed;
        let name = config.name.clone();
        let result_str = get_result_str_and_update_tests_stats(result.value, tests_stats);
        pretty_printing::print_test_result(
            &name,
            &result_str,
            tests_stats.passed - passed_before > 0,
        );
    }
    Ok(())
}
