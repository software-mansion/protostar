use anyhow::Result;
use clap::{Args, Parser, Subcommand};
use console::style;
use protostar_cli::{get_account, get_provider, Network};
use std::env;

mod starknet_commands;

#[derive(Parser)]
#[command(version)]
#[command(about = "protostar-cli - a protostar starknet CLI", long_about = None)]
struct Cli {
    /// RPC provider url address
    #[clap(short = 'u', long = "url")]
    rpc_url: String,

    /// Network name, one of: testnet, testnet2, mainnet
    #[clap(short = 'n', long = "network")]
    network: Option<String>,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Declare a contract
    Declare(Declare),
}

#[derive(Args)]
#[command(about = "Declare a contract to starknet", long_about = None)]
struct Declare {
    /// Path to the sierra compiled contract
    #[clap(short = 's', long = "sierra-contract-path")]
    sierra_contract_path: String,

    /// Path to the casm compiled contract
    #[clap(short = 'c', long = "casm-contract-path")]
    casm_contract_path: String,

    /// Account name to be used for contract declaration, defaults to __default__
    #[clap(short = 'a', long = "account", default_value = "__default__")]
    account: String,

    /// Path to the file holding accounts info, defaults to ~/.starknet_accounts/starknet_open_zeppelin_accounts.json
    #[clap(
        short = 'f',
        long = "accounts-file",
        default_value = "~/.starknet_accounts/starknet_open_zeppelin_accounts.json"
    )]
    accounts_file_path: String,
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

    let network_name = cli.network.unwrap_or_else(|| {
        env::var("STARKNET_NETWORK").unwrap_or_else(|_| {
            eprintln!(
                "{}",
                style("No --network flag passed nor STARTNKET_NETWORK environment variable set!")
                    .red()
            );
            std::process::exit(1);
        })
    });
    let network = get_network(&network_name)?;
    let provider = get_provider(&cli.rpc_url)?; // todo: Arc::new ?

    match &cli.command {
        Some(Commands::Declare(name)) => {
            let mut account =
                get_account(&name.account, &name.accounts_file_path, &provider, &network)?;
            let declare = starknet_commands::declare::declare(
                &name.sierra_contract_path,
                &name.casm_contract_path,
                &mut account,
            )
            .await?;
            // dbg!(declare);
            Ok(())
        }
        None => Err(anyhow::anyhow!("No command specified")),
    }
}
