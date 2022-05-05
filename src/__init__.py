# Python complains about importing `Project`` if the import below is removed
from src.commands import (
    BuildCommand,
    InitCommand,
    InstallCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from src.main import main
