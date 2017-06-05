#!/usr/bin/env python3
import argparse
import configparser
import os
import platform
import shutil
import stat
import subprocess
import sys
import typing

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIGS_DIR = os.path.join(BASE_DIR, "configs_home/")
APPS_DIR = os.path.join(BASE_DIR, 'markup_resource/')

input_func = input
PLATFORM_DARWIN = 'Darwin'
PLATFORM_LINUX = 'Linux'


class ColorFormatCodes:
    BLUE = '\033[34m'
    BOLD = '\033[1m'
    NORMAL = '\033[0m'


class ConfigError(Exception):
    pass


def to_header(content: str):
    return ColorFormatCodes.BLUE + content + ColorFormatCodes.NORMAL


def to_bold(content: str):
    return ColorFormatCodes.BOLD + content + ColorFormatCodes.NORMAL


def confirm(question: str) -> bool:
    while True:
        answer = input_func(question + ' <Yes|No>').lower()

        if answer == 'yes' or answer == 'y':
            confirmed = True
            break
        if answer == 'no' or answer == 'n':
            confirmed = False
            break

    return confirmed


def delete(filepath):
    """
    Delete the given file, directory or link.

    It Should support undelete later on.

    Args:
        filepath (str): Absolute full path to a file. e.g. /path/to/file
    """
    # Some files have ACLs, let's remove them recursively
    remove_acl(filepath)

    # Some files have immutable attributes, let's remove them recursively
    remove_immutable_attribute(filepath)

    # Finally remove the files and folders
    if os.path.isfile(filepath) or os.path.islink(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)


def copy(src, dst):
    """
    Copy a file or a folder (recursively) from src to dst.

    For simplicity sake, both src and dst must be absolute path and must
    include the filename of the file or folder.
    Also do not include any trailing slash.

    e.g. copy('/path/to/src_file', '/path/to/dst_file')
    or copy('/path/to/src_folder', '/path/to/dst_folder')

    But not: copy('/path/to/src_file', 'path/to/')
    or copy('/path/to/src_folder/', '/path/to/dst_folder')

    Args:
        src (str): Source file or folder
        dst (str): Destination file or folder
    """
    assert isinstance(src, str)
    assert os.path.exists(src)
    assert isinstance(dst, str)

    # Create the path to the dst file if it does not exists
    abs_path = os.path.dirname(os.path.abspath(dst))
    if not os.path.isdir(abs_path):
        os.makedirs(abs_path)

    # We need to copy a single file
    if os.path.isfile(src):
        # Copy the src file to dst
        shutil.copy(src, dst)

    # We need to copy a whole folder
    elif os.path.isdir(src):
        shutil.copytree(src, dst)

    # What the heck is this ?
    else:
        raise ValueError("Unsupported file: {}".format(src))

    # Set the good mode to the file or folder recursively
    chmod(dst)


def link(target, link_to):
    """
    Create a link to a target file or a folder.

    For simplicity sake, both target and link_to must be absolute path and must
    include the filename of the file or folder.
    Also do not include any trailing slash.

    e.g. link('/path/to/file', '/path/to/link')

    But not: link('/path/to/file', 'path/to/')
    or link('/path/to/folder/', '/path/to/link')

    Args:
        target (str): file or folder the link will point to
        link_to (str): Link to create
    """
    assert isinstance(target, str)
    assert os.path.exists(target)
    assert isinstance(link_to, str)

    # Create the path to the link if it does not exists
    abs_path = os.path.dirname(os.path.abspath(link_to))
    if not os.path.isdir(abs_path):
        os.makedirs(abs_path)

    # Make sure the file or folder recursively has the good mode
    chmod(target)

    # Create the link to target
    os.symlink(target, link_to)


def chmod(target):
    """
    Recursively set the chmod for files to 0600 and 0700 for folders.

    It's ok unless we need something more specific.

    Args:
        target (str): Root file or folder
    """
    assert isinstance(target, str)
    assert os.path.exists(target)

    file_mode = stat.S_IRUSR | stat.S_IWUSR
    folder_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR

    # Remove the immutable attribute recursively if there is one
    remove_immutable_attribute(target)

    if os.path.isfile(target):
        os.chmod(target, file_mode)

    elif os.path.isdir(target):
        # chmod the root item
        os.chmod(target, folder_mode)

        # chmod recursively in the folder it it's one
        for root, dirs, files in os.walk(target):
            for cur_dir in dirs:
                os.chmod(os.path.join(root, cur_dir), folder_mode)
            for cur_file in files:
                os.chmod(os.path.join(root, cur_file), file_mode)

    else:
        raise ValueError("Unsupported file type: {}".format(target))


