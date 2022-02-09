from colorama import Fore

from src.commands.common import PackageConfig
from logging import getLogger


def init():
    """
    Interactive config creator

    """
    logger = getLogger()

    package = PackageConfig()
    logger.info("Package name:")
    package.name = input()

    logger.info("Package description:")
    package.description = input()

    logger.info("Package version:")
    package.description = input()

    package.write()
