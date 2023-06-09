use anyhow::Error;
use cairo_felt::Felt252;
use camino::Utf8PathBuf;
use console::style;

use cairo_lang_runner::RunResultValue;

use crate::test_stats::TestsStats;

pub fn print_error_message(error: &Error) {
    let error_tag = style("ERROR").red();
    println!("[{error_tag}] {error}");
}

pub fn print_collected_tests_count(tests_num: usize, tests_files_num: usize) {
    let plain_text = format!("Collected {tests_num} test(s) and {tests_files_num} test file(s)");
    println!("{}", style(plain_text).bold());
}

pub fn print_running_tests(test_file: &Utf8PathBuf, tests_num: usize) {
    let plain_text = format!("Running {tests_num} test(s) from {test_file}");
    println!("{}", style(plain_text).bold());
}

pub fn print_test_summary(tests_stats: TestsStats) {
    println!(
        "{}: {} passed, {} failed ",
        style("Tests").bold(),
        tests_stats.passed,
        tests_stats.failed
    );
}

pub fn print_test_result(test_name: &str, result_value: &RunResultValue) {
    let result_str = get_result_str(result_value);

    let passed = did_pass(result_value);
    let result_tag = if passed {
        style("PASS").green()
    } else {
        style("FAIL").red()
    };

    let result_str_bold = style(result_str).bold();

    println!("[{result_tag}] {test_name} {result_str_bold}");
}

fn get_result_str(run_result: &RunResultValue) -> String {
    match run_result {
        RunResultValue::Panic(result_data) | RunResultValue::Success(result_data) => {
            result_data_to_text(result_data)
        }
    }
}

fn did_pass(run_result: &RunResultValue) -> bool {
    match run_result {
        RunResultValue::Success(_) => true,
        RunResultValue::Panic(_) => false,
    }
}

fn result_data_to_text(data: &[Felt252]) -> String {
    let mut readable_text = String::new();

    for felt in data {
        let felt_bytes = felt.to_bytes_be();
        let felt_text = String::from_utf8_lossy(&felt_bytes);
        readable_text.push_str(&felt_text);
    }

    readable_text
}