def error_and_exit(message: str):
    """
    Throw an error with the given message and immediately quit.

    Args:
        message(str): The message to display.
    """
    fail = '\033[91m'
    end = '\033[0m'
    sys.exit(fail + "Error: {}".format(message) + end)


def is_process_running(process_name: str) -> bool:
    """
    Check if a process with the given name is running.

    Args:
        (str): Process name, e.g. "Sublime Text"

    Returns:
        (bool): True if the process is running
    """
    is_running = False

    # On systems with pgrep, check if the given process is running
    if os.path.isfile('/usr/bin/pgrep'):
        dev_null = open(os.devnull, 'wb')
        returncode = subprocess.call(['/usr/bin/pgrep', process_name],
                                     stdout=dev_null)
        is_running = bool(returncode == 0)

    return is_running


def remove_acl(path):
    """
    Remove the ACL of the file or folder located on the given path.

    Also remove the ACL of any file and folder below the given one,
    recursively.

    Args:
        path (str): Path to the file or folder to remove the ACL for,
                    recursively.
    """
    # Some files have ACLs, let's remove them recursively
    if (platform.system() == PLATFORM_DARWIN and
            os.path.isfile('/bin/chmod')):
        subprocess.call(['/bin/chmod', '-R', '-N', path])
    elif ((platform.system() == PLATFORM_LINUX) and
              os.path.isfile('/bin/setfacl')):
        subprocess.call(['/bin/setfacl', '-R', '-b', path])


def remove_immutable_attribute(path):
    """
    Remove the immutable attribute of the given path.

    Remove the immutable attribute of the file or folder located on the given
    path. Also remove the immutable attribute of any file and folder below the
    given one, recursively.

    Args:
        path (str): Path to the file or folder to remove the immutable
                    attribute for, recursively.
    """
    # Some files have ACLs, let's remove them recursively
    if ((platform.system() == PLATFORM_DARWIN) and
            os.path.isfile('/usr/bin/chflags')):
        subprocess.call(['/usr/bin/chflags', '-R', 'nouchg', path])
    elif (platform.system() == PLATFORM_LINUX and
              os.path.isfile('/usr/bin/chattr')):
        subprocess.call(['/usr/bin/chattr', '-R', '-i', path])


class AppConfig:
    def __init__(self):
        self.name = None
        self.pretty_name = None
        self.configuration_files = set()


class RunOptions:
    verbose: bool = False
    mackup_path: str = ""
    apps: set = set()


