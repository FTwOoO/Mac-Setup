#!/usr/bin/env python3
import abc
import argparse
import collections
import contextlib
import io
import json
import os.path
import pathlib
import re
import shutil
import ssl
import stat
import string
import subprocess
import tarfile
import typing
import urllib.parse
import urllib.request

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HOME_DIR = os.path.abspath(os.path.expanduser("~"))
ZSH_CONFIG_FILE = os.path.join(HOME_DIR, ".zshrc")
PACKAGES_INFO_FILE = os.path.join(BASE_DIR, ".packages.json")

Config = collections.namedtuple("Config", ["BinDirectory", "ConfigDirectory", "Update"])

InstallationInfo = collections.namedtuple("InstallationInfo",
                                          [
                                              "Name",  # 工具的名称(通常也是它可执行文件的名字)
                                              "Version",
                                              "PackageURL",  # 源码包URL下载地址
                                              "InstallLocation",  # 安装到什么位置，如果为None，则默认安装到bin/$Name/
                                              "ExecuteFileLocation",
                                              # 可执行文件在源码根目录中的相对路经，如果为None,则默认是pkg/bin/$Name
                                              "InstallCommands",  # 在源码根目录运行什么命令进行安装
                                              "UninstallCommands",
                                          ]
                                          )


class Context(contextlib.AbstractContextManager):
    config: Config
    installInfo: typing.Dict[str, InstallationInfo] = dict()

    def __init__(self, config: Config):
        self.config = config

    def __enter__(self):
        with open(PACKAGES_INFO_FILE, 'r') as f:
            d = json.loads(f.read())

            for k, v in d.items():
                self.installInfo[k] = InstallationInfo(**v)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(PACKAGES_INFO_FILE, 'w') as f:
            d = {}
            for k, v in self.installInfo.items():
                d[k] = v._asdict()

            fileData = json.dumps(d)
            f.write(fileData)


PackageVersionInfo = collections.namedtuple("PackageVersionInfo", ["Version", "PackageURL"])


class Program:
    def __init__(self, ctx: Context):
        self._ctx: Context = ctx

    @property
    def ctx(self) -> Context:
        return self._ctx

    @abc.abstractclassmethod
    def name(cls) -> str:
        pass

    @classmethod
    def dependencies(cls) -> typing.List:
        return []

    @abc.abstractclassmethod
    def newVersion(cls) -> PackageVersionInfo:
        pass

    @abc.abstractmethod
    def _install(self, packageInfo: PackageVersionInfo):
        pass

    def success_callback(self):
        pass

    def install(self):
        if len(self.dependencies()) > 0:
            for dpCls in self.dependencies():
                obj = dpCls(self.ctx)
                obj.install()
                dp = dpCls.name()

                if self.ctx.installInfo.get(dp) is None:
                    raise Exception("{} depands on {}".format(self.name(), dp))

                location = self.ctx.installInfo[dp].InstallLocation
                if not os.path.isdir(location):
                    raise Exception("Missing {} at {}".format(dp, location))

        originInfo = self.ctx.installInfo.get(self.name())
        versionInfo = self.newVersion()

        if self.ctx.config.Update and originInfo is not None and originInfo.Version == versionInfo.Version:
            if originInfo.InstallLocation and os.path.isdir(originInfo.InstallLocation):
                print("The program[{}] is update to date".format(self.name()))
                return
            else:
                print("Package[{}] not found on path {}".format(self.name(), originInfo.InstallLocation))

        self._install(versionInfo)
        self.success_callback()


def extract_url_from_htmlpage_by_regex(sourceURL: str, regex: str) -> str:
    pageURL = sourceURL
    rsp = urllib.request.urlopen(pageURL, context=ssl._create_unverified_context())
    if rsp.status != 200:
        raise Exception("Fail to get {}, HTTP code{}".format(pageURL, rsp.status))

    data = rsp.read()
    html = data.decode('utf-8')
    urls = re.findall(regex, html, re.X)
    if len(urls) > 0:
        packageURL = sorted(urls)[-1]
        return packageURL
    else:
        raise Exception("Cant find any package urls from {}, with regex:{}".format(sourceURL, regex))


def get_version_string_from_package_url(url: str) -> str:
    _file_name = os.path.basename(urllib.parse.urlparse(url).path)
    version = _file_name.rstrip(".gz").rstrip(".tar").rstrip(".tgz")
    return version


def open_file_by_url(url):
    out_file = io.BytesIO()
    with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as response:
        if response.status != 200:
            raise Exception("Fail to get {}, HTTP code{}".format(url, response.status))

        data = response.read()
        out_file.write(data)
        out_file.flush()
        out_file.seek(0)

    return out_file


