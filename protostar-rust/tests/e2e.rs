use anyhow::Result;
use assert_fs::fixture::PathCopy;
use camino::Utf8PathBuf;
use snapbox::cmd::{cargo_bin, Command as SnapboxCommand};

#[test]
fn running_tests() -> Result<()> {
    let temp = assert_fs::TempDir::new().unwrap();
    temp.copy_from("example_package", &["**/*"]).unwrap();
    let snapbox = SnapboxCommand::new(cargo_bin!("rust_test_runner"));
    let corelib = Utf8PathBuf::from("../../cairo/corelib/src")
        .canonicalize_utf8()?
        .to_string();

    snapbox
        .current_dir(&temp)
        .args(&["--corelib-path", corelib.as_str()])
        .assert()
        .success();

    Ok(())
}
