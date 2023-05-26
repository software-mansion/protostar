use anyhow::{anyhow, Context, Result};
use clap::Parser;
use rust_test_runner_bindings::run_tests;
use scarb_metadata::{Metadata, MetadataCommand, PackageId, PackageMetadata};
use serde::Deserialize;
use std::env::set_var;
use std::path::PathBuf;

const CONTRACT_TARGET: &str = "starknet-contract";

#[derive(Parser, Debug)]
struct Args {
    // #[clap(required = true)]
    // paths: Vec<PathBuf>,
    #[arg(short, long)]
    linked_libraries: Option<Vec<PathBuf>>,
}

#[derive(Deserialize, Debug)]
struct ProtostarConfig {
    exit_first: Option<bool>,
    ignore: Option<Vec<String>>,
    json: Option<bool>,
    last_failed: Option<bool>,
    report_slowest_tests: Option<bool>,
}

fn protostar_config_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<ProtostarConfig> {
    let raw_metadata = metadata
        .packages
        .iter()
        .find(|pk| pk.id == *package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .tool_metadata("protostar")
        .ok_or_else(|| anyhow!("Failed to find protostar config for package = {package}"))?
        .clone();
    let protostar_config: ProtostarConfig = serde_json::from_value(raw_metadata)?;

    Ok(protostar_config)
}

fn dependencies_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<(PathBuf, Vec<PathBuf>)> {
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
        .packages
        .iter()
        .find(|p| p.id == *package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .root
        .clone()
        .into_std_path_buf();

    let dependencies = compilation_unit
        .components
        .iter()
        .map(|cu| cu.source_root().to_owned().into_std_path_buf())
        .collect();

    Ok((base_path, dependencies))
}

fn main() -> Result<()> {
    let args = Args::parse();
    // TODO resolve this path somehow
    set_var(
        "CARGO_MANIFEST_DIR",
        "/Users/arturmichalek/Coding/protostar/cairo/Cargo.toml",
    );

    let scarb_metadata = MetadataCommand::new()
        .current_dir("/Users/arturmichalek/Coding/protostar/protostar-rust/pkg")
        .inherit_stderr()
        .exec()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config = protostar_config_for_package(&scarb_metadata, package)?;
        dbg!(&protostar_config);

        let (base_path, dependencies) = dependencies_for_package(&scarb_metadata, package)?;
        let dependencies = dependencies
            .iter()
            .filter(|d| d.to_str().map_or(true, |s| !s.contains("core/src")))
            .cloned()
            .collect::<Vec<_>>();
        dbg!(&dependencies);
        dbg!(&base_path);

        run_tests(
            "/Users/arturmichalek/Coding/protostar/protostar-rust/pkg",
            Some(&dependencies),
            // Some(&vec![PathBuf::from(
            //     "/Users/arturmichalek/Coding/protostar/protostar-rust/pkg/src",
            // )]),
        )?;
    }

    Ok(())
}
