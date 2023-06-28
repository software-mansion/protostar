use anyhow::{anyhow, Context, Error, Result};
use camino::Utf8PathBuf;
use serde::{Deserialize, Serialize};
use starknet::core::types::BlockTag::{Latest, Pending};
use starknet::core::types::MaybePendingTransactionReceipt::{PendingReceipt, Receipt};
use starknet::core::types::TransactionReceipt::{
    Declare, Deploy, DeployAccount, Invoke, L1Handler,
};
use starknet::core::types::{BlockId, StarknetError, TransactionStatus};
use starknet::providers::jsonrpc::JsonRpcClientError;
use starknet::providers::jsonrpc::JsonRpcClientError::RpcError;
use starknet::providers::jsonrpc::RpcError::{Code, Unknown};
use starknet::providers::ProviderError::{Other, StarknetError as ProviderStarknetError};
use starknet::providers::{Provider, ProviderError};
use starknet::{
    accounts::SingleOwnerAccount,
    core::{chain_id, types::FieldElement},
    providers::jsonrpc::{HttpTransport, JsonRpcClient},
    signers::{LocalWallet, SigningKey},
};
use std::collections::HashMap;
use std::fs;
use std::thread::sleep;
use std::time::Duration;
use url::Url;

pub const UDC_ADDRESS: &str = "0x041a78e741e5af2fec34b695679bc6891742439f7afb8484ecd7766661ad02bf";

#[derive(Deserialize, Serialize, Clone)]
struct Account {
    private_key: String,
    public_key: String,
    address: String,
    salt: Option<String>,
    deployed: Option<bool>,
}

pub enum Network {
    Testnet,
    Testnet2,
    Mainnet,
}

impl Network {
    #[must_use]
    pub fn get_chain_id(&self) -> FieldElement {
        match self {
            Network::Testnet => chain_id::TESTNET,
            Network::Testnet2 => chain_id::TESTNET2,
            Network::Mainnet => chain_id::MAINNET,
        }
    }
    #[must_use]
    pub fn get_value(&self) -> &'static str {
        match self {
            Network::Testnet => "alpha-goerli",
            Network::Testnet2 => "alpha-goerli2",
            Network::Mainnet => "alpha-mainnet,",
        }
    }
}

pub fn get_provider(url: &str) -> Result<JsonRpcClient<HttpTransport>> {
    let parsed_url = Url::parse(url)?;
    let provider = JsonRpcClient::new(HttpTransport::new(parsed_url));
    Ok(provider)
}

fn get_account_info(name: &str, chain_id: &str, path: &Utf8PathBuf) -> Result<Account> {
    let accounts: HashMap<String, HashMap<String, Account>> =
        serde_json::from_str(&fs::read_to_string(path)?)?;
    let user = accounts
        .get(chain_id)
        .and_then(|accounts_map| accounts_map.get(name))
        .cloned();

    user.ok_or_else(|| anyhow!("Account {} not found under chain id {}", name, chain_id))
}

pub fn get_account<'a>(
    name: &str,
    accounts_file_path: &Utf8PathBuf,
    provider: &'a JsonRpcClient<HttpTransport>,
    network: &Network,
) -> Result<SingleOwnerAccount<&'a JsonRpcClient<HttpTransport>, LocalWallet>> {
    // todo: #2113 verify network with provider
    let account_info = get_account_info(name, network.get_value(), accounts_file_path)?;
    let signer = LocalWallet::from(SigningKey::from_secret_scalar(
        FieldElement::from_hex_be(&account_info.private_key).with_context(|| {
            format!(
                "Failed to convert private key {} to FieldElement",
                &account_info.private_key
            )
        })?,
    ));
    let address = FieldElement::from_hex_be(&account_info.address).with_context(|| {
        format!(
            "Failed to convert account address {} to FieldElement",
            &account_info.private_key
        )
    })?;
    let mut account = SingleOwnerAccount::new(provider, signer, address, network.get_chain_id());

    Ok(account)
}

pub fn get_block_id(value: &str) -> Result<BlockId> {
    // todo: add more block ids (hash, number)
    match value {
        "pending" => Ok(BlockId::Tag(Pending)),
        "latest" => Ok(BlockId::Tag(Latest)),
        _ if value.starts_with("0x") => Ok(BlockId::Hash(FieldElement::from_hex_be(value)?)),
        _ => match value.parse::<u64>() {
            Ok(value) => Ok(BlockId::Number(value)),
            Err(_) => Err(anyhow::anyhow!(
                "No such block id {}! Possible values are pending, latest, block hash (hex) and block number (u64).",
                value
            )),
        },
    }
}

pub fn get_network(name: &str) -> Result<Network> {
    match name {
        "testnet" => Ok(Network::Testnet),
        "testnet2" => Ok(Network::Testnet2),
        "mainnet" => Ok(Network::Mainnet),
        _ => Err(anyhow::anyhow!(
            "No such network {}! Possible values are testnet, testnet2, mainnet.",
            name
        )),
    }
}

pub async fn wait_for_tx(
    provider: &JsonRpcClient<HttpTransport>,
    tx_hash: FieldElement,
) -> Result<&str> {
    'a: while {
        let receipt = provider
            .get_transaction_receipt(tx_hash)
            .await
            .expect("Could not get transaction with hash: {tx_hash:#x}");

        let status = if let Receipt(receipt) = receipt {
            match receipt {
                Invoke(receipt) => receipt.status,
                Declare(receipt) => receipt.status,
                Deploy(receipt) => receipt.status,
                DeployAccount(receipt) => receipt.status,
                L1Handler(receipt) => receipt.status,
            }
        } else {
            continue 'a;
        };

        match status {
            TransactionStatus::Pending => {
                sleep(Duration::from_secs(5));
                true
            }
            TransactionStatus::AcceptedOnL2 | TransactionStatus::AcceptedOnL1 => {
                return Ok("Transaction accepted")
            }
            TransactionStatus::Rejected => {
                return Err(anyhow!("Transaction has been rejected"));
            }
        }
    } {}

    Err(anyhow!("Unexpected error happened"))
}

#[must_use]
pub fn get_rpc_error_message(error: StarknetError) -> &'static str {
    match error {
        StarknetError::FailedToReceiveTransaction => "Node failed to receive transaction",
        StarknetError::ContractNotFound => "There is no contract at the specified address",
        StarknetError::BlockNotFound => "Block was not found",
        StarknetError::TransactionHashNotFound => {
            "Transaction with provided hash was not found (does not exist)"
        }
        StarknetError::InvalidTransactionIndex => "There is no transaction with such an index",
        StarknetError::ClassHashNotFound => "Provided class hash does not exist",
        StarknetError::ContractError => "An error occurred in the called contract",
        StarknetError::InvalidContractClass => "Contract class is invalid",
        StarknetError::ClassAlreadyDeclared => {
            "Contract with the same class hash is already declared"
        }
        _ => "Unknown RPC error",
    }
}

pub fn handle_rpc_error<T, G>(
    error: ProviderError<JsonRpcClientError<T>>,
) -> std::result::Result<G, Error> {
    match error {
        Other(RpcError(Code(error))) | ProviderStarknetError(error) => {
            Err(anyhow!(get_rpc_error_message(error)))
        }
        Other(RpcError(Unknown(error))) => Err(anyhow!(error.message)),
        _ => Err(anyhow!("Unknown RPC error")),
    }
}
