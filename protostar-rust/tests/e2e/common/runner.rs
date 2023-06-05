use anyhow::{Context, Result};
use assert_fs::fixture::PathCopy;
use camino::Utf8PathBuf;
use snapbox::cmd::{cargo_bin, Command as SnapboxCommand};

pub fn runner() -> SnapboxCommand {
    let snapbox = SnapboxCommand::new(cargo_bin!("rust_test_runner"));
    snapbox
}

pub fn corelib_path() -> String {
    let corelib = Utf8PathBuf::from("../../cairo/corelib/src")
        .canonicalize_utf8()
        .expect("Failed to find corelib")
        .to_string();
    corelib
}
