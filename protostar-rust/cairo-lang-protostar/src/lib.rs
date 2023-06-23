
use std::path::{Path, PathBuf};


use anyhow::{Result};

use cairo_lang_compiler::project::{
    get_main_crate_ids_from_project, setup_single_file_project,
    update_crate_roots_from_project_config, ProjectError,
};

use cairo_lang_filesystem::ids::CrateId;
use cairo_lang_project::{DeserializationError, ProjectConfig, ProjectConfigContent};
use cairo_lang_semantic::db::SemanticGroup;




use cairo_lang_utils::ordered_hash_map::OrderedHashMap;

use smol_str::SmolStr;

pub mod casm_generator;
pub mod test_collector;

pub fn build_project_config(
    source_root: &Path,
    crate_name: &str,
) -> Result<ProjectConfig, DeserializationError> {
    let base_path: PathBuf = source_root
        .to_str()
        .ok_or(DeserializationError::PathError)?
        .into();
    let crate_roots = OrderedHashMap::from([(SmolStr::from(crate_name), base_path.clone())]);
    Ok(ProjectConfig {
        base_path,
        content: ProjectConfigContent { crate_roots },
        corelib: None,
    })
}

pub fn setup_project_without_cairo_project_toml(
    db: &mut dyn SemanticGroup,
    path: &Path,
    crate_name: &str,
) -> Result<Vec<CrateId>, ProjectError> {
    if path.is_dir() {
        match build_project_config(path, crate_name) {
            Ok(config) => {
                let main_crate_ids = get_main_crate_ids_from_project(db, &config);
                update_crate_roots_from_project_config(db, config);
                Ok(main_crate_ids)
            }
            _ => Err(ProjectError::LoadProjectError),
        }
    } else {
        Ok(vec![setup_single_file_project(db, path)?])
    }
}
