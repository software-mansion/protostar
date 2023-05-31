use anyhow::{anyhow, Context, Result};
use cairo_lang_protostar::test_collector::{collect_tests, LinkedLibrary};
use cairo_lang_runner::{RunResultValue, SierraCasmRunner};
use camino::{Utf8Path, Utf8PathBuf};
use scarb_metadata::{Metadata, PackageId};
use serde::Deserialize;
use walkdir::WalkDir;

#[derive(Deserialize, Debug, PartialEq)]
pub struct ProtostarTestConfig {
    #[serde(default)]
    exit_first: bool, // TODO Not implemented!
}

fn run_result_value_to_string(run_result: RunResultValue) -> String {
    return match run_result {
        RunResultValue::Success(data) => format!("PASS {:?}", data),
        RunResultValue::Panic(data) => format!("FAIL {:?}", data),
    };
}

fn collect_tests_in_directory(input_path: &Utf8PathBuf) -> Result<Vec<Utf8PathBuf>> {
    let mut test_directories: Vec<Utf8PathBuf> = vec![];

    for entry in WalkDir::new(input_path) {
        let entry =
            entry.with_context(|| format!("Failed to read directory at path = {}", input_path))?;
        let path = entry.path();

        if path.is_file() && path.extension().unwrap_or_default() == "cairo" {
            test_directories.push(
                Utf8Path::from_path(path)
                    .with_context(|| format!("Failed to convert path = {:?} to utf-8", path))?
                    .to_path_buf(),
            );
        }
    }

    Ok(test_directories)
}

pub fn run_tests(
    input_path: Utf8PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
    config: &ProtostarTestConfig,
) -> Result<()> {
    let test_directories = collect_tests_in_directory(&input_path)?;
    for test in test_directories {
        run_tests_in_file(test, linked_libraries.clone())?;
    }
    Ok(())
}

fn run_tests_in_file(
    input_path: Utf8PathBuf,
    linked_libraries: Option<Vec<LinkedLibrary>>,
) -> Result<()> {
    let builtins = vec!["GasBuiltin", "Pedersen", "RangeCheck", "bitwise", "ec_op"];

    let (sierra_program, test_configs) =
        collect_tests(input_path.as_str(), None, linked_libraries, Some(builtins))?;

    let runner =
        SierraCasmRunner::new(sierra_program, Some(Default::default()), Default::default())
            .context("Failed setting up runner.")?;

    for config in &test_configs {
        let result = runner
            .run_function(
                runner.find_function(&config.name.as_str())?,
                &[],
                if let Some(available_gas) = &config.available_gas {
                    Some(available_gas.clone())
                } else {
                    Some(usize::MAX)
                },
                Default::default(),
            )
            .with_context(|| format!("Failed to run the function `{}`.", config.name.as_str()))?;
        let name = config.name.clone();
        let result_str = run_result_value_to_string(result.value);
        println!("{}: {}", name, result_str);
    }
    Ok(())
}

pub fn protostar_config_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<ProtostarTestConfig> {
    let raw_metadata = metadata
        .get_package(package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .tool_metadata("protostar")
        .ok_or_else(|| anyhow!("Failed to find protostar config for package = {package}"))?
        .clone();
    let protostar_config: ProtostarTestConfig = serde_json::from_value(raw_metadata)?;

    Ok(protostar_config)
}

pub fn dependencies_for_package(
    metadata: &Metadata,
    package: &PackageId,
) -> Result<(Utf8PathBuf, Vec<LinkedLibrary>)> {
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
        .get_package(package)
        .ok_or_else(|| anyhow!("Failed to find metadata for package = {package}"))?
        .root
        .clone();

    let dependencies = compilation_unit
        .components
        .iter()
        .filter(|du| !du.source_path.to_string().contains("core/src"))
        .map(|cu| LinkedLibrary {
            name: cu.name.clone(),
            path: cu.source_root().to_owned().into_std_path_buf(),
        })
        .collect();

    Ok((base_path, dependencies))
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;
    use assert_fs::fixture::{FileTouch, FileWriteStr, PathChild, PathCopy};
    use scarb_metadata::MetadataCommand;

    #[test]
    fn get_dependencies_for_package() -> Result<()> {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("pkg", &["**/*"]).unwrap();
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()?;

        let (_, dependencies) =
            dependencies_for_package(&scarb_metadata, &scarb_metadata.workspace.members[0])?;

        // TODO consider some assert for returned path (_)
        assert!(dependencies.len() > 0);
        Ok(())
    }

    #[test]
    fn get_dependencies_for_package_err_on_invalid_package() -> Result<()> {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("pkg", &["**/*"]).unwrap();
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()?;

        let result =
            dependencies_for_package(&scarb_metadata, &PackageId::from(String::from("12345679")));
        let err = result.unwrap_err();

        assert!(format!("{}", err).contains("Failed to find metadata for package"));

        Ok(())
    }

    #[test]
    fn get_protostar_config_for_package() -> Result<()> {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("pkg", &["**/*"]).unwrap();
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()?;

        let config =
            protostar_config_for_package(&scarb_metadata, &scarb_metadata.workspace.members[0])?;

        assert_eq!(
            config,
            ProtostarTestConfig {
                exit_first: false,
                json: false,
                last_failed: false,
                report_slowest_tests: false,
            }
        );

        Ok(())
    }

    #[test]
    fn get_protostar_config_for_package_err_on_invalid_package() -> Result<()> {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("pkg", &["**/*"]).unwrap();
        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()?;

        let result = protostar_config_for_package(
            &scarb_metadata,
            &PackageId::from(String::from("12345679")),
        );
        let err = result.unwrap_err();

        assert!(format!("{}", err).contains("Failed to find metadata for package"));

        Ok(())
    }

    #[test]
    fn get_protostar_config_for_package_err_on_missing_config() -> Result<()> {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("pkg", &["**/*"]).unwrap();
        let content = "[package]
name = \"pkg\"
version = \"0.1.0\"";
        temp.child("Scarb.toml").write_str(content)?;

        let scarb_metadata = MetadataCommand::new()
            .inherit_stderr()
            .current_dir(temp.path())
            .exec()?;

        let result =
            protostar_config_for_package(&scarb_metadata, &scarb_metadata.workspace.members[0]);
        let err = result.unwrap_err();

        assert!(format!("{}", err).contains("Failed to find protostar config for package"));

        Ok(())
    }

    #[test]
    fn collecting_tests() -> Result<()> {
        let temp = assert_fs::TempDir::new().unwrap();
        temp.copy_from("pkg", &["**/*"]).unwrap();
        let tests_path = Utf8PathBuf::from_path_buf(temp.to_path_buf()).unwrap();

        let tests = collect_tests_in_directory(&tests_path)?;

        assert!(tests.len() > 0);

        Ok(())
    }

    #[test]
    fn collecting_tests_err_on_invalid_dir() -> Result<()> {
        let tests_path = Utf8PathBuf::from("aaee");

        let result = collect_tests_in_directory(&tests_path);
        let err = result.unwrap_err();

        assert!(format!("{}", err).contains("Failed to read directory at path"));

        Ok(())
    }
}
