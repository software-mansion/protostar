use rust_test_runner::pretty_printing;

use anyhow::{anyhow, Result};
use cairo_lang_protostar::test_collector::LinkedLibrary;
use camino::Utf8PathBuf;
use clap::Parser;
use rust_test_runner::{run_test_runner, ProtostarTestConfig};
use scarb_metadata::{Metadata, MetadataCommand, PackageId};
use std::env::set_var;

#[derive(Parser, Debug)]
struct Args {
    test_filter: Option<String>,
}

fn protostar_config_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<ProtostarTestConfig> {
    let raw_metadata = metadata
        .get_package(package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .tool_metadata("protostar")
        .ok_or_else(|| anyhow!("Failed to find protostar config for package = {package}"))?
        .clone();
    let protostar_config: ProtostarTestConfig = serde_json::from_value(raw_metadata)?;

    Ok(protostar_config)
}

fn dependencies_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<(Utf8PathBuf, Vec<LinkedLibrary>)> {
    let compilation_unit = metadata
        .compilation_units
        .iter()
        .filter(|unit| unit.package == *package)
        .min_by_key(|unit| match unit.target.name.as_str() {
            name @ "starknet-contract" => (0, name),
            name @ "lib" => (1, name),
            name => (2, name),
        })
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?;

    let base_path = metadata
        .get_package(package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .root
        .clone();

    let dependencies = compilation_unit
        .components
        .iter()
        .filter(|du| !du.source_path.to_string().contains("core/src"))
        .map(|cu| LinkedLibrary {
            name: cu.name.clone(),
            path: cu.source_root().to_owned().into_std_path_buf(),
        })
        .collect();

    Ok((base_path, dependencies))
}

fn main_execution() -> Result<()> {
    pretty_printing::enable_colors();

    let args = Args::parse();

    // TODO #1997
    set_var("CARGO_MANIFEST_DIR", "../../cairo/Cargo.toml");

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config = protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) = dependencies_for_package(&scarb_metadata, package)?;

        run_test_runner(base_path, Some(dependencies), &protostar_config)?;
    }
    Ok(())
}

fn main() {
    match main_execution() {
        Ok(()) => std::process::exit(0),
        Err(error) => {
            pretty_printing::print_error_message(error);
            std::process::exit(1);
        }
    };
}
