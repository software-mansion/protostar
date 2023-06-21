use anyhow::{Context, Result};
use clap::Args;

use starknet::accounts::{Account, Call, SingleOwnerAccount};
use starknet::core::types::FieldElement;
use starknet::core::utils::get_selector_from_name;
use starknet::providers::jsonrpc::HttpTransport;
use starknet::providers::JsonRpcClient;
use starknet::signers::LocalWallet;

#[derive(Args)]
#[command(about = "Invoke a contract on starknet")]
pub struct Invoke {
    /// Address of contract to invoke
    #[clap(long)]
    pub contract_address: String,

    /// Name of the function to invoke
    #[clap(long)]
    pub entry_point_name: String,

    /// Calldata for the invoked function
    #[clap(long)]
    pub calldata: Vec<String>,
}

pub async fn invoke(
    contract_address: &str,
    entry_point_name: &str,
    calldata: Vec<&str>,
    account: &mut SingleOwnerAccount<&JsonRpcClient<HttpTransport>, LocalWallet>,
) -> Result<()> {
    let call = Call {
        to: FieldElement::from_hex_be(contract_address)?,
        selector: get_selector_from_name(entry_point_name)?,
        calldata: calldata
            .iter()
            .map(|cd| {
                FieldElement::from_hex_be(cd).context("Failed to convert calldata to FieldElement")
            })
            .collect::<Result<Vec<_>>>()?,
    };
    let result = account
        .execute(vec![call])
        .max_fee(FieldElement::from_hex_be("0x2386f26fc10000")?)
        .send()
        .await?;

    dbg!(result);

    Ok(())
}
