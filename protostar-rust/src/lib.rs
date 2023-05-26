use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::types::PyDict;
use pyo3::exceptions::{PyValueError, PyRuntimeError};

use anyhow::Context;
use std::collections::HashMap;

use cairo_lang_protostar::test_collector::collect_tests;
use cairo_lang_runner::{RunResultValue, SierraCasmRunner, ProtostarTestConfig};

use blockifier::transaction::transaction_utils::create_state_with_trivial_validation_account;

fn run_result_value_to_string(run_result: RunResultValue) -> String {
    match run_result {
        RunResultValue::Success(data) => {
            return format!("Success {:?}", data);
        }
        RunResultValue::Panic(data) => {
            return format!("Panic {:?}", data);
        }
    }
}

fn internal_run_tests(input_path: &str, test_config: ProtostarTestConfig) -> anyhow::Result<()> {
    let (sierra_program, test_configs) = collect_tests(&input_path.to_owned(), None, None, None)?;

    let runner = SierraCasmRunner::new(sierra_program, None, HashMap::new())
        .with_context(|| "Failed setting up runner.")?;

    for config in &test_configs {
        let state = create_state_with_trivial_validation_account();
        let result = runner
            .run_function(
                runner.find_function(&config.name.as_str())?,
                &[],
                config.available_gas,
                Default::default(),
                Some(ProtostarTestConfig{ contracts_paths: test_config.contracts_paths.clone() }),
                Some(state),
            )
            .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;
        let name = config.name.clone();
        let result_str = run_result_value_to_string(result.value);
        println!("{}: {}", name, result_str);
    }
    Ok(())
}

#[pyfunction]
fn run_tests(input_path: String, contracts_paths_arg: &PyDict) -> PyResult<()> {
  let mut contracts_paths = HashMap::new();
  for key in contracts_paths_arg.keys() {
    let paths: Vec<String> = contracts_paths_arg.get_item(key).expect("a key has to have a value").extract().unwrap();
    if paths.len() > 1 {
      return Err(PyValueError::new_err(format!("Cairo 1 allows only 1 path per contract name, {} detected for name {}", paths.len(), key)));
    }
    let path = paths[0].clone();
    let key_converted: String = key.extract().unwrap();
    contracts_paths.insert(key_converted, path);
  }
  let test_config = ProtostarTestConfig{ contracts_paths };
    internal_run_tests(&input_path.to_owned(), test_config)
        .map_err(|e| PyErr::new::<PyRuntimeError, _>(format!("{:?}", e)))?;

    Ok(())
}

#[pymodule]
fn rust_test_runner_bindings(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(run_tests))?;
    Ok(())
}
