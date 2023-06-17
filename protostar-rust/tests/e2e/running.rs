use assert_fs::fixture::PathCopy;
use indoc::indoc;

use crate::common::runner::runner;

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
            [FAIL] test_simple::test_simple::test_failing
            original value: [8111420071579136082810415440747], converted to a string: [failing check]
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

#[test]
fn run_print_test() {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("tests/data/print_test", &["**/*"]).unwrap();

    let snapbox = runner();

    snapbox
        .current_dir(&temp)
        .assert()
        .success()
        .stdout_matches(indoc! {r#"Collected 1 test(s) and 2 test file(s)
            Running 0 test(s) from src/lib.cairo
            Running 1 test(s) from tests/test_print.cairo
            original value: [123], converted to a string: [{]
            original value: [6381921], converted to a string: [aaa]
            original value: [3618502788666131213697322783095070105623107215331596699973092056135872020480]
            original value: [152]
            original value: [124], converted to a string: [|]
            original value: [149]
            original value: [439721161573], converted to a string: [false]
            [PASS] test_print::test_print::test_print
            Tests: 1 passed, 0 failed
        "#});
}

#[test]
fn run_panic_decoding_test() {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("tests/data/panic_decoding_test", &["**/*"])
        .unwrap();

    let snapbox = runner();

    snapbox
        .current_dir(&temp)
        .assert()
        .success()
        .stdout_matches(indoc! {r#"Collected 1 test(s) and 2 test file(s)
            Running 0 test(s) from src/lib.cairo
            Running 1 test(s) from tests/test_panic_decoding.cairo
            [FAIL] test_panic_decoding::test_panic_decoding::test_panic_decoding
            original value: [123], converted to a string: [{]
            original value: [6381921], converted to a string: [aaa]
            original value: [3618502788666131213697322783095070105623107215331596699973092056135872020480]
            original value: [152]
            original value: [124], converted to a string: [|]
            original value: [149]
            Tests: 0 passed, 1 failed
        "#});
}
