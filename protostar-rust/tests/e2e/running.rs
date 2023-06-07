use crate::common::runner::{corelib_path, runner};
use assert_fs::fixture::PathCopy;
use indoc::indoc;

#[test]
fn running_tests() {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("tests/data/example_package", &["**/*"])
        .unwrap();

    let snapbox = runner();
    let corelib = corelib_path();

    snapbox
        .current_dir(&temp)
        .args(["--corelib-path", corelib])
        .assert()
        .success()
        .stdout_matches(indoc! {r#"Collected 6 test(s) and 3 test file(s)
            Running 3 test(s) from tests/test_2.cairo
            [PASS] test_2::test_2::test_two
            [FAIL] test_2::test_2::test_two_failing 2 == 3
            [PASS] test_2::test_2::test_three
            Running 2 test(s) from tests/test_my_test.cairo
            [PASS] test_my_test::test_my_test::test_my_test
            [PASS] test_my_test::test_my_test::test_four
            Running 1 test(s) from src/lib.cairo
            [PASS] [..]::test_fib
            Tests: 5 passed, 1 failed
        "#});
}
