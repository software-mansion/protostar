use anyhow::{anyhow, Context, Result};
use camino::Utf8PathBuf;
use clap::Parser;
use include_dir::{include_dir, Dir};
use scarb_metadata::MetadataCommand;
use std::path::PathBuf;
use tempfile::{tempdir, TempDir};

use rust_test_runner::run_test_runner;
use rust_test_runner::{pretty_printing, RunnerConfig};

use std::process::Command;

static CORELIB_PATH: Dir = include_dir!("../cairo/corelib/src");

#[derive(Parser, Debug)]
struct Args {
    /// Name used to filter tests
    test_filter: Option<String>,
    /// Use exact matches for `test_filter`
    #[arg(short, long)]
    exact: bool,
}

fn load_corelib() -> Result<TempDir> {
    let tmp_dir = tempdir()?;
    CORELIB_PATH
        .extract(&tmp_dir)
        .expect("Failed to copy corelib to temporary directory");
    Ok(tmp_dir)
}

fn main_execution() -> Result<()> {
    let args = Args::parse();

    // TODO #1997
    let corelib_dir = load_corelib()?;
    let corelib_path: PathBuf = corelib_dir.path().into();
    let corelib = Utf8PathBuf::try_from(corelib_path.clone())
        .context("Failed to convert corelib path to Utf8PathBuf")?;

    let scarb_metadata = MetadataCommand::new().inherit_stderr().exec()?;

    let _ = Command::new("scarb")
        .current_dir(std::env::current_dir().expect("failed to obtain current dir"))
        .arg("build")
        .output()?;

    for package in &scarb_metadata.workspace.members {
        let protostar_config =
            rust_test_runner::protostar_config_for_package(&scarb_metadata, package)?;
        let (base_path, dependencies) =
            rust_test_runner::dependencies_for_package(&scarb_metadata, package)?;
        let runner_config =
            RunnerConfig::new(args.test_filter.clone(), args.exact, protostar_config);

        run_test_runner(
            &base_path,
            Some(dependencies.clone()),
            &runner_config,
            Some(&corelib),
        )?;
    }

    // Explicitly close the temporary directory so we can handle the error
    corelib_dir.close().with_context(|| {
        anyhow!(
            "Failed to close temporary directory = {} with corelib. Corelib files might have not been released from filesystem",
            corelib_path.display()
        )
    })?;
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
