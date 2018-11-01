""" Wrapper for argparse library to declar commands on handler functions.
"""
import argparse

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
            self.args_parser.exit(status=1, message=str(error))


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

    def __init__(self, cli_name, root_parser=None, options=None):
        """ Create a group of the commands.

        :param str prog: Name of the executable.
        :param Sequence[Option]: The options that are defined on the group.
        """
        self.cli_name = cli_name
        self._parser = root_parser or argparse.ArgumentParser(prog=cli_name)
        self._subparsers = self._parser.add_subparsers(
            title='subcommands',
            description='valid subcommands',
        )
        # The default command is run when there is no subcommand specified.
        self._default_command = None  # type: Command
        for option in (options or ()):
            option.add_to_parser(self._parser)
        self._setup_fns = []

    def on_start(self, fn):
        fn and self._setup_fns.append(fn)
        return self

    def group(self, name, help=None):
        """Register sub-group."""
        parser = self._subparsers.add_parser(name, help=help)
        def show_group_help(args):
            parser.print_help()
        parser.set_defaults(func=show_group_help)
        return CommandGroup(name, root_parser=parser)

    def command(self, name, help=None, is_default=False, arguments=()):
        """ Register the command in the group.

        :param str name: Name of the command.
        :param str help: Help message displayed when help for the group is shown.
        """
        def decorator(fn):
            description = get_command_description(fn)
            parser = self._subparsers.add_parser(
                name,
                help=help,
                description=description,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
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

        for fn in self._setup_fns:
            fn(args)

        command = getattr(args, 'func', None)
        # args.func is missing in case if no subcommand specified
        if command is None and self._default_command:
            command = self._default_command
            # If the argumetns are set for the group we are interested to parse
            # only the known args for the sub-command parser.
            args = command.args_parser.parse_known_args()

        if command:
            command(args)
        else:
            self._parser.print_help()


def get_command_description(fn):
    description = getattr(fn, '__doc__') or ''
    return description.strip()
