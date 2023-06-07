use std::collections::HashMap;
use std::fmt::Debug;

use anyhow::{Context, Result};
use camino::{Utf8Path, Utf8PathBuf};
use serde::Deserialize;
use walkdir::WalkDir;

use cairo_lang_protostar::casm_generator::TestConfig;
use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{RunResultValue, SierraCasmRunner, StarknetState};
use cairo_lang_sierra::program::Program;
use cairo_lang_sierra_to_casm::metadata::MetadataComputationConfig;

use crate::pretty_printing::print_test_summary;

pub mod pretty_printing;

#[derive(Default, Clone, Copy)]
pub struct TestsStats {
    passed: usize,
    failed: usize,
}

#[derive(Deserialize, Debug)]
pub struct ProtostarTestConfig {
    #[serde(default)]
    exit_first: bool, // TODO Not implemented!
}

fn update_tests_stats(run_result: &RunResultValue, tests_stats: &mut TestsStats) {
    match run_result {
        RunResultValue::Success(_) => {
            tests_stats.passed += 1;
        }
        RunResultValue::Panic(_) => {
            tests_stats.failed += 1;
        }
    }
}

fn collect_tests_in_directory(input_path: &Utf8PathBuf) -> Result<Vec<Utf8PathBuf>> {
    let mut test_files: Vec<Utf8PathBuf> = vec![];

    for entry in WalkDir::new(input_path) {
        let entry =
            entry.with_context(|| format!("Failed to read directory at path = {}", input_path))?;
        let path = entry.path();

        if path.is_file() && path.extension().unwrap_or_default() == "cairo" {
            test_files.push(
                Utf8Path::from_path(path)
                    .with_context(|| format!("Failed to convert path = {:?} to utf-8", path))?
                    .to_path_buf(),
            );
        }
    }

    Ok(test_files)
}

pub fn run_test_runner(
    input_path: &Utf8PathBuf,
    linked_libraries: &Option<Vec<LinkedLibrary>>,
    config: &ProtostarTestConfig,
) -> Result<()> {
    let test_directories = collect_tests_in_directory(input_path)?;

    let mut tests_vector = vec![];

    let builtins = vec!["GasBuiltin", "Pedersen", "RangeCheck", "bitwise", "ec_op"];
    for ref test_file in test_directories {
        let (sierra_program, test_configs) = collect_tests(
            test_file.as_str(),
            None,
            linked_libraries.clone(),
            Some(builtins.clone()),
        )?;
        let relative_path_test_file = test_file.strip_prefix(input_path)?.to_path_buf();
        tests_vector.push((sierra_program, test_configs, relative_path_test_file));
    }

    pretty_printing::print_collected_tests_count(
        tests_vector.iter().map(|(_, e, _)| e.len()).sum(),
        tests_vector.len(),
    );
    let mut tests_stats = TestsStats::default();
    for (sierra_program, test_configs, test_file) in tests_vector {
        run_tests(sierra_program, &test_configs, &mut tests_stats, &test_file)?;
    }
    print_test_summary(tests_stats);

    Ok(())
}

fn run_tests(
    sierra_program: Program,
    test_configs: &[TestConfig],
    tests_stats: &mut TestsStats,
    test_file: &Utf8Path,
) -> Result<()> {
    let runner = SierraCasmRunner::new(
        sierra_program,
        Some(MetadataComputationConfig::default()),
        HashMap::default(),
    )
    .context("Failed setting up runner.")?;

    pretty_printing::print_running_tests(test_file, test_configs.len());
    for config in test_configs {
        let result = runner
            .run_function(
                runner.find_function(config.name.as_str())?,
                &[],
                if let Some(available_gas) = &config.available_gas {
                    Some(*available_gas)
                } else {
                    Some(usize::MAX)
                },
                StarknetState::default(),
            )
            .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;

        update_tests_stats(&result.value, tests_stats);
        pretty_printing::print_test_result(&config.name.clone(), &result.value);
    }
    Ok(())
}
