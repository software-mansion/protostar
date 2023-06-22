use anyhow::{Error, Result};
use camino::Utf8PathBuf;
use clap::Args;
use starknet::core::types::DeclareTransactionResult;
use starknet::{
    accounts::{Account, SingleOwnerAccount},
    core::types::contract::{CompiledClass, SierraClass},
    providers::jsonrpc::{HttpTransport, JsonRpcClient},
    signers::LocalWallet,
};
use std::sync::Arc;

#[derive(Args)]
#[command(about = "Declare a contract to starknet", long_about = None)]
pub struct Declare {
    /// Path to the sierra compiled contract
    #[clap(short = 's', long = "sierra-contract-path")]
    pub sierra_contract_path: Utf8PathBuf,

    /// Path to the casm compiled contract
    #[clap(short = 'c', long = "casm-contract-path")]
    pub casm_contract_path: Utf8PathBuf,
}

pub async fn declare(
    sierra_contract_path: &Utf8PathBuf,
    casm_contract_path: &Utf8PathBuf,
    account: &mut SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet>,
) -> Result<DeclareTransactionResult, Error> {
    let contract_definition: SierraClass = {
        let file_contents = std::fs::read(sierra_contract_path)
            .map_err(|err| anyhow::anyhow!("Failed to read contract file: {}", err))?;
        serde_json::from_slice(&file_contents)
            .map_err(|err| anyhow::anyhow!("Failed to parse contract definition: {}", err))?
    };
    let casm_contract_definition: CompiledClass = {
        let file_contents = std::fs::read(casm_contract_path)
            .map_err(|err| anyhow::anyhow!("Failed to read contract file: {}", err))?;
        serde_json::from_slice(&file_contents)
            .map_err(|err| anyhow::anyhow!("Failed to parse contract definition: {}", err))?
    };

    let casm_class_hash = casm_contract_definition.class_hash()?;

    let declaration = account.declare(Arc::new(contract_definition.flatten()?), casm_class_hash);
    let declared = declaration.send().await?;

    Ok(declared)
}
