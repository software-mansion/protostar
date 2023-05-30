use anyhow::{Context, Result};
use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{RunResultValue, SierraCasmRunner};
use serde::Deserialize;
use std::path::PathBuf;
use walkdir::WalkDir;

fn run_result_value_to_string(run_result: RunResultValue) -> String {
    return match run_result {
        RunResultValue::Success(data) => format!("Success {:?}", data),
        RunResultValue::Panic(data) => format!("Panic {:?}", data),
    };
}

fn collect_tests_in_directory(input_path: &PathBuf) -> Result<Vec<PathBuf>> {
    let mut test_directories: Vec<PathBuf> = vec![];

    for entry in WalkDir::new(input_path) {
        let entry = entry.context(format!(
            "Failed to read directory at path = {}",
            input_path.display()
        ))?;
        let path = entry.path();

        if path.is_file() && path.extension().unwrap_or_default() == "cairo" {
            test_directories.push(path.to_path_buf());
        }
    }

    Ok(test_directories)
}

pub fn run_tests(
    input_path: PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
    config: &ProtostarTestConfig,
) -> Result<()> {
    let test_directories = collect_tests_in_directory(&input_path)?;
    for test in test_directories {
        run_tests_in_file(test, linked_libraries.clone())?;
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

    let runner =
        SierraCasmRunner::new(sierra_program, Some(Default::default()), Default::default())
            .context("Failed setting up runner.")?;

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

#[derive(Deserialize, Debug)]
pub struct ProtostarTestConfig {
    exit_first: Option<bool>,
    ignore: Option<Vec<String>>,
    json: Option<bool>,
    last_failed: Option<bool>,
    report_slowest_tests: Option<bool>,
}
