use anyhow::{Context, Result};
use camino::Utf8PathBuf;
use clap::Parser;
use scarb_metadata::MetadataCommand;

use rust_test_runner::pretty_printing;
use rust_test_runner::run_test_runner;

#[derive(Parser, Debug)]
struct Args {
    test_filter: Option<String>,
    // TODO #1997 this is a temporary solution for tests to work, this argument
    //  should be detected automatically
    #[arg(short, long)]
    corelib_path: Option<String>,
}

fn main_execution() -> Result<()> {
    let args = Args::parse();

    // TODO #1997
    let corelib = match args.corelib_path {
        Some(corelib) => Utf8PathBuf::from(corelib),
        None => Utf8PathBuf::from("../../cairo/corelib/src")
            .canonicalize_utf8()
            .context("Failed to resolve corelib path")?,
    };

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config =
            rust_test_runner::protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) =
            rust_test_runner::dependencies_for_package(&scarb_metadata, package)?;

        run_test_runner(
            &base_path,
            Some(&dependencies),
            &protostar_config,
            Some(&corelib),
        )?;
    }
    Ok(())
}

fn main() {
    match main_execution() {
        Ok(()) => std::process::exit(0),
        Err(error) => {
            pretty_printing::print_error_message(&error);
            std::process::exit(1);
        }
    };
}
