import os
from logging import INFO, StreamHandler, getLogger

from colorama import init as init_colorama

from src.commands import (
    handle_install_command,
    handle_remove_command,
    handle_update_command,
    init,
)
from src.commands.compile import compile_contract
from src.commands.test import run_test_runner
from src.protostar_exception import ProtostarException
from src.utils import StandardLogFormatter, log_color_provider

init_colorama()
cwd = os.getcwd()


async def cli(args, script_root):
    log_color_provider.is_ci_mode = args.no_color

    logger = getLogger()
    logger.setLevel(INFO)
    handler = StreamHandler()
    handler.setFormatter(StandardLogFormatter(log_color_provider))
    logger.addHandler(handler)

    try:
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
                getattr(args, "sources-root"),
                omit=args.omit,
                match=args.match,
                cairo_paths=args.cairo_path,
                cairo_paths_recursive=args.cairo_path_recursive,
            )
        elif args.command == "compile":
            compile_contract(
                input_files=getattr(args, "input-files"),
                libraries_root=args.libraries_root,
                output_file=args.output,
                output_abi_file=args.abi,
                cairo_path=args.cairo_path,
            )
    except ProtostarException as err:
        logger.error(err.message)
