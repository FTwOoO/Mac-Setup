import argparse

from apps.golang import Golang
from apps.openssl import OpenSSL
from apps.python3 import Python
from apps.zsh import Zsh
import base
from base.context import Context
from base.config import Config

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
    base.setup_base_dir(base_dir)

    with Context(Config(BinDirectory=base.get_bin_dir(),
                        ConfigDirectory=base.get_config_dir(),
                        Force=force)) as ctx:

        for key in programs:
            programCls = INSTALLER[key]

            program = programCls(ctx)
            program.install()

if __name__ == "__main__":
    main()