class ApplicationRunner(object):
    def __init__(self, options: RunOptions, config: AppConfig):
        self.mackup_folder = options.mackup_path
        self.files = list(config.configuration_files)
        self.verbose = options.verbose

    def __getFilepaths(self, filename):
        return (os.path.join(os.environ['HOME'], filename), os.path.abspath(os.path.join(self.mackup_folder, filename)))

    def backup(self):
        """
        Backup the application config files.

        Algorithm:
            if exists home/file
              if home/file is a real file
                if exists mackup/file
                  are you sure ?
                  if sure
                    rm mackup/file
                    mv home/file mackup/file
                    link mackup/file home/file
                else
                  mv home/file mackup/file
                  link mackup/file home/file
        """
        # For each file used by the application
        for filename in self.files:
            (home_filepath, mackup_filepath) = self.__getFilepaths(filename)

            if not os.path.exists(home_filepath):
                print("Doing nothing: {} does not exist".format(home_filepath))

            elif os.path.islink(home_filepath):
                if os.path.exists(mackup_filepath) and os.path.samefile(home_filepath, mackup_filepath):
                    print("Doing nothing: {} is already backed up to {}".format(home_filepath, mackup_filepath))
                else:
                    print("Doing nothing: {} is a broken link, you might want to fix it.".format(home_filepath))
            else:
                print("Backing up {} to {} ...".format(home_filepath, mackup_filepath))

                if os.path.exists(mackup_filepath):
                    if os.path.isfile(mackup_filepath):
                        file_type = 'file'
                    elif os.path.isdir(mackup_filepath):
                        file_type = 'folder'
                    elif os.path.islink(mackup_filepath):
                        file_type = 'link'
                    else:
                        raise ValueError("Unsupported file: {}".format(mackup_filepath))

                    if confirm("A {} named {} already exists in the"
                               " backup.\nAre you sure that you want to"
                               " replace it ?"
                                       .format(file_type, mackup_filepath)):
                        delete(mackup_filepath)

                copy(home_filepath, mackup_filepath)
                delete(home_filepath)
                link(mackup_filepath, home_filepath)

    def restore(self):
        """
        Restore the application config files.

        Algorithm:
            if exists mackup/file
              if exists home/file
                are you sure ?
                if sure
                  rm home/file
                  link mackup/file home/file
              else
                link mackup/file home/file
        """
        # For each file used by the application
        for filename in self.files:
            (home_filepath, mackup_filepath) = self.__getFilepaths(filename)

            # If the file exists and is not already pointing to the mackup file
            # and the folder makes sense on the current platform (Don't sync
            # any subfolder of ~/Library on GNU/Linux)
            file_or_dir_exists = (os.path.isfile(mackup_filepath) or
                                  os.path.isdir(mackup_filepath))
            pointing_to_mackup = (os.path.islink(home_filepath) and
                                  os.path.exists(mackup_filepath) and
                                  os.path.samefile(mackup_filepath,
                                                   home_filepath))
            supported = True

            if file_or_dir_exists and not pointing_to_mackup and supported:
                if self.verbose:
                    print("Restoring\n  linking {}\n  to      {} ..."
                          .format(home_filepath, mackup_filepath))
                else:
                    print("Restoring {} ...".format(filename))

                # Check if there is already a file in the home folder
                if os.path.exists(home_filepath):
                    # Name it right
                    if os.path.isfile(home_filepath):
                        file_type = 'file'
                    elif os.path.isdir(home_filepath):
                        file_type = 'folder'
                    elif os.path.islink(home_filepath):
                        file_type = 'link'
                    else:
                        raise ValueError("Unsupported file: {}"
                                         .format(mackup_filepath))

                    if confirm("You already have a {} named {} in your"
                               " home.\nDo you want to replace it with"
                               " your backup ?"
                                       .format(file_type, filename)):
                        delete(home_filepath)
                        link(mackup_filepath, home_filepath)
                else:
                    link(mackup_filepath, home_filepath)
            elif self.verbose:
                if os.path.exists(home_filepath):
                    print("Doing nothing\n  {}\n  already linked by\n  {}"
                          .format(mackup_filepath, home_filepath))
                elif os.path.islink(home_filepath):
                    print("Doing nothing\n  {}\n  "
                          "is a broken link, you might want to fix it."
                          .format(home_filepath))
                else:
                    print("Doing nothing\n  {}\n  does not exist"
                          .format(mackup_filepath))

    def uninstall(self):
        """
        Uninstall Mackup.

        Restore any file where it was before the 1st Mackup backup.

        Algorithm:
            for each file in config
                if mackup/file exists
                    if home/file exists
                        delete home/file
                    copy mackup/file home/file
            delete the mackup folder
            print how to delete mackup
        """
        # For each file used by the application
        for filename in self.files:
            (home_filepath, mackup_filepath) = self.__getFilepaths(filename)

            # If the mackup file exists
            if (os.path.isfile(mackup_filepath) or
                    os.path.isdir(mackup_filepath)):
                # Check if there is a corresponding file in the home folder
                if os.path.exists(home_filepath):
                    if self.verbose:
                        print("Reverting {}\n  at {} ..."
                              .format(mackup_filepath, home_filepath))
                    else:
                        print("Reverting {} ...".format(filename))

                    # If there is, delete it as we are gonna copy the Dropbox
                    # one there
                    delete(home_filepath)

                    # Copy the Dropbox file to the home folder
                    copy(mackup_filepath, home_filepath)
            elif self.verbose:
                print("Doing nothing, {} does not exist"
                      .format(mackup_filepath))


class ApplicationsDatabase(object):
    @staticmethod
    def get_config_files() -> set:
        config_files = set()

        for filename in os.listdir(APPS_DIR):
            if filename.endswith('.cfg'):
                config_files.add(os.path.join(APPS_DIR, filename))

        return config_files

    def __init__(self):
        self.apps: typing.Dict[str, AppConfig] = {}

        for config_file in ApplicationsDatabase.get_config_files():
            config = configparser.ConfigParser(allow_no_value=True)
            config.optionxform = str

            if config.read(config_file):
                filename = os.path.basename(config_file)
                app_name = filename[:-len('.cfg')]

                self.apps[app_name] = AppConfig()
                self.apps[app_name].name = app_name

                app_pretty_name = config.get('application', 'name')
                self.apps[app_name].pretty_name = app_pretty_name

                if config.has_section('configuration_files'):
                    for path in config.options('configuration_files'):
                        if path.startswith('/'):
                            raise ValueError('Unsupported absolute path: {}'
                                             .format(path))
                        self.apps[app_name].configuration_files.add(path)

    def get_app(self, app_name) -> AppConfig:
        return self.apps[app_name]

    def get_all_apps(self) -> typing.List[AppConfig]:
        return [v for k, v in self.apps.items()]


