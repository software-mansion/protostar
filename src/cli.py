from argparse import ArgumentParser

root_parser = ArgumentParser()
root_subparsers = root_parser.add_subparsers(help="types of A")

cmd_install_parser = root_subparsers.add_parser("install")
cmd_install_parser.add_argument("package", type=str, action="append")


def cli(args):
    print(args)


cli(root_parser.parse_args())
