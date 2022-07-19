from protostar.commands.build import BuildCommand
from protostar.commands.deploy import DeployCommand
from protostar.commands.init import InitCommand
from protostar.commands.install import InstallCommand, handle_install_command
from protostar.commands.migrate import MigrateCommand
from protostar.commands.remove import (
    RemoveCommand,
    handle_remove_command,
    removal_exceptions,
)
from protostar.commands.test import TestCommand
from protostar.commands.update import UpdateCommand, handle_update_command
from protostar.commands.upgrade import UpgradeCommand
