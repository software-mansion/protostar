use crate::common::runner::runner;
use assert_fs::fixture::PathCopy;
use indoc::indoc;

#[test]
fn run_simple_test() {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("tests/data/simple_test", &["**/*"]).unwrap();

    let snapbox = runner();

    snapbox
        .current_dir(&temp)
        .assert()
        .success()
        .stdout_matches(indoc! {r#"Collected 6 test(s) and 3 test file(s)
            Running 1 test(s) from src/lib.cairo
            [PASS] [..]::test_fib
            Running 2 test(s) from tests/ext_function_test.cairo
            [PASS] ext_function_test::ext_function_test::test_my_test
            [PASS] ext_function_test::ext_function_test::test_simple
            Running 3 test(s) from tests/test_simple.cairo
            [PASS] test_simple::test_simple::test_simple
            [PASS] test_simple::test_simple::test_simple2
            [FAIL] test_simple::test_simple::test_failing failing check
            Tests: 5 passed, 1 failed
        "#});
}

#[test]
fn run_declare_test() {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("tests/data/declare_test", &["**/*"])
        .unwrap();

    let snapbox = runner();

    snapbox
        .current_dir(&temp)
        .assert()
        .success()
        .stdout_matches(indoc! {r#"Collected 1 test(s) and 2 test file(s)
            Running 0 test(s) from src/lib.cairo
            Running 1 test(s) from tests/test_declare.cairo
            [PASS] test_declare::test_declare::test_declare_simple
            Tests: 1 passed, 0 failed
        "#});
}