class Mackup(object):
    def __init__(self, options: RunOptions):
        self.options = options
        self.app_db = ApplicationsDatabase()

    def backup(self):
        self.__check_for_usable_backup_env()
        for app_name in sorted(self.options.apps):
            app = ApplicationRunner(self.options, self.app_db.get_app(app_name))
            self.__printAppHeader(app_name)
            app.backup()

    def restore(self):
        self.__check_for_usable_restore_env()
        for app_name in sorted(self.options.apps):
            app = ApplicationRunner(self.options, self.app_db.get_app(app_name))
            self.__printAppHeader(app_name)
            app.restore()

    def uninstall(self):
        self.__check_for_usable_restore_env()
        for app_name in sorted(self.options.apps):
            app = ApplicationRunner(self.options, self.app_db.get_app(app_name))
            self.__printAppHeader(app_name)
            app.uninstall()

    def list(self):
        self.__check_for_usable_environment()
        output = "Supported applications:\n"

        app_names = list(map(lambda x: x.name, self.app_db.get_all_apps()))

        for app_name in sorted(app_names):
            output += " - {}\n".format(app_name)
        output += "\n"
        output += ("{} applications supported in Mackup".format(len(app_names)))
        print(output)

    def __printAppHeader(self, app_name):
        if self.options.verbose:
            print(("\n{0} {1} {0}").format(to_header("---"), to_bold(app_name)))

    def __check_for_usable_environment(self):
        """Check if the current env is usable and has everything's required."""

        # Do not let the user run Mackup as root
        if os.geteuid() == 0:
            error_and_exit("Running Mackup as a superuser is useless and"
                           " dangerous. Don't do it!")

    def __check_for_usable_backup_env(self):
        self.__check_for_usable_environment()
        self.__create_mackup_home()

    def __check_for_usable_restore_env(self):
        self.__check_for_usable_environment()

        if not os.path.isdir(self.options.mackup_path):
            error_and_exit("Unable to find the Mackup folder: {}\n"
                           "You might want to back up some files or get your"
                           " storage directory synced first."
                           .format(self.options.mackup_path))

    def __create_mackup_home(self):
        if not os.path.isdir(self.options.mackup_path):
            if confirm("Mackup needs a directory to store your"
                       " configuration files\n"
                       "Do you want to create it now? <{}>"
                               .format(self.options.mackup_path)):
                os.makedirs(self.options.mackup_path)
            else:
                error_and_exit("Mackup can't do anything without a home =(")


def main():
    CMD_PROGRAMS = 'apps'
    CMD_OP = 'op'
    CMD_DST = 'dst'
    CMD_OP_LIST = 'list'
    CMD_OP_BACKUP = 'backup'
    CMD_OP_RESTORE = 'restore'
    CMD_OP_UNINSTALL = 'uninstall'

    parser = argparse.ArgumentParser(prog='markup')
    parser.add_argument('--op',
                        dest=CMD_OP,
                        choices=[CMD_OP_LIST, CMD_OP_BACKUP, CMD_OP_RESTORE, CMD_OP_UNINSTALL],
                        required=True)
    parser.add_argument('--dst',
                        dest=CMD_DST,
                        default=CONFIGS_DIR,
                        type=str)
    parser.add_argument(CMD_PROGRAMS, nargs="+", help="Programs to install")

    args = vars(parser.parse_args())

    options = RunOptions()
    options.verbose = True
    options.mackup_path = args[CMD_DST]
    options.apps = set(args[CMD_PROGRAMS])

    mckp = Mackup(options)

    if args[CMD_OP] == CMD_OP_LIST:
        mckp.list()
    elif args[CMD_OP] == CMD_OP_BACKUP:
        mckp.backup()
    elif args[CMD_OP] == CMD_OP_RESTORE:
        mckp.restore()
    elif args[CMD_OP] == CMD_OP_UNINSTALL:
        mckp.uninstall()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
