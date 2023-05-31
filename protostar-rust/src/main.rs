use anyhow::{anyhow, Result};
use camino::Utf8PathBuf;
use clap::Parser;
use scarb_metadata::{Metadata, MetadataCommand, PackageId};

use cairo_lang_protostar::test_collector::LinkedLibrary;
use rust_test_runner::pretty_printing;
use rust_test_runner::{run_test_runner, ProtostarTestConfig};

#[derive(Parser, Debug)]
struct Args {
    test_filter: Option<String>,
}

fn main_execution() -> Result<()> {
    let _args = Args::parse();

    // TODO #1997
    set_var("CARGO_MANIFEST_DIR", "../../cairo/Cargo.toml");

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config = rust_test_runner::protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) = rust_test_runner::dependencies_for_package(&scarb_metadata, package)?;

        run_test_runner(&base_path, Some(&dependencies), &protostar_config)?;
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
