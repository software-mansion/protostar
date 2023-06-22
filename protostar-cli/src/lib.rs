use anyhow::{anyhow, Result};
use camino::Utf8PathBuf;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use starknet::core::types::BlockId;
use starknet::core::types::BlockTag::{Latest, Pending};
use starknet::{
    accounts::SingleOwnerAccount,
    core::{chain_id, types::FieldElement},
    providers::jsonrpc::{HttpTransport, JsonRpcClient},
    signers::{LocalWallet, SigningKey},
};
use std::fs;
use url::Url;

#[derive(Deserialize, Serialize)]
struct Account {
    private_key: String,
    public_key: String,
    address: String,
}

pub enum Network {
    Testnet,
    Testnet2,
    Mainnet,
}

impl Network {
    pub fn get_chain_id(&self) -> FieldElement {
        match self {
            Network::Testnet => chain_id::TESTNET,
            Network::Testnet2 => chain_id::TESTNET2,
            Network::Mainnet => chain_id::MAINNET,
        }
    }
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
    let accounts: Value = serde_json::from_str(&fs::read_to_string(path)?)?;
    let account_data = accounts
        .as_object()
        .and_then(|accounts_map| {
            accounts_map
                .get(chain_id)
                .and_then(|on_chain_accounts| on_chain_accounts.get(name))
        })
        .ok_or_else(|| anyhow!("Account {} not found under chain id {}", name, chain_id))?;

    let account: Account = serde_json::from_value(account_data.clone())?;
    Ok(account)
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
        FieldElement::from_hex_be(&account_info.private_key).unwrap(),
    ));
    let address = FieldElement::from_hex_be(&account_info.address).unwrap();
    let mut account = SingleOwnerAccount::new(provider, signer, address, network.get_chain_id());

    Ok(account)
}

pub fn get_block_id(value: &str) -> Result<BlockId> {
    match value {
        "pending" => Ok(BlockId::Tag(Pending)),
        "latest" => Ok(BlockId::Tag(Latest)),
        _ => Err(anyhow::anyhow!(
            "No such block id {}! Possible values are pending and latest for now.",
            value
        )),
    }
}
