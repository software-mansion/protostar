mod common;

use crate::common::runner::{corelib_path, runner};
use anyhow::Result;
use assert_fs::fixture::PathCopy;
use camino::Utf8PathBuf;
use snapbox::cmd::{cargo_bin, Command as SnapboxCommand};

#[test]
fn running_tests() -> Result<()> {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("example_package", &["**/*"]).unwrap();

    let snapbox = runner();
    let corelib = corelib_path()?;

    snapbox
        .current_dir(&temp)
        .args(&["--corelib-path", corelib.as_str()])
        .assert()
        .success();

    Ok(())
}
