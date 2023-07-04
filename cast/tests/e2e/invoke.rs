use crate::helpers::fixtures::{
    declare_simple_balance_contract, default_cli_args, deploy_simple_balance_contract,
};
use crate::helpers::runner::runner;
use indoc::indoc;

#[tokio::test]
async fn test_happy_case() {
    declare_simple_balance_contract().await;
    deploy_simple_balance_contract().await;

    let mut args = default_cli_args();
    args.append(&mut vec![
        "--int-format",
        "--json",
        "invoke",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--entry-point-name",
        "increase_balance",
        "--calldata",
        "0x1ab93",
        "--max-fee",
        "999999999999",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stdout_eq(indoc! {r#"
{
  "command": "Invoke",
  "transaction_hash": "441760207739321214581433241542253705558196427645618141494280065272904928835"
}
"#});
}

#[tokio::test]
async fn test_contract_does_not_exist() {
    declare_simple_balance_contract().await;
    deploy_simple_balance_contract().await;

    let mut args = default_cli_args();
    args.append(&mut vec![
        "invoke",
        "--contract-address",
        "0x1",
        "--entry-point-name",
        "increase_balance",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: There is no contract at the specified address
    "#});
}

#[tokio::test]
async fn test_wrong_function_name() {
    declare_simple_balance_contract().await;
    deploy_simple_balance_contract().await;

    let mut args = default_cli_args();
    args.append(&mut vec![
        "invoke",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--entry-point-name",
        "balance",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: An error occurred in the called contract
    "#});
}

#[tokio::test]
async fn test_wrong_calldata() {
    declare_simple_balance_contract().await;
    deploy_simple_balance_contract().await;

    let mut args = default_cli_args();
    args.append(&mut vec![
        "invoke",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--entry-point-name",
        "increase_balance",
        "--calldata",
        "0x1ab93 0x1",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: Error at pc=0:81:
        Got an exception while executing a hint.
        Cairo traceback (most recent call last):
        Unknown location (pc=0:731)
        Unknown location (pc=0:677)
        Unknown location (pc=0:291)
        Unknown location (pc=0:314)

        Error in the called contract (0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68):
        Execution was reverted; failure reason: [0x496e70757420746f6f206c6f6e6720666f7220617267756d656e7473].
    "#});
}

#[tokio::test]
async fn test_too_low_max_fee() {
    declare_simple_balance_contract().await;
    deploy_simple_balance_contract().await;

    let mut args = default_cli_args();
    args.append(&mut vec![
        "invoke",
        "--contract-address",
        "0x2bd89651521ec94a7c497c53f6b4555eeecef8b2221350dc5a04aa14ba41d68",
        "--entry-point-name",
        "increase_balance",
        "--calldata",
        "0x1ab93",
        "--max-fee",
        "1",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: Transaction has been rejected
    "#});
}
