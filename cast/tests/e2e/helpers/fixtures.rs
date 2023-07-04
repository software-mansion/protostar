use crate::helpers::constants::{ACCOUNT, ACCOUNT_FILE_PATH, CONTRACTS_DIR, NETWORK, URL};
use camino::Utf8PathBuf;
use cast::{get_account, get_network, get_provider};
use starknet::accounts::{Account, SingleOwnerAccount};
use starknet::contract::ContractFactory;
use starknet::core::types::contract::{CompiledClass, SierraClass};
use starknet::core::types::FieldElement;
use starknet::providers::jsonrpc::HttpTransport;
use starknet::providers::JsonRpcClient;
use starknet::signers::LocalWallet;
use std::sync::Arc;

pub fn sierra_balance_path() -> String {
    CONTRACTS_DIR.to_string() + "/balance/target/dev/balance_HelloStarknet.sierra.json"
}

pub fn casm_balance_path() -> String {
    CONTRACTS_DIR.to_string() + "/balance/target/dev/balance_HelloStarknet.casm.json"
}

pub fn account(
    provider: &JsonRpcClient<HttpTransport>,
) -> SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet> {
    get_account(
        ACCOUNT,
        &Utf8PathBuf::from(ACCOUNT_FILE_PATH),
        provider,
        &get_network(NETWORK).unwrap(),
    )
    .unwrap()
}

pub async fn declare_simple_balance_contract() {
    let provider = get_provider(URL).unwrap();
    let account = account(&provider);

    let contract_definition: SierraClass = {
        let file_contents = std::fs::read(sierra_balance_path()).unwrap();
        serde_json::from_slice(&file_contents).unwrap()
    };
    let casm_contract_definition: CompiledClass = {
        let file_contents = std::fs::read(casm_balance_path()).unwrap();
        serde_json::from_slice(&file_contents).unwrap()
    };

    let casm_class_hash = casm_contract_definition.class_hash().unwrap();

    let declaration = account.declare(
        Arc::new(contract_definition.flatten().unwrap()),
        casm_class_hash,
    );
    declaration.send().await.ok();
}

pub async fn deploy_simple_balance_contract() {
    let provider = get_provider(URL).unwrap();
    let account = account(&provider);

    let factory = ContractFactory::new(
        FieldElement::from_hex_be(
            "0x8448a68b5ea1affc45e3fd4b8b480ea36a51dc34e337a16d2567d32d0c6f8a",
        )
        .unwrap(),
        account,
    );
    let deployment = factory.deploy(Vec::new(), FieldElement::from_hex_be("0x1").unwrap(), false);
    deployment.send().await.ok();
}

pub fn default_cli_args() -> Vec<&'static str> {
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
