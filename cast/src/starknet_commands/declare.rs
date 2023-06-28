use anyhow::{Context, Result};
use cast::wait_for_tx;
use clap::Args;
use starknet::accounts::ConnectedAccount;
use starknet::core::types::FieldElement;
use starknet::{
    accounts::{Account, SingleOwnerAccount},
    core::types::{
        contract::{CompiledClass, SierraClass},
        DeclareTransactionResult,
    },
    providers::jsonrpc::{HttpTransport, JsonRpcClient},
    signers::LocalWallet,
};
use std::sync::Arc;
use std::process::Command;

#[derive(Args)]
#[command(about = "Declare a contract to starknet", long_about = None)]
pub struct Declare {
    /// contract name
    pub contract: String,

    /// Max fee for the transaction. If not provided, max fee will be automatically estimated
    #[clap(short, long)]
    pub max_fee: Option<u128>,
}

pub async fn declare(
    contract: &str,
    max_fee: Option<u128>,
    account: &mut SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet>,
) -> Result<DeclareTransactionResult> {
    let command_result = Command::new("scarb")
        .current_dir(std::env::current_dir().expect("Failed to obtain current dir"))
        .arg("build")
        .output()
        .expect("Failed to start building contracts with Scarb");
    let result_code = command_result.status.code().expect("failed to obtain status code from scarb build");
    if result_code != 0 {
        panic!("scarb build returned non-zero exit code: {}", result_code);
    }

    let current_dir = std::env::current_dir().expect("Failed to obtain current dir");
    let paths = std::fs::read_dir(format!("{}/target/dev", current_dir.to_str().unwrap()))
        .expect("Failed to read the file that should have been built with scarb");

    let mut maybe_sierra_contract_path: Option<String> = None;
    let mut maybe_casm_contract_path: Option<String> = None;
    for path in paths {
        let path_str = path
            .expect("Path not resolved properly")
            .path()
            .to_str()
            .expect("Failed to convert path to string")
            .to_string();
        if path_str.contains(&contract[..]) {
            if path_str.contains(".sierra.json") {
                maybe_sierra_contract_path = Some(path_str);
            } else if path_str.contains(".casm.json") {
                maybe_casm_contract_path = Some(path_str);
            }
        }
    }

    let sierra_contract_path = maybe_sierra_contract_path.expect(&format!("No sierra found for contract: {}", contract)[..]);
    let casm_contract_path = maybe_casm_contract_path.expect(&format!("No casm found for contract: {}", contract)[..]);

    let contract_definition: SierraClass = {
        let file_contents = std::fs::read(sierra_contract_path.clone())
            .with_context(|| format!("Failed to read contract file: {sierra_contract_path}"))?;
        serde_json::from_slice(&file_contents).with_context(|| {
            format!("Failed to parse contract definition: {sierra_contract_path}")
        })?
    };
    let casm_contract_definition: CompiledClass = {
        let file_contents = std::fs::read(casm_contract_path.clone())
            .with_context(|| format!("Failed to read contract file: {casm_contract_path}"))?;
        serde_json::from_slice(&file_contents)
            .with_context(|| format!("Failed to parse contract definition: {casm_contract_path}"))?
    };

    let casm_class_hash = casm_contract_definition.class_hash()?;

    let declaration = account.declare(Arc::new(contract_definition.flatten()?), casm_class_hash);
    let execution = if let Some(max_fee) = max_fee {
        declaration.max_fee(FieldElement::from(max_fee))
    } else {
        declaration
    };

    let declared = execution.send().await?;

    wait_for_tx(account.provider(), declared.transaction_hash).await;

    Ok(declared)
}