def find_first_level_of_tagfile(tf: tarfile.TarFile) -> str:
    # 通过遍历tar包里的内容，找到首级目录（如果有多个首级目录，那么此方法不适用)
    _mbs = tf.getmembers()
    counter = collections.Counter()
    for mb in _mbs:
        path = mb.path
        dname = path.split('/')[0]
        counter[dname] += 1

    return counter.most_common(1)[0][0]


def is_same_directory(path1: str, path2: str) -> bool:
    return path1.rstrip('/') == path2.rstrip('/')


def install_source_code_tgz(config: Config, options: InstallationInfo) -> InstallationInfo:
    install_location = options.InstallLocation
    if not install_location:
        install_location = os.path.join(config.BinDirectory, "{}/".format(options.Name))
    else:
        install_location = os.path.abspath(install_location)

    execute_file_location = options.ExecuteFileLocation
    if not execute_file_location:
        execute_file_location = os.path.join(install_location, "bin/{}".format(options.Name))
    else:
        execute_file_location = os.path.join(install_location, options.ExecuteFileLocation)

    # 解压后的源码目录名
    src_dir_name = ""

    # 解压后的源码目录
    src_dir = ""

    # Download tar.gz file and then unpack root directory to src_dir
    with open_file_by_url(options.PackageURL) as out_file:
        tf = tarfile.open(fileobj=out_file)
        src_dir_name = find_first_level_of_tagfile(tf)

        src_dir = os.path.join(config.BinDirectory, src_dir_name)
        if os.path.isdir(src_dir):
            shutil.rmtree(src_dir)

        tf.extractall(path=config.BinDirectory)

    if not os.path.isdir(src_dir):
        raise Exception("Cant find src directory: {}".format(src_dir))

    try:

        if not is_same_directory(install_location, src_dir) and os.path.exists(install_location):
            shutil.rmtree(install_location)

        os.chdir(src_dir)

        resolvedInfo = InstallationInfo(*options)
        resolvedInfo = resolvedInfo._replace(InstallLocation=install_location)
        resolvedInfo = resolvedInfo._replace(ExecuteFileLocation=execute_file_location)

        resolvedCommands = list(map(
            lambda cmdTpl: string.Template(cmdTpl).substitute(**resolvedInfo._asdict(), **config._asdict()),
            options.InstallCommands,
        ))
        resolvedInfo = resolvedInfo._replace(InstallCommands=resolvedCommands)

        for cmd in resolvedInfo.InstallCommands:
            subprocess.run(cmd, shell=True, check=True)

        return resolvedInfo
    except:
        raise
    finally:
        if not is_same_directory(install_location, src_dir):
            shutil.rmtree(src_dir)


class OpenSSL(Program):
    @classmethod
    def name(cls) -> str:
        return 'openssl'

    @classmethod
    def newVersion(self) -> PackageVersionInfo:
        if hasattr(self, '_newVersion'):
            return self._newVersion

        pageURL = 'https://www.openssl.org/source/'
        packageURL = extract_url_from_htmlpage_by_regex(pageURL, r'<a\shref\="(openssl-1[-\d\.\w]+\.tar\.gz)"\>')
        packageURL = pageURL + packageURL
        version = get_version_string_from_package_url(packageURL)
        return PackageVersionInfo(Version=version, PackageURL=packageURL)

    def _install(self, packageInfo: PackageVersionInfo):
        self.ctx.installInfo[self.name()] = install_source_code_tgz(
            self.ctx.config,
            InstallationInfo(
                Name=self.name(),
                Version=packageInfo.Version,
                PackageURL=packageInfo.PackageURL,
                InstallLocation=None,
                ExecuteFileLocation='bin/openssl',
                InstallCommands=[
                    """./config --prefix="$InstallLocation" --openssldir="$InstallLocation" """,
                    'make',
                    'make test',
                    'make install'],
                UninstallCommands=[],
            ))

    def success_callback(self):
        ob = Zsh(self.ctx)
        ob.export_path(os.path.dirname(self.ctx.installInfo[self.name()].ExecuteFileLocation))


