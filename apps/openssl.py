#!/usr/bin/env python3
import os.path

from apps.zsh import Zsh
from base.install_info import InstallationInfo
from base.package_version_info import PackageVersionInfo
from base.program import Program
import util.parse
import util.install

class OpenSSL(Program):
    @classmethod
    def name(cls) -> str:
        return 'openssl'

    @classmethod
    def newVersion(self) -> PackageVersionInfo:
        pageURL = 'https://www.openssl.org/source/'
        packageURL = util.parse.extract_url_from_htmlpage_by_regex(pageURL, r'<a\shref\="(openssl-1[-\d\.\w]+\.tar\.gz)"\>')
        packageURL = pageURL + packageURL
        version = util.parse.get_version_string_from_package_url(packageURL)
        return PackageVersionInfo(Version=version, PackageURL=packageURL)

    def _install(self, packageInfo: PackageVersionInfo):
        self.ctx.installInfo[self.name()] = util.install.install_source_code_tgz(
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
