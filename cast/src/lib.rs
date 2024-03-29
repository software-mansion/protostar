use anyhow::{anyhow, Context, Error, Result};
use camino::Utf8PathBuf;
use primitive_types::U256;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use starknet::core::types::{
    BlockId,
    BlockTag::{Latest, Pending},
    FieldElement,
    MaybePendingTransactionReceipt::Receipt,
    StarknetError,
    TransactionReceipt::{Declare, Deploy, DeployAccount, Invoke, L1Handler},
    TransactionStatus,
};
use starknet::providers::jsonrpc::JsonRpcClientError;
use starknet::providers::jsonrpc::JsonRpcClientError::RpcError;
use starknet::providers::jsonrpc::RpcError::{Code, Unknown};
use starknet::providers::ProviderError::{Other, StarknetError as ProviderStarknetError};
use starknet::{
    accounts::SingleOwnerAccount,
    core::chain_id,
    providers::{
        jsonrpc::{HttpTransport, JsonRpcClient},
        Provider, ProviderError,
    },
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

#[derive(Debug, PartialEq)]
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
                "Failed to convert private key: {} to FieldElement",
                &account_info.private_key
            )
        })?,
    ));
    let address = FieldElement::from_hex_be(&account_info.address).with_context(|| {
        format!(
            "Failed to convert account address: {} to FieldElement",
            &account_info.address
        )
    })?;
    let account = SingleOwnerAccount::new(provider, signer, address, network.get_chain_id());

    Ok(account)
}

