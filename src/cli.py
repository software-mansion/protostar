import os
import os.path
import sys
from logging import INFO, StreamHandler, getLogger
from pathlib import Path
from typing import List, Optional

from colorama import init as init_colorama

from src.commands import (
    handle_install_command,
    handle_remove_command,
    handle_update_command,
    init,
    upgrade,
)
from src.commands.build.build_project import build_project
from src.commands.test import run_test_runner
from src.protostar_exception import ProtostarException
from src.utils import ProtostarDirectory, StandardLogFormatter, log_color_provider
from src.utils.config.project import Project
from src.utils.protostar_directory import VersionManager

init_colorama()
cwd = os.getcwd()


async def cli(args, script_root: Path):
    log_color_provider.is_ci_mode = args.no_color

    logger = getLogger()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter(log_color_provider))
    logger.addHandler(handler)

    protostar_directory = ProtostarDirectory(script_root)
    version_manager = VersionManager(protostar_directory)
    current_project = Project(version_manager)

    try:
        if args.version:
            version_manager.print_current_version()
        elif args.command == "install":
            handle_install_command(args)
        elif args.command == "remove":
            handle_remove_command(args)
        elif args.command == "init":
            init(args, script_root, version_manager)
        elif args.command == "update":
            handle_update_command(args)
        elif args.command == "upgrade":
            upgrade(protostar_directory, version_manager)
        elif args.command == "test":
            await run_test_runner(
                args.target,
                project=current_project,
                omit=args.omit,
                match=args.match,
                cairo_paths=inject_protostar_cairo_dir(
                    args.cairo_path or [], protostar_directory.protostar_binary_dir_path
                ),
            )
        elif args.command == "build":
            build_project(
                project=current_project,
                output_dir=args.output,
                cairo_path=inject_protostar_cairo_dir(
                    args.cairo_path or [], protostar_directory.protostar_binary_dir_path
                ),
                disable_hint_validation=args.disable_hint_validation,
            )
    except ProtostarException as err:
        logger.error(err.message)
    except KeyboardInterrupt:
        sys.exit()


def inject_protostar_cairo_dir(
    cairo_paths: List[Path], protostar_binary_dir: Optional[Path]
) -> List[Path]:
    if protostar_binary_dir:
        protostar_cairo_dir = protostar_binary_dir / "cairo"
        if protostar_cairo_dir not in cairo_paths:
            cairo_paths.append(protostar_cairo_dir)
    return cairo_paths
