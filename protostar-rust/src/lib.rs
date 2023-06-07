use std::collections::HashMap;
use std::fmt::Debug;

use anyhow::{Context, Result};
use camino::{Utf8Path, Utf8PathBuf};
use serde::Deserialize;
use walkdir::WalkDir;

use cairo_lang_protostar::casm_generator::TestConfig;
use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{SierraCasmRunner, StarknetState};
use cairo_lang_sierra::program::Program;
use cairo_lang_sierra_to_casm::metadata::MetadataComputationConfig;

use crate::test_stats::TestsStats;

pub mod pretty_printing;
mod test_stats;

#[derive(Deserialize, Debug)]
pub struct ProtostarTestConfig {
    #[serde(default)]
    exit_first: bool, // TODO Not implemented!
}

type TestInstance = (Program, Vec<TestConfig>, Utf8PathBuf);

fn collect_tests_from_directory(
    input_path: &Utf8PathBuf,
    linked_libraries: &Option<Vec<LinkedLibrary>>,
) -> Result<Vec<TestInstance>> {
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

    internal_collect_tests(input_path, linked_libraries, test_files)
}

fn internal_collect_tests(
    input_path: &Utf8PathBuf,
    linked_libraries: &Option<Vec<LinkedLibrary>>,
    test_files: Vec<Utf8PathBuf>,
) -> Result<Vec<(Program, Vec<TestConfig>, Utf8PathBuf)>> {
    let mut tests = vec![];

    let builtins = vec!["GasBuiltin", "Pedersen", "RangeCheck", "bitwise", "ec_op"];
    for ref test_file in test_files {
        let (sierra_program, test_configs) = collect_tests(
            test_file.as_str(),
            None,
            linked_libraries.clone(),
            Some(builtins.clone()),
        )?;
        let relative_path_test_file = test_file.strip_prefix(input_path)?.to_path_buf();
        tests.push((sierra_program, test_configs, relative_path_test_file));
    }

    Ok(tests)
}

pub fn run_test_runner(
    input_path: &Utf8PathBuf,
    linked_libraries: &Option<Vec<LinkedLibrary>>,
    config: &ProtostarTestConfig,
) -> Result<()> {
    let tests = collect_tests_from_directory(input_path, linked_libraries)?;

    pretty_printing::print_collected_tests_count(
        tests.iter().map(|(_, e, _)| e.len()).sum(),
        tests.len(),
    );

    let mut tests_stats = TestsStats::default();
    for (sierra_program, test_configs, test_file) in tests {
        run_tests(sierra_program, &test_configs, &test_file, &mut tests_stats)?;
    }
    pretty_printing::print_test_summary(tests_stats);

    Ok(())
}

fn run_tests(
    sierra_program: Program,
    test_configs: &[TestConfig],
    test_file: &Utf8Path,
    tests_stats: &mut TestsStats,
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

        tests_stats.update(&result.value);
        pretty_printing::print_test_result(&config.name.clone(), &result.value);
    }
    Ok(())
}
