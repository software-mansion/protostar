use crate::common::runner::{corelib_path, runner};
use assert_fs::fixture::PathCopy;
use indoc::indoc;

#[test]
fn running_tests() {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("example_package", &["**/*"]).unwrap();

    let snapbox = runner();
    let corelib = corelib_path();

    snapbox
        .current_dir(&temp)
        .args(&["--corelib-path", corelib])
        .assert()
        .success()
        .stdout_matches(indoc! {r#"test_2::test_2::test_two: PASS []
            test_2::test_2::test_two_failing: FAIL [55114047758387]
            test_2::test_2::test_three: PASS []
            test_my_test::test_my_test::test_my_test: PASS []
            test_my_test::test_my_test::test_four: PASS []
            [..]::test_fib: PASS []
        "#});
}
