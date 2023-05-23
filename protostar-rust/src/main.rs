use anyhow::Result;
use clap::Parser;
use rust_test_runner_bindings::run_tests;
use scarb_metadata::MetadataCommand;
use serde::Deserialize;
use std::env::set_var;
use std::path::PathBuf;
use cairo_lang_sierra_to_casm::invocations::InvocationError;

#[derive(Parser, Debug)]
struct Args {
    // #[clap(required = true)]
    paths: Vec<PathBuf>,
}

#[derive(Deserialize, Debug)]
struct ProtostarConfig {
    exit_first: Option<bool>,
    ignore: Option<Vec<String>>,
    json: Option<bool>,
    last_failed: Option<bool>,
    linked_libraries: Option<Vec<PathBuf>>,
    report_slowest_tests: Option<bool>,
}

fn fetch_protostar_config(cwd: &PathBuf, package_name: &str) -> Result<ProtostarConfig> {
    let metadata = MetadataCommand::new()
        .current_dir(cwd.parent().unwrap())
        .inherit_stderr()
        .exec()?;
    let raw_protostar_metadata = metadata
        .packages
        .iter()
        .find(|&x| x.name == package_name)
        .unwrap()
        .tool_metadata("protostar")
        .unwrap();
    let protostar_metadata: ProtostarConfig =
        serde_json::from_value(raw_protostar_metadata.clone())?;

    Ok(protostar_metadata)
}

fn main() {
    let args = Args::parse();
    // TODO resolve this path somehow
    set_var(
        "CARGO_MANIFEST_DIR",
        "/Users/arturmichalek/Coding/protostar/cairo/Cargo.toml",
    );

    let paths = &args.paths;
    println!("{:?}", paths);
    for path in paths {
        let protostar_config = fetch_protostar_config(path, "pkg");
        println!("{:?}", protostar_config);

        run_tests(path.to_str().unwrap()).unwrap();
    }
}
