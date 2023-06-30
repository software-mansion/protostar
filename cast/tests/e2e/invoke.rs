use indoc::indoc;
use crate::helpers::constants::{ACCOUNT, ACCOUNT_FILE_PATH, NETWORK, URL};
use crate::helpers::runner::runner;


#[test]
fn test_happy_case() {
    let args = vec![
        "--url",
        URL,
        "--network",
        NETWORK,
        "--accounts-file",
        ACCOUNT_FILE_PATH,
        "--account",
        ACCOUNT,
        "invoke",
        "--contract-address",
        "some address",
        "--entry-point-name",
        "some function",
        "--calldata",
        "1 2 3 4",
    ];

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"abc"#});
}