class Python(Program):
    @classmethod
    def name(cls) -> str:
        return 'python'

    @classmethod
    def dependencies(cls) -> typing.List:
        return [OpenSSL]

    @classmethod
    def newVersion(self) -> PackageVersionInfo:
        nextURL = extract_url_from_htmlpage_by_regex("https://www.python.org/downloads/",
                                                     r'<a \s href="(/downloads/release/python-[\d]+/)">')
        nextURL = 'https://www.python.org' + nextURL
        packageURL = extract_url_from_htmlpage_by_regex(nextURL,
                                                        r'<a \s href="([\w\.\d\:\/-]+[\d\w\.]+\.tgz)">Gzipped \s source \s tarball')

        version = get_version_string_from_package_url(packageURL)
        return PackageVersionInfo(Version=version, PackageURL=packageURL)

    def _install(self, packageInfo: PackageVersionInfo):
        opensslLocation = self.ctx.installInfo['openssl'].InstallLocation

        opensslLib = os.path.join(opensslLocation, "lib/")
        opensslInclude = os.path.join(opensslLocation, "include/")

        self.ctx.installInfo[self.name()] = install_source_code_tgz(
            ctx.config,
            InstallationInfo(
                Name=self.name(),
                Version=packageInfo.Version,
                PackageURL=packageInfo.PackageURL,
                InstallLocation=None,
                ExecuteFileLocation='bin/python3',
                InstallCommands=[
                    """./configure --without-gcc CFLAGS="-I{OPENSSL_INCLUDE}" LDFLAGS="-L{OPENSSL_LIB}" --prefix=$InstallLocation """.format(
                        OPENSSL_INCLUDE=opensslInclude,
                        OPENSSL_LIB=opensslLib),
                    'make',
                    'make install',
                ],
                UninstallCommands=[],
            ))

    def success_callback(self):
        ob = Zsh(self.ctx)
        ob.export_path(os.path.dirname(self.ctx.installInfo[self.name()].ExecuteFileLocation))


class Golang(Program):
    @classmethod
    def name(cls) -> str:
        return "go"

    @classmethod
    def newVersion(cls) -> PackageVersionInfo:
        packageURL = extract_url_from_htmlpage_by_regex('https://golang.org/dl/',
                                                        r'<a \s class\="download" \s href\="([\w\.\d\:\/-]+darwin-amd64\.tar\.gz)">')
        version = get_version_string_from_package_url(packageURL)
        return PackageVersionInfo(Version=version, PackageURL=packageURL)

    def _install(self, packageInfo: PackageVersionInfo):
        self.ctx.installInfo[self.name()] = install_source_code_tgz(
            self.ctx.config,
            InstallationInfo(
                Name=self.name(),
                Version=packageInfo.Version,
                PackageURL=packageInfo.PackageURL,
                InstallLocation=None,
                ExecuteFileLocation=None,
                InstallCommands=[],
                UninstallCommands=[],
            ))

    def success_callback(self):
        ob = Zsh(self.ctx)
        ob.export_path(os.path.dirname(self.ctx.installInfo[self.name()].ExecuteFileLocation))
        gopath = os.path.join(os.path.dirname(self.ctx.installInfo[self.name()].InstallLocation), "gopath")
        ob.export("GOPATH", gopath)


class Zsh(Program):
    @classmethod
    def name(cls) -> str:
        return "zsh"

    @classmethod
    def newVersion(cls) -> PackageVersionInfo:
        return PackageVersionInfo(Version="1", PackageURL="")

    def _install(self, packageInfo: PackageVersionInfo):
        zsh_config = os.path.join(self.ctx.config.ConfigDirectory, "shell/zshrc.sh")

        target = pathlib.Path(ZSH_CONFIG_FILE)
        if target.is_file() or target.is_symlink():
            target.unlink()

        target.symlink_to(zsh_config)
        target.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)
        subprocess.run("{}".format(zsh_config), check=True, shell=True)

        self.ctx.installInfo[self.name()] = InstallationInfo(
            Name=self.name(),
            Version=packageInfo.Version,
            PackageURL=None,
            InstallLocation=None,
            ExecuteFileLocation=None,
            InstallCommands=[],
            UninstallCommands=[],
        )

    def export_path(self, path):
        key = "PATH"
        value = '''$PATH:{path}'''.format(path=path)
        return self.export(key, value)

    def export(self, key, value):
        cmd = '''export {key}="{value}" '''.format(key=key, value=value)
        zsh_path_config = os.path.join(self.ctx.config.ConfigDirectory, "shell/path.sh")
        with open(zsh_path_config, '+') as file:
            file.writelines([cmd])


INSTALLER = {
    'go': Golang,
    'python': Python,
    'zsh': Zsh,
    'openssl': OpenSSL,
}

CMD_UPDATE = 'update'
CMD_PROGRAMS = 'programs'

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='setup_system')
    parser.add_argument('--update', '-u',
                        dest=CMD_UPDATE,
                        action='store_true',
                        help='Check if there has updates, if so, update it')

    parser.add_argument(CMD_PROGRAMS,
                        nargs="+",
                        choices=INSTALLER.keys(),
                        help="Programs to install, available programs:{}".format(','.join(INSTALLER.keys())))

    args = vars(parser.parse_args())
    update = args[CMD_UPDATE]
    programs = args[CMD_PROGRAMS]

    with Context(Config(BinDirectory=os.path.join(os.path.dirname(__file__), "bin/"),
                        ConfigDirectory=os.path.join(os.path.dirname(__file__), "configs/"),
                        Update=update)) as ctx:

        for key in programs:
            programCls = INSTALLER[key]
            program = programCls(ctx)
            program.install()