pub fn get_block_id(value: &str) -> Result<BlockId> {
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

// todo: #2142 add tests
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

pub async fn handle_wait_for_tx_result<T>(
    provider: &JsonRpcClient<HttpTransport>,
    transaction_hash: FieldElement,
    return_value: T,
) -> Result<T> {
    match wait_for_tx(provider, transaction_hash).await {
        Ok(_) => Ok(return_value),
        Err(message) => Err(anyhow!(message)),
    }
}

pub fn print_formatted(
    mut output: Vec<(&str, String)>,
    int_format: bool,
    json: bool,
    error: bool,
) -> Result<()> {
    if !int_format {
        output = output
            .into_iter()
            .map(|(key, value)| {
                if let Ok(int_value) = U256::from_dec_str(&value) {
                    (key, format!("{int_value:#x}"))
                } else {
                    (key, value)
                }
            })
            .collect();
    }

    if json {
        let json_output: HashMap<&str, String> = output.into_iter().collect();
        let json_value: Value = serde_json::to_value(json_output)?;

        write_to_output(serde_json::to_string_pretty(&json_value)?, error);
    } else {
        for (key, value) in &output {
            write_to_output(format!("{key}: {value}"), error);
        }
    }

    Ok(())
}

fn write_to_output<T: std::fmt::Display>(value: T, error: bool) {
    if error {
        eprintln!("{value}");
    } else {
        println!("{value}");
    }
}

pub fn parse_number(number_as_str: &str) -> Result<FieldElement> {
    let contract_address = match &number_as_str[..2] {
        "0x" => FieldElement::from_hex_be(number_as_str)?,
        _ => FieldElement::from_dec_str(number_as_str)?,
    };
    Ok(contract_address)
}

#[cfg(test)]
mod tests {
    use crate::{get_account, get_block_id, get_network, get_provider, Network};
    use camino::Utf8PathBuf;
    use starknet::core::types::{
        BlockId,
        BlockTag::{Latest, Pending},
        FieldElement,
    };
    use std::fs;
    use url::ParseError;

    #[test]
    fn test_get_provider() {
        let provider = get_provider("http://127.0.0.1:5050/rpc");
        assert!(provider.is_ok());
    }

    #[test]
    fn test_get_provider_invalid_url() {
        let provider = get_provider("");
        let err = provider.unwrap_err();
        assert!(err.is::<ParseError>());
    }

    #[test]
    fn test_get_account() {
        let provider = get_provider("http://127.0.0.1:5050/rpc").unwrap();
        let account = get_account(
            "user1",
            &Utf8PathBuf::from("tests/data/accounts/accounts.json"),
            &provider,
            &Network::Testnet,
        );

        assert!(account.is_ok());

        let expected = fs::read_to_string("tests/data/accounts/user1_representation")
            .expect("Failed to read expected debug representation");
        let returned = format!("{:?}", account.unwrap());
        assert_eq!(returned.trim(), expected.trim());
    }

    #[test]
    fn test_get_account_no_file() {
        let provider = get_provider("http://127.0.0.1:5050/rpc").unwrap();
        let account = get_account(
            "user1",
            &Utf8PathBuf::from("tests/data/accounts/nonexistentfile.json"),
            &provider,
            &Network::Testnet,
        );
        let err = account.unwrap_err();
        assert!(err.to_string().contains("No such file or directory"));
    }

    #[test]
    fn test_get_account_invalid_file() {
        let provider = get_provider("http://127.0.0.1:5050/rpc").unwrap();
        let account = get_account(
            "user1",
            &Utf8PathBuf::from("tests/data/accounts/invalid_format.json"),
            &provider,
            &Network::Testnet,
        );
        let err = account.unwrap_err();
        assert!(err.is::<serde_json::Error>());
    }

    #[test]
    fn test_get_account_no_network() {
        let provider = get_provider("http://127.0.0.1:5050/rpc").unwrap();
        let account = get_account(
            "user1",
            &Utf8PathBuf::from("tests/data/accounts/accounts.json"),
            &provider,
            &Network::Mainnet,
        );
        let err = account.unwrap_err();
        assert!(err
            .to_string()
            .contains("Account user1 not found under chain id alpha-mainnet"));
    }

    #[test]
    fn test_get_account_no_user_for_network() {
        let provider = get_provider("http://127.0.0.1:5050/rpc").unwrap();
        let account = get_account(
            "user10",
            &Utf8PathBuf::from("tests/data/accounts/accounts.json"),
            &provider,
            &Network::Testnet,
        );
        let err = account.unwrap_err();
        assert!(err
            .to_string()
            .contains("Account user10 not found under chain id alpha-goerli"));
    }

    #[test]
    fn test_get_account_failed_to_convert_field_elements() {
        let provider = get_provider("http://127.0.0.1:5050/rpc").unwrap();
        let account1 = get_account(
            "with_wrong_private_key",
            &Utf8PathBuf::from("tests/data/accounts/faulty_accounts.json"),
            &provider,
            &Network::Testnet,
        );
        let err1 = account1.unwrap_err();
        assert!(err1
            .to_string()
            .contains("Failed to convert private key: privatekey to FieldElement"));

        let account2 = get_account(
            "with_wrong_address",
            &Utf8PathBuf::from("tests/data/accounts/faulty_accounts.json"),
            &provider,
            &Network::Testnet,
        );
        let err2 = account2.unwrap_err();
        assert!(err2
            .to_string()
            .contains("Failed to convert account address: address to FieldElement"));
    }

    #[test]
    fn test_get_block_id() {
        let pending_block = get_block_id("pending").unwrap();
        let latest_block = get_block_id("latest").unwrap();

        assert_eq!(pending_block, BlockId::Tag(Pending));
        assert_eq!(latest_block, BlockId::Tag(Latest));
    }

    #[test]
    fn test_get_block_id_hex() {
        let block = get_block_id("0x0").unwrap();

        assert_eq!(
            block,
            BlockId::Hash(
                FieldElement::from_hex_be(
                    "0x0000000000000000000000000000000000000000000000000000000000000000"
                )
                .unwrap()
            )
        );
    }

    #[test]
    fn test_get_block_id_num() {
        let block = get_block_id("0").unwrap();

        assert_eq!(block, BlockId::Number(0));
    }

    #[test]
    fn test_get_block_id_invalid() {
        let block = get_block_id("mariusz").unwrap_err();
        assert!(block
            .to_string()
            .contains("No such block id mariusz! Possible values are pending, latest, block hash (hex) and block number (u64)."));
    }

    #[test]
    fn test_get_network() {
        let testnet = get_network("testnet").unwrap();
        let testnet2 = get_network("testnet2").unwrap();
        let mainnet = get_network("mainnet").unwrap();

        assert_eq!(testnet, Network::Testnet);
        assert_eq!(testnet2, Network::Testnet2);
        assert_eq!(mainnet, Network::Mainnet);
    }

    #[test]
    fn test_get_network_invalid() {
        let net = get_network("mariusz").unwrap_err();
        assert!(net
            .to_string()
            .contains("No such network mariusz! Possible values are testnet, testnet2, mainnet."));
    }
}
