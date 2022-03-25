import os
from logging import INFO, StreamHandler, getLogger
from colorama import init as init_colorama

from src.commands import (
    handle_install_command,
    handle_update_command,
    handle_remove_command,
    init,
    upgrade,
    print_current_version,
)
from src.commands.build.build_project import build_project
from src.commands.test import run_test_runner
from src.protostar_exception import ProtostarException
from src.utils import StandardLogFormatter, log_color_provider
from src.utils.config.project import Project

init_colorama()
cwd = os.getcwd()


async def cli(args, script_root):
    log_color_provider.is_ci_mode = args.no_color

    logger = getLogger()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter(log_color_provider))
    logger.addHandler(handler)
    current_project = Project.get_current()

    try:
        if args.version:
            print_current_version()
        elif args.command == "install":
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
                disable_hint_validation=args.disable_hint_validation,
            )
    except ProtostarException as err:
        logger.error(err.message)
