"""Test clis wrapper for the argparse."""
import mock
from collections import namedtuple

from pundleapp import clis, errors


SubcommandRun = namedtuple('SubcommandRun', 'group,cmd,sys_exit_mock')


def test_subcommand_run(capsys):
    def cmd(args):
        print('done')

    _call_subcommand(cmd)

    assert 'done' == capsys.readouterr().out.strip()


def test_subcommand_fails_with_pundle_error(capsys):
    # Given
    error_msg = 'Failed to find the reqs file'
    def cmd(args):
        raise errors.PundleException(error_msg)
    # When
    result = _call_subcommand(cmd)
    # Then
    assert error_msg == capsys.readouterr().err.strip()
    result.sys_exit_mock.assert_called_once_with(1)


def test_group_help_generated(capsys):
    group = clis.CommandGroup(cli_name='cli-name')

    @group.command('cmd-name', help='Cmd help message')
    def cmd(args):
        pass

    group._parser.print_help()
    assert """
usage: cli-name [-h] {cmd-name} ...

optional arguments:
  -h, --help  show this help message and exit

subcommands:
  valid subcommands

  {cmd-name}
    cmd-name  Cmd help message
    """.strip() == capsys.readouterr().out.strip()


def test_sucommand_help_generated(capsys):
    group = clis.CommandGroup(cli_name='cli-name')

    @group.command('cmd-name', help='Cmd help message', arguments=(
        clis.Option('--option', help='option help', action='store_true'),
        clis.Argument('arg_list', nargs='*')
    ))
    def cmd(args):
        """ Cmd help message.

        And this should be a description.

        Example:

        | cli-name cmd-name --option arg1 arg2
        """
        pass
    cmd.args_parser.print_help()
    assert """
usage: cli-name cmd-name [-h] [--option] [arg_list [arg_list ...]]

Cmd help message.

        And this should be a description.

        Example:

        | cli-name cmd-name --option arg1 arg2

positional arguments:
  arg_list

optional arguments:
  -h, --help  show this help message and exit
  --option    option help
    """.strip() == capsys.readouterr().out.strip()


@mock.patch('sys.exit')
def _call_subcommand(fn, sys_exit_mock, args=None):
    group = clis.CommandGroup(cli_name='cli-name')
    cmd = group.command('cmd-name')(fn)
    with mock.patch('sys.argv', [group.cli_name, cmd.name] + (args or [])):
        group.run()
    return SubcommandRun(group, cmd, sys_exit_mock)
