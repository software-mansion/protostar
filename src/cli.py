import os
from logging import INFO, StreamHandler, getLogger

from colorama import init as init_colorama

from src.commands import (
    handle_install_command,
    handle_remove_command,
    handle_update_command,
    init,
)
from src.commands.build.build_project import build_project
from src.commands.test import run_test_runner
from src.utils import StandardLogFormatter
from src.utils.config.project import Project

init_colorama()
cwd = os.getcwd()


async def cli(args, script_root):
    logger = getLogger()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter())
    logger.addHandler(handler)
    current_project = Project.get_current()

    if args.command == "install":
        handle_install_command(args)
    elif args.command == "remove":
        handle_remove_command(args)
    elif args.command == "init":
        init(script_root)
    elif args.command == "update":
        handle_update_command(args)
    elif args.command == "test":
        await run_test_runner(
            getattr(args, "tests-root"),
            project=current_project,
            omit=args.omit,
            match=args.match,
            cairo_paths=args.cairo_path,
        )
    elif args.command == "build":
        build_project(
            project=current_project,
            output_dir=args.output,
            cairo_path=args.cairo_path,
        )
