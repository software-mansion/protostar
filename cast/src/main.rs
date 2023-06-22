use crate::starknet_commands::{call::Call, declare::Declare, invoke::Invoke};
use anyhow::Result;
use camino::Utf8PathBuf;
use clap::{Parser, Subcommand};
use console::style;
use cast::{get_account, get_block_id, get_provider, Network};

mod starknet_commands;

#[derive(Parser)]
#[command(version)]
#[command(about = "cast - a starknet-foundry CLI", long_about = None)]
struct Cli {
    /// RPC provider url address
    #[clap(short = 'u', long = "url")]
    rpc_url: String,

    /// Network name, one of: testnet, testnet2, mainnet
    #[clap(short = 'n', long = "network")]
    network: Option<String>,

    /// Account name to be used for contract declaration, defaults to __default__
    #[clap(short = 'a', long = "account", default_value = "__default__")]
    account: String,

    /// Path to the file holding accounts info, defaults to ~/.starknet_accounts/starknet_open_zeppelin_accounts.json
    #[clap(
        short = 'f',
        long = "accounts-file",
        default_value = "~/.starknet_accounts/starknet_open_zeppelin_accounts.json"
    )]
    accounts_file_path: Utf8PathBuf,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Declare a contract
    Declare(Declare),

    /// Call a contract
    Call(Call),

    /// Invoke a contract
    Invoke(Invoke),
}

fn get_network(name: &str) -> Result<Network> {
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

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // todo: #2052 take network from scarb config if flag not provided
    let network_name = cli.network.unwrap_or_else(|| {
        eprintln!("{}", style("No --network flag passed!").red());
        std::process::exit(1);
    });
    let network = get_network(&network_name)?;
    let provider = get_provider(&cli.rpc_url)?;

    match cli.command {
        Commands::Declare(declare) => {
            let mut account =
                get_account(&cli.account, &cli.accounts_file_path, &provider, &network)?;

            let declared_contract = starknet_commands::declare::declare(
                &declare.sierra_contract_path,
                &declare.casm_contract_path,
                &mut account,
            )
            .await?;
            eprintln!("Class hash: {}", declared_contract.class_hash);
            eprintln!("Transaction hash: {}", declared_contract.transaction_hash);
            Ok(())
        }
        Commands::Call(args) => {
            let block_id = get_block_id(&args.block_id).unwrap();

            let result = starknet_commands::call::call(
                args.contract_address.as_ref(),
                args.function_name.as_ref(),
                args.calldata.as_ref(),
                &provider,
                block_id.as_ref(),
            )
            .await?;

            // todo (#2107): Normalize outputs in CLI
            eprintln!("Call response: {:?}", result);
            Ok(())
        }
        Commands::Invoke(invoke) => {
            let mut account =
                get_account(&cli.account, &cli.accounts_file_path, &provider, &network)?;
            starknet_commands::invoke::invoke(
                &invoke.contract_address,
                &invoke.entry_point_name,
                invoke.calldata.iter().map(AsRef::as_ref).collect(),
                invoke.max_fee.as_deref(),
                &mut account,
            )
            .await?;
            Ok(())
        }
    }
}
