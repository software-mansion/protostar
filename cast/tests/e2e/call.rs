use indoc::indoc;
use crate::helpers::fixtures::default_cli_args;
use crate::helpers::runner::runner;

#[tokio::test]
async fn test_happy_case() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "--json",
        "call",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--function-name",
        "get_balance",
        "--block-id",
        "latest",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stdout_eq(indoc! {r#"
{
  "command": "Call",
  "response": "[FieldElement { inner: 0x0000000000000000000000000000000000000000000000000000000000000000 }]"
}
"#});
}

#[tokio::test]
async fn test_contract_does_not_exist() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "call",
        "--contract-address",
        "0x1",
        "--function-name",
        "get_balance",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: There is no contract at the specified address
    "#});
}

#[tokio::test]
async fn test_wrong_function_name() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "call",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--function-name",
        "balance",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: An error occurred in the called contract
    "#});
}

#[tokio::test]
async fn test_wrong_calldata() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "call",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--function-name",
        "get_balance",
        "--calldata",
        "0x1",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: Execution was reverted; failure reason: [0x496e70757420746f6f206c6f6e6720666f7220617267756d656e7473].
    "#});
}
