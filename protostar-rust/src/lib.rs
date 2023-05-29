use anyhow::{anyhow, Context, Result};
use itertools::Itertools;
use std::path::PathBuf;
use walkdir::WalkDir;

use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{RunResultValue, SierraCasmRunner};
use cairo_lang_sierra_to_casm::metadata::MetadataComputationConfig;

fn run_result_value_to_string(run_result: RunResultValue) -> String {
    return match run_result {
        RunResultValue::Success(data) => format!("Success {:?}", data),
        RunResultValue::Panic(data) => format!("Panic {:?}", data),
    };
}

pub fn run_tests(input_path: PathBuf, linked_libraries: Option<Vec<LinkedLibrary>>) -> Result<()> {
    for entry in WalkDir::new(&input_path) {
        if entry.is_err() {
            continue;
        }

        let entry = entry.unwrap();
        let path = entry.path();

        if path.is_file() && path.extension().map_or(false, |ex| ex == "cairo") {
            run_tests_in_file(entry.path().to_path_buf(), linked_libraries.clone())?;
        }
    }
    Ok(())
}

fn run_tests_in_file(
    input_path: PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
) -> Result<()> {
    let builtins = vec!["GasBuiltin", "Pedersen", "RangeCheck", "bitwise", "ec_op"];

    let (sierra_program, test_configs) = collect_tests(
        input_path.to_str().unwrap(),
        None,
        linked_libraries,
        Some(builtins),
    )?;

    dbg!(&test_configs);

    let runner =
        SierraCasmRunner::new(sierra_program, Some(Default::default()), Default::default())
            .with_context(|| "Failed setting up runner.")?;

    for config in &test_configs {
        let result = runner
            .run_function(
                runner.find_function(&config.name.as_str())?,
                &[],
                Some(usize::MAX),
                Default::default(),
            )
            .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;
        let name = config.name.clone();
        let result_str = run_result_value_to_string(result.value);
        println!("{}: {}", name, result_str);
    }
    Ok(())
}

// #[pyfunction]
// fn run_tests(input_path: String) -> PyResult<()> {
//     internal_run_tests(&input_path.to_owned())
//         .map_err(|e| PyErr::new::<RuntimeError, _>(format!("{:?}", e)))?;
//
//     Ok(())
// }
//
// #[pymodule]
// fn rust_test_runner_bindings(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_wrapped(wrap_pyfunction!(run_tests))?;
//     Ok(())
// }
