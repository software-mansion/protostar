use crate::helpers::constants::{ACCOUNT, ACCOUNT_FILE_PATH, NETWORK, URL};
use crate::helpers::runner::runner;

pub fn declare_simple_balance_contract() {
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

    runner(&args).assert().success();
}

pub fn deploy_simple_balance_contract() {
    let args = vec![
        "--url",
        URL,
        "--network",
        NETWORK,
        "--accounts-file",
        ACCOUNT_FILE_PATH,
        "--account",
        ACCOUNT,
        "deploy",
        "--class-hash",
        "0x8448a68b5ea1affc45e3fd4b8b480ea36a51dc34e337a16d2567d32d0c6f8a",
        "--salt",
        "0x1",
    ];

    runner(&args).assert().success();
}

pub fn common_cli_args() -> Vec<&'static str> {
    vec![
        "--url",
        URL,
        "--network",
        NETWORK,
        "--accounts-file",
        ACCOUNT_FILE_PATH,
        "--account",
        ACCOUNT,
    ]
}
