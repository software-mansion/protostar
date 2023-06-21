use clap::{Args};
use starknet::core::types::{BlockId, FieldElement, FunctionCall};
use starknet::core::utils::get_selector_from_name;
use starknet::providers::jsonrpc::HttpTransport;
use starknet::providers::{JsonRpcClient, Provider};
use anyhow::{Error, Result};


#[derive(Args)]
#[command(about = "Call a contract instance on Starknet", long_about = None)]
pub struct Call {
    /// Address of the called contract
    #[clap(short = 'a', long = "contract-address")]
    pub(crate) contract_address: String,

    /// Name of the contract function to be called
    #[clap(short = 'e', long = "func-name")]
    pub(crate) func_name: String,

    /// Arguments of the called function
    #[clap(short = 'c', long = "calldata", num_args = 1.., value_delimiter = ' ')]
    pub(crate) calldata: Option<Vec<String>>,

    /// Block identifier on which call should be performed
    #[clap(short = 'b', long = "block-id", default_value = "pending")]
    pub(crate) block_id: String,
}

pub async fn call(
    contract_address: &str,
    func_name: &str,
    calldata: &Option<Vec<String>>,
    provider: &JsonRpcClient<HttpTransport>,
    block_id: &BlockId,
) -> Result<(), Error> {
    let function_call = FunctionCall {
        contract_address: FieldElement::from_hex_be(contract_address)?,
        entry_point_selector: get_selector_from_name(func_name)?,
        calldata: calldata
            .clone()
            .unwrap()
            .iter()
            .map(|x| FieldElement::from_hex_be(x).unwrap())
            .collect(),
    };
    let res = provider.call(function_call, block_id).await?;

    Ok(())
}
