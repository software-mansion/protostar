use camino::Utf8PathBuf;
use once_cell::sync::Lazy;
use snapbox::cmd::{cargo_bin, Command as SnapboxCommand};

static PATH: Lazy<String> = Lazy::new(|| {
    Utf8PathBuf::from("../../cairo/corelib/src")
        .canonicalize_utf8()
        .expect("Failed to find corelib")
        .to_string()
});

pub fn runner() -> SnapboxCommand {
    let snapbox = SnapboxCommand::new(cargo_bin!("rust_test_runner"));
    snapbox
}

pub fn corelib_path() -> &'static str {
    PATH.as_ref()
}
