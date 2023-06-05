use anyhow::{anyhow, Error, Result};
use cairo_lang_protostar::test_collector::LinkedLibrary;
use camino::Utf8PathBuf;
use clap::Parser;
use env_logger::{Builder, WriteStyle};
use log::{error, info, LevelFilter};
use rust_test_runner::{run_tests, ProtostarTestConfig};
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

fn initialize_logger() {
    Builder::new()
        .filter(Some("rust_test_runner"), LevelFilter::Info)
        .write_style(WriteStyle::Always)
        .init();
}

fn main_execution() -> Result<()> {
    let args = Args::parse();

    // TODO #1997
    set_var("CARGO_MANIFEST_DIR", "../../cairo/Cargo.toml");

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config = protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) = dependencies_for_package(&scarb_metadata, package)?;

        run_tests(base_path, Some(dependencies), &protostar_config)?;
    }

    Ok(())
}

fn main() -> Result<()> {
    initialize_logger();
    info!("Protostar started...");

    match main_execution() {
        Err(error) => error!("{}", error),
        _ => (),
    };

    Ok(())
}
