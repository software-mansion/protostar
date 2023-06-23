use anyhow::{Context, Result};
use clap::Args;

use cast::UDC_ADDRESS;
use starknet::accounts::SingleOwnerAccount;
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

    /// If false, salt will not be modified with account address
    #[clap(short, long, default_value = "true")]
    pub unique: String,

    /// Max fee for the transaction. If not provided, max fee will be automatically estimated
    #[clap(short, long)]
    pub max_fee: Option<String>,
}

pub async fn deploy(
    class_hash: &str,
    constructor_calldata: Vec<&str>,
    salt: Option<&str>,
    unique: &str,
    max_fee: Option<&str>,
    account: &SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet>,
) -> Result<(FieldElement, FieldElement)> {
    let salt = match salt {
        Some(salt) => FieldElement::from_hex_be(salt)?,
        // TODO: add random salt generation
        None => FieldElement::ZERO,
    };
    let class_hash = FieldElement::from_hex_be(class_hash)?;
    let unique = matches!(unique, "true");
    let raw_constructor_calldata = constructor_calldata
        .iter()
        .map(|cd| {
            FieldElement::from_hex_be(cd).context("Failed to convert calldata to FieldElement")
        })
        .collect::<Result<Vec<_>>>()?;

    let factory = ContractFactory::new(class_hash, account);
    let deployment = factory.deploy(&raw_constructor_calldata, salt, unique);

    let execution = if let Some(max_fee) = max_fee {
        deployment.max_fee(
            FieldElement::from_hex_be(max_fee)
                .context("Failed to convert max_fee to FieldElement")?,
        )
    } else {
        deployment
    };

    let result = execution.send().await?;

    let address = get_contract_address(salt, class_hash, &raw_constructor_calldata, UDC_ADDRESS);

    Ok((result.transaction_hash, address))
}
