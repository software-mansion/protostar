use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::exceptions::RuntimeError;

use anyhow::Context;
use std::collections::HashMap;

use cairo_lang_protostar::test_collector::collect_tests;
use cairo_lang_runner::{SierraCasmRunner, RunResultValue};

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

fn internal_run_tests(input_path: &str) -> anyhow::Result<Vec<(String, String)>> {
  let (sierra_program, test_configs) = collect_tests(&input_path.to_owned(), None, None, None)?;

  let runner = SierraCasmRunner::new(
    sierra_program,
    None,
    HashMap::new(),
  )
  .with_context(|| "Failed setting up runner.")?;

  let mut results = vec![];
  for config in &test_configs {
    let result = runner
    .run_function(
        runner.find_function(&config.name.as_str())?,
        &[],
        config.available_gas,
        Default::default(),
    )
    .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;
    results.push((config.name.clone(), run_result_value_to_string(result.value)));
  }
  Ok(results)
}

#[pyfunction]
fn run_tests(input_path: String) -> PyResult<Vec<(String, String)>> {
    let results = internal_run_tests(&input_path.to_owned()).map_err(|e| PyErr::new::<RuntimeError, _>(format!("{:?}", e)))?;

    Ok(results)
}

#[pymodule]
fn rust_test_runner_bindings(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(run_tests))?;
    Ok(())
}
