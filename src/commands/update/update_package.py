from git.repo import Repo


def update_package(package_name: str, repo_root_dir: str, packages_dir: str):
    repo = Repo(repo_root_dir)
