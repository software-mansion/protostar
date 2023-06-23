use anyhow::{anyhow, Context, Result};
use camino::Utf8PathBuf;
use serde::{Deserialize, Serialize};
use starknet::core::types::BlockId;
use starknet::core::types::BlockTag::{Latest, Pending};
use starknet::{
    accounts::SingleOwnerAccount,
    core::{chain_id, types::FieldElement},
    providers::jsonrpc::{HttpTransport, JsonRpcClient},
    signers::{LocalWallet, SigningKey},
};
use std::collections::HashMap;
use std::fs;
use url::Url;

// Taken from starknet-rs
pub const UDC_ADDRESS: FieldElement = FieldElement::from_mont([
    15_144_800_532_519_055_890,
    15_685_625_669_053_253_235,
    9_333_317_513_348_225_193,
    121_672_436_446_604_875,
]);

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
        _ => Err(anyhow::anyhow!(
            "No such block id {}! Possible values are pending and latest for now.",
            value
        )),
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
