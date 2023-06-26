use anyhow::{anyhow, Context, Result};
use camino::Utf8PathBuf;
use cast::{handle_rpc_error, wait_for_tx};
use clap::Args;
use starknet::accounts::ConnectedAccount;
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
use starknet::accounts::AccountError::Provider;
use starknet::providers::jsonrpc::JsonRpcClientError::RpcError;
use starknet::providers::jsonrpc::RpcError::{Code, Unknown};
use starknet::providers::ProviderError::{Other, StarknetError};

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
) -> Result<()> {
    let contract_definition: SierraClass = {
        let file_contents = std::fs::read(sierra_contract_path)
            .with_context(|| format!("Failed to read contract file: {sierra_contract_path}"))?;
        serde_json::from_slice(&file_contents).with_context(|| {
            format!("Failed to parse contract definition: {sierra_contract_path}")
        })?
    };
    let casm_contract_definition: CompiledClass = {
        let file_contents = std::fs::read(casm_contract_path)
            .with_context(|| format!("Failed to read contract file: {casm_contract_path}"))?;
        serde_json::from_slice(&file_contents)
            .with_context(|| format!("Failed to parse contract definition: {casm_contract_path}"))?
    };

    let casm_class_hash = casm_contract_definition.class_hash()?;

    let declaration = account.declare(Arc::new(contract_definition.flatten()?), casm_class_hash);
    let declared = declaration.send().await;
    match declared {
        Ok(declared) => {
            let message = wait_for_tx(account.provider(), declared.transaction_hash).await?;
            Ok(())
        },
        Err(error) => {
            match error {
                Provider(Other(RpcError(Code(error))) | StarknetError(error)) => {
                    handle_rpc_error(error);
                    Err(anyhow!("Err"))
                },
                Provider(Other(RpcError(Unknown(error)))) => {
                    Err(anyhow!(error.message))
                }
                _ => Ok(())
            }
        }
    }
}
