use anyhow::{Error, Result};
use starknet::{
    accounts::{Account, SingleOwnerAccount},
    core::types::contract::{CompiledClass, SierraClass},
    providers::jsonrpc::{HttpTransport, JsonRpcClient},
    signers::LocalWallet,
};
use std::sync::Arc;

pub async fn declare(
    sierra_contract_path: &str,
    casm_contract_path: &str,
    account: &mut SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet>,
) -> Result<(), Error> {
    let contract_definition: SierraClass =
        serde_json::from_reader(std::fs::File::open(sierra_contract_path).unwrap()).unwrap();
    let casm_contract_definition: CompiledClass =
        serde_json::from_reader(std::fs::File::open(casm_contract_path).unwrap()).unwrap();

    let class_hash = contract_definition.class_hash()?;
    let casm_class_hash = casm_contract_definition.class_hash()?;

    let declaration = account.declare(Arc::new(contract_definition.flatten()?), casm_class_hash);
    let declared = declaration.send().await?;

    // dbg!(declaration);
    // dbg!(declared);
    Ok(())
}
