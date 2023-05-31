use anyhow::Result;
use clap::Parser;
use rust_test_runner::run_tests;
use scarb_metadata::MetadataCommand;
use std::env::set_var;

#[derive(Parser, Debug)]
struct Args {
    test_filter: Option<String>,
}

fn main() -> Result<()> {
    let args = Args::parse();

    // TODO #1997
    set_var("CARGO_MANIFEST_DIR", "../../cairo/Cargo.toml");

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config =
            rust_test_runner::protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) =
            rust_test_runner::dependencies_for_package(&scarb_metadata, package)?;

        run_tests(base_path, Some(dependencies), &protostar_config)?;
    }

    Ok(())
}
