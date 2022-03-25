import os
import os.path
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
from src.utils import StandardLogFormatter, log_color_provider
from src.utils.config.project import Project

init_colorama()
cwd = os.getcwd()


async def cli(args, script_root, protostar_dir: Optional[Path]):
    log_color_provider.is_ci_mode = args.no_color

    logger = getLogger()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter(log_color_provider))
    logger.addHandler(handler)
    current_project = Project.get_current()

    try:
        if args.command == "install":
            handle_install_command(args)
        elif args.command == "remove":
            handle_remove_command(args)
        elif args.command == "init":
            init(args, script_root)
        elif args.command == "update":
            handle_update_command(args)
        elif args.command == "upgrade":
            upgrade()
        elif args.command == "test":
            cairo_paths: List[Path] = args.cairo_path or []
            if protostar_dir:
                cairo_paths.append(protostar_dir / "cairo")
            await run_test_runner(
                getattr(args, "tests-root"),
                project=current_project,
                omit=args.omit,
                match=args.match,
                cairo_paths=cairo_paths,
            )
        elif args.command == "build":
            cairo_paths: List[Path] = args.cairo_path
            if protostar_dir:
                cairo_paths.append(protostar_dir / "cairo")
            build_project(
                project=current_project,
                output_dir=args.output,
                cairo_path=cairo_paths,
                disable_hint_validation=args.disable_hint_validation,
            )
    except ProtostarException as err:
        logger.error(err.message)
