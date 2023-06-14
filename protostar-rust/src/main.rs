use anyhow::{Context, Result};
use camino::Utf8PathBuf;
use clap::Parser;
use include_dir::{include_dir, Dir};
use scarb_metadata::MetadataCommand;
use tempfile::tempdir;

use rust_test_runner::pretty_printing;
use rust_test_runner::run_test_runner;

use std::process::Command;

static CORELIB: Dir = include_dir!("../cairo/corelib/src");

#[derive(Parser, Debug)]
struct Args {
    test_filter: Option<String>,
}

fn load_corelib() -> Result<Utf8PathBuf> {
    let tmp_dir = tempdir()?;
    CORELIB
        .extract(&tmp_dir)
        .expect("Failed to copy corelib to temporary directory");
    Utf8PathBuf::try_from(tmp_dir.into_path())
        .context("Failed to convert corelib path to Utf8PathBuf")
}

fn main_execution() -> Result<()> {
    let _args = Args::parse();

    // TODO #1997
    let corelib = load_corelib()?;

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    let _ = Command::new("scarb")
        .current_dir(std::env::current_dir().expect("failed to obtain current dir"))
        .arg("build")
        .output()?;

    for package in &scarb_metadata.workspace.members {
        let (base_path, dependencies) =
            rust_test_runner::dependencies_for_package(&scarb_metadata, package)?;

        run_test_runner(&base_path, Some(dependencies.clone()), Some(&corelib))?;
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
