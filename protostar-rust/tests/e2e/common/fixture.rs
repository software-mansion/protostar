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
        let temp_dir = TempDir::new().unwrap();
        let project_path = Utf8PathBuf::try_from(temp_dir.path().join(package_name)).unwrap();

        let output = Command::new("scarb")
            .current_dir(temp_dir.path())
            .args(["new", project_path.as_str()])
            .output()
            .expect("Failed to create a project with Scarb");

        println!("{}", std::str::from_utf8(&output.stdout).unwrap());
        assert!(output.status.success());

        TestRunnerFixture {
            project_path,
            temp_dir,
            corelib_path,
        }
    }

    fn create_file(&self, original_path: &str, destination_path: &str) {
        let destination_path = self.project_path.join(destination_path);
        let parent = destination_path.parent().unwrap();
        fs::create_dir_all(parent).unwrap();
        fs::copy(original_path, destination_path).expect("Failed to create a file");
    }

    fn run_selected_tests(&self, paths: &[(&str, &str)]) {
        let paths: Vec<(String, String)> = paths
            .iter()
            .map(|(source, destination)| {
                (
                    Utf8PathBuf::from(*source)
                        .canonicalize_utf8()
                        .unwrap()
                        .to_string(),
                    String::from(*destination),
                )
            })
            .collect();

        std::env::set_current_dir(&self.project_path).expect("Failed to set working directory");
        for (original_path, destination_path) in paths {
            self.create_file(&original_path, &destination_path)
        }

        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .exec()
            .expect("Failed to get Scarb metadata");
        let output = Command::new("scarb")
            .current_dir(std::env::current_dir().expect("Failed to get current directory"))
            .arg("build")
            .output()
            .expect("Failed to build contracts with Scarb");

        assert!(output.status.success());

        for package in &scarb_metadata.workspace.members {
            let protostar_config =
                rust_test_runner::protostar_config_for_package(&scarb_metadata, package).unwrap();
            let (base_path, dependencies) =
                rust_test_runner::dependencies_for_package(&scarb_metadata, package)
                    .expect("Failed to get dependencies for package");
            let runner_config = RunnerConfig::new(None, false, false, &protostar_config);
            println!("{}", self.corelib_path);
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
    test_runner.run_selected_tests(&[(
        "tests/data/simple_test/tests/test_simple.cairo",
        "tests/test.cairo",
    )]);

    let paths = fs::read_dir(std::env::current_dir().unwrap()).unwrap();

    for path in paths {
        println!("Name: {}", path.unwrap().path().display())
    }
}
