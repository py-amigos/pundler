""" Wrapper for argparse library to declar commands on handler functions.
"""
import argparse
import sys

from .errors import PundleException


class Command:
    """Result of applying CommandGroup.command decorator."""

    def __init__(self, name, fn, args_parser):
        self.name = name
        self.fn = fn
        self.args_parser = args_parser

    def print_help(self):
        self.args_parser.print_help()

    def __call__(self, args):
        try:
            self.fn(args)
        except PundleException as error:
            sys.stderr.write(str(error))
            sys.exit(1)


class Argument:
    """Arguments holder for the the argparse.ArgumentParser.add_argument call.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser):
        parser.add_argument(*self.args, **self.kwargs)


Option = Argument


class CommandGroup:
    """Group of the commands that are represented as argparse subparsers."""

    def __init__(self, cli_name):
        """ Create a group of the commands.

        :parma str prog: Name of the executable.
        """
        self.cli_name = cli_name
        self._parser = argparse.ArgumentParser(prog=cli_name)
        self._subparsers = self._parser.add_subparsers(
            title='subcommands',
            description='valid subcommands',
        )
        # The default command is run when there is no subcommand specified.
        self._default_command = None  # type: Command

    def command(self, name, help=None, is_default=False, arguments=()):
        parser = self._subparsers.add_parser(name, help=help)

        def decorator(fn):
            command = Command(name, fn, parser)
            if is_default:
                self._default_command = command
            parser.set_defaults(func=command)
            for arg in arguments:
                arg.add_to_parser(parser)
            return command
        return decorator

    def run(self):
        args = self._parser.parse_args()
        command = getattr(args, 'func', None)
        # args.func is missing in case if no subcommand specified
        if command is None and self._default_command:
            command = self._default_command
            args = command.args_parser.parse_args()

        if command:
            command(args)
        else:
            self._parser.print_help()
