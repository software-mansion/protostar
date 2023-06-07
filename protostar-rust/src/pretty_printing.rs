use anyhow::Error;
use camino::Utf8Path;
use console::set_colors_enabled;
use console::style;

use super::TestsStats;

pub fn enable_colors() {
    set_colors_enabled(true);
}

pub fn print_error_message(error: Error) {
    println!("[{}] {}", style("ERROR").red(), error);
}

pub fn print_collected_tests(tests_num: usize, tests_files_num: usize) {
    let plain_text = format!(
        "Collected {} test(s) and {} test file(s)",
        tests_num, tests_files_num
    );
    println!("{}", style(plain_text).bold());
}

pub fn print_running_tests(test_file: &Utf8Path, tests_num: usize) {
    let plain_text = format!("Running {} test(s) from {:?}", tests_num, test_file);
    println!("{}", style(plain_text).bold());
}

pub fn print_test_result(test_name: &str, result_str: &str, passed: bool) {
    let result_tag = if passed {
        style("PASS").green()
    } else {
        style("FAIL").red()
    };
    println!(
        "[{}] {} {}",
        result_tag,
        test_name,
        style(result_str).bold()
    );
}

pub fn print_test_summary(tests_stats: TestsStats) {
    println!(
        "{}: {} passed, {} failed ",
        style("Tests").bold(),
        tests_stats.passed,
        tests_stats.failed
    );
}
