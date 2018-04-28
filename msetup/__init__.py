import argparse

from msetup.apps.golang import Golang
from msetup.apps.openssl import OpenSSL
from msetup.apps.python3 import Python
from msetup.apps.zsh import Zsh
import msetup.base
from msetup.base.context import Context
from msetup.base.config import Config
from msetup.base import DEFAULT_BIN_DIR, DEFAULT_CONFIGS_DIR

INSTALLER = {
    'go': Golang,
    'python': Python,
    'zsh': Zsh,
    'openssl': OpenSSL,
}

CMD_FORCE = 'force'
CMD_PROGRAMS = 'programs'
CMD_BASE_DIR = 'base'


def main():

    parser = argparse.ArgumentParser(prog='install.py')
    parser.add_argument('--force', '-f',
                        dest=CMD_FORCE,
                        action='store_true',
                        default=False)

    parser.add_argument("--base",
                        dest=CMD_BASE_DIR,
                        type=str,
                        help="base directory")

    parser.add_argument(CMD_PROGRAMS,
                        nargs="+",
                        choices=INSTALLER.keys(),
                        help="Programs to install, available programs:{}".format(','.join(INSTALLER.keys())))

    args = vars(parser.parse_args())
    force = args[CMD_FORCE]
    programs = args[CMD_PROGRAMS]
    base_dir = args[CMD_BASE_DIR]
    msetup.base.setup_base_dir(base_dir)

    with Context(Config(BinDirectory=DEFAULT_BIN_DIR,
                        ConfigDirectory=DEFAULT_CONFIGS_DIR,
                        Force=force)) as ctx:

        for key in programs:
            programCls = INSTALLER[key]

            program = programCls(ctx)
            program.install()

if __name__ == "__main__":
    main()