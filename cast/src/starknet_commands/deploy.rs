use anyhow::{Context, Result};
use clap::Args;
use rand::rngs::OsRng;
use rand::RngCore;

use cast::{wait_for_tx, UDC_ADDRESS};
use starknet::accounts::{ConnectedAccount, SingleOwnerAccount};
use starknet::contract::ContractFactory;
use starknet::core::types::FieldElement;
use starknet::core::utils::get_contract_address;
use starknet::providers::jsonrpc::HttpTransport;
use starknet::providers::JsonRpcClient;
use starknet::signers::LocalWallet;

#[derive(Args)]
#[command(about = "Deploy a contract on Starknet")]
pub struct Deploy {
    /// Class hash of contract to deploy
    #[clap(long)]
    pub class_hash: String,

    /// Calldata for the contract constructor
    #[clap(short, long)]
    pub constructor_calldata: Vec<String>,

    /// Salt for the address
    #[clap(short, long)]
    pub salt: Option<String>,

    /// If true, salt will be modified with an account address
    #[clap(short, long)]
    pub unique: bool,

    /// Max fee for the transaction. If not provided, max fee will be automatically estimated
    #[clap(short, long)]
    pub max_fee: Option<u128>,
}

pub async fn deploy(
    class_hash: &str,
    constructor_calldata: Vec<&str>,
    salt: Option<&str>,
    unique: bool,
    max_fee: Option<u128>,
    account: &SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet>,
) -> Result<(FieldElement, FieldElement)> {
    let salt = match salt {
        Some(salt) => FieldElement::from_hex_be(salt)?,
        None => FieldElement::from(OsRng.next_u32()),
    };
    let class_hash = FieldElement::from_hex_be(class_hash)?;
    let raw_constructor_calldata: Vec<FieldElement> = constructor_calldata
        .iter()
        .map(|cd| {
            FieldElement::from_hex_be(cd).context("Failed to convert calldata to FieldElement")
        })
        .collect::<Result<_>>()?;

    let factory = ContractFactory::new(class_hash, account);
    let deployment = factory.deploy(&raw_constructor_calldata, salt, unique);

    let execution = if let Some(max_fee) = max_fee {
        deployment.max_fee(FieldElement::from(max_fee))
    } else {
        deployment
    };

    let result = execution.send().await?;

    wait_for_tx(account.provider(), result.transaction_hash).await;

    let address = get_contract_address(
        salt,
        class_hash,
        &raw_constructor_calldata,
        FieldElement::from_hex_be(UDC_ADDRESS)?,
    );

    Ok((result.transaction_hash, address))
}
