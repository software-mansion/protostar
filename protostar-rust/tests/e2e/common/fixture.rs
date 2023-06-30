use std::fs;
use std::process::Command;

use assert_fs::TempDir;
use camino::Utf8PathBuf;
use scarb_metadata::MetadataCommand;

use rust_test_runner::{run, RunnerConfig};

static CORELIB_PATH: &str = "../cairo/corelib/src";

struct TestRunnerFixture {
    project_path: Utf8PathBuf,
    corelib_path: Utf8PathBuf,
    temp_dir: TempDir,
}

impl TestRunnerFixture {
    fn new(package_name: &str) -> Self {
        let corelib_path = Utf8PathBuf::from(CORELIB_PATH).canonicalize_utf8().unwrap();
        let directory = TempDir::new().unwrap();
        let output = Command::new("scarb")
            .current_dir(directory.path())
            .args(["new", package_name])
            .output()
            .expect("Failed to create a project with Scarb");

        assert!(output.status.success());

        TestRunnerFixture {
            project_path: Utf8PathBuf::try_from(directory.path().join(package_name)).unwrap(),
            temp_dir: directory,
            corelib_path,
        }
    }

    fn create_file(&self, original_path: &str, destination_path: &str) {
        let path = self.project_path.join(destination_path);
        let parent = path.parent().unwrap();
        fs::create_dir_all(parent).unwrap();
        fs::copy(original_path, destination_path).expect("Failed to create a file");
    }

    fn run_selected_tests(&self, paths: [(&str, &str); 1]) {
        for (original_path, destination_path) in paths {
            self.create_file(original_path, destination_path)
        }
        std::env::set_current_dir(&self.project_path).expect("Failed to set working directory");
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .exec()
            .expect("Failed to get Scarb metadata");
        let _ = Command::new("scarb")
            .current_dir(std::env::current_dir().expect("Failed to get current directory"))
            .arg("build")
            .output()
            .expect("Failed to build contracts with Scarb");
        for package in &scarb_metadata.workspace.members {
            let protostar_config =
                rust_test_runner::protostar_config_for_package(&scarb_metadata, package).unwrap();
            let (base_path, dependencies) =
                rust_test_runner::dependencies_for_package(&scarb_metadata, package)
                    .expect("Failed to get dependencies for package");
            let runner_config = RunnerConfig::new(None, false, false, &protostar_config);

            run(
                &base_path,
                Some(dependencies.clone()),
                &runner_config,
                Some(&self.corelib_path),
            )
            .expect("Failed to run tests");
        }
    }
}

#[test]
fn test() {
    let test_runner = TestRunnerFixture::new("my_pkg");
    test_runner.run_selected_tests([(
        "tests/data/simple_test/tests/test_simple.cairo",
        "tests/test.cairo",
    )]);

    // let paths = fs::read_dir(std::env::current_dir().unwrap()).unwrap();
    //
    // for path in paths {
    //     println!("Name: {}", path.unwrap().path().display())
    // }
}
