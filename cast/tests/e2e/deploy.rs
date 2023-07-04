use crate::helpers::constants::MAP_CLASS_HASH;
use crate::helpers::fixtures::default_cli_args;
use crate::helpers::runner::runner;
use indoc::indoc;

#[tokio::test]
async fn test_happy_case() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "--int-format",
        "--json",
        "deploy",
        "--class-hash",
        MAP_CLASS_HASH,
        "--salt",
        "0x2",
        "--unique",
        "--max-fee",
        "999999999999",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stdout_eq(indoc! {r#"
{
  "command": "Deploy",
  "contract_address": "3136215836708901795618334565051954066277512294057960177787473886680603169588",
  "transaction_hash": "3264120505042658743939221190313555798158132320315351505088247563355415619141"
}
"#});
}

#[tokio::test]
async fn test_contract_not_declared() {
    let mut args = default_cli_args();
    args.append(&mut vec!["deploy", "--class-hash", "0x1"]);

    let snapbox = runner(&args);
    let output = String::from_utf8(snapbox.assert().success().get_output().stderr.clone()).unwrap();

    assert!(output.contains("Class with hash 0x1 is not declared."));
}

#[tokio::test]
async fn test_contract_already_deployed() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "deploy",
        "--class-hash",
        MAP_CLASS_HASH,
        "--salt",
        "0x100",
        "--max-fee",
        "999999999999",
    ]);

    let snapbox = runner(&args);
    snapbox.assert().success();

    let snapbox2 = runner(&args);
    snapbox2.assert().success().stderr_matches(indoc! {r#"
{
  "command": "Deploy",
  "contract_address": "3136215836708901795618334565051954066277512294057960177787473886680603169588",
  "transaction_hash": "3264120505042658743939221190313555798158132320315351505088247563355415619141"
}
"#});
    // let output = String::from_utf8(snapbox.assert().success().get_output().stderr.clone()).unwrap();
    //
    // println!("{output}");
    //
    // assert!(output.contains("'code': <StarknetErrorCode.CONTRACT_ADDRESS_UNAVAILABLE: 4>"));
}

#[tokio::test]
async fn test_too_low_max_fee() {
    let mut args = default_cli_args();
    args.append(&mut vec![
        "deploy",
        "--class-hash",
        MAP_CLASS_HASH,
        "--salt",
        "0x2",
        "--unique",
        "--max-fee",
        "1",
    ]);

    let snapbox = runner(&args);

    snapbox.assert().success().stderr_matches(indoc! {r#"
        error: Transaction has been rejected
    "#});
}
