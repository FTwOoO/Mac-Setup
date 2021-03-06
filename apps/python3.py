#!/usr/bin/env python3
import os.path
import os.path
import typing

import apps
from apps.zsh import Zsh
from base.install_info import InstallationInfo
from base.package_version_info import PackageVersionInfo
from base.program import Program


class Python(Program):
    @classmethod
    def name(cls) -> str:
        return 'python'

    @classmethod
    def dependencies(cls) -> typing.List:
        return [apps.openssl.OpenSSL]

    @classmethod
    def newVersion(self) -> PackageVersionInfo:
        nextURL = util.parse.extract_url_from_htmlpage_by_regex("https://www.python.org/downloads/",
                                                     r'<a \s href="(/downloads/release/python-[\d]+/)">')
        nextURL = 'https://www.python.org' + nextURL
        packageURL = util.parse.extract_url_from_htmlpage_by_regex(nextURL,
                                                        r'<a \s href="([\w\.\d\:\/-]+[\d\w\.]+\.tgz)">Gzipped \s source \s tarball')

        version = util.parse.get_version_string_from_package_url(packageURL)
        return PackageVersionInfo(Version=version, PackageURL=packageURL)

    def _install(self, packageInfo: PackageVersionInfo):
        opensslLocation = self.ctx.installInfo['openssl'].InstallLocation

        opensslLib = os.path.join(opensslLocation, "lib/")
        opensslInclude = os.path.join(opensslLocation, "include/")

        self.ctx.installInfo[self.name()] = util.install.install_source_code_tgz(
            self.ctx.config,
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