use indoc::indoc;

use crate::helpers::constants::{NETWORK, URL};
use crate::helpers::runner::runner;

const ACCOUNT: &str = "user1";
const ACCOUNT_FILE_PATH: &str = "tests/data/accounts/accounts.json";

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
        "declare",
        "-s",
        "tests/data/declare/contract.json",
        "-c",
        "tests/data/declare/contract.casm",
    ];

    let snapbox = runner(&args);

    snapbox.assert().success().stdout_matches(
        indoc! {r#"Class hash: 0x8448a68b5ea1affc45e3fd4b8b480ea36a51dc34e337a16d2567d32d0c6f8a
        Transaction hash: 0x16a2cef32f09a77beb1af5fda87e7c83eb246202d9203c023f93c6d070045c8
        "#},
    );
}

// happy case with max fee
// max fee too low
// not sierra in file
// not casm in file
// already declared
// scarbowe errory, brak ścieżek itd
// spojrz na pra marcina i dodaj coś jeszcze z errorow


