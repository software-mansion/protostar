use anyhow::{Context, Result};
use clap::Args;

use cast::wait_for_tx;
use starknet::accounts::{Account, Call, ConnectedAccount, SingleOwnerAccount};
use starknet::core::types::FieldElement;
use starknet::core::utils::get_selector_from_name;
use starknet::providers::jsonrpc::HttpTransport;
use starknet::providers::JsonRpcClient;
use starknet::signers::LocalWallet;

#[derive(Args)]
#[command(about = "Invoke a contract on Starknet")]
pub struct Invoke {
    /// Address of contract to invoke
    #[clap(short = 'a', long)]
    pub contract_address: String,

    /// Name of the function to invoke
    #[clap(short, long)]
    pub entry_point_name: String,

    /// Calldata for the invoked function
    #[clap(short, long)]
    pub calldata: Vec<String>,

    /// Max fee for the transaction. If not provided, max fee will be automatically estimated
    #[clap(short, long)]
    pub max_fee: Option<u128>,
}

pub async fn invoke(
    contract_address: &str,
    entry_point_name: &str,
    calldata: Vec<&str>,
    max_fee: Option<u128>,
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
    let execution = account.execute(vec![call]);

    let execution = if let Some(max_fee) = max_fee {
        execution.max_fee(FieldElement::from(max_fee))
    } else {
        execution
    };

    let result = execution.send().await?;

    wait_for_tx(account.provider(), result.transaction_hash).await;

    // todo (#2107): Normalize outputs in CLI
    println!("{result:?}");

    Ok(())
}
