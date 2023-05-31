use anyhow::{anyhow, Result};
use cairo_lang_protostar::test_collector::LinkedLibrary;
use camino::Utf8PathBuf;
use clap::Parser;
use rust_test_runner::{ProtostarTestConfig, run_tests};
use scarb_metadata::{Metadata, MetadataCommand, PackageId};
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
        let protostar_config = rust_test_runner::protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) = rust_test_runner::dependencies_for_package(&scarb_metadata, package)?;

        run_tests(base_path, Some(dependencies), &protostar_config)?;
    }

    Ok(())
}
