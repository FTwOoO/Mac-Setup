#!/usr/bin/env python3
import os.path

from msetup.apps.zsh import Zsh
from msetup.base.install_info import InstallationInfo
from msetup.base.package_version_info import PackageVersionInfo
from msetup.base.program import Program


class Golang(Program):
    @classmethod
    def name(cls) -> str:
        return "go"

    @classmethod
    def newVersion(cls) -> PackageVersionInfo:
        packageURL = util.parse.extract_url_from_htmlpage_by_regex('https://golang.org/dl/',
                                                        r'<a \s class\="download" \s href\="([\w\.\d\:\/-]+darwin-amd64\.tar\.gz)">')
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
                ExecuteFileLocation=None,
                InstallCommands=[],
                UninstallCommands=[],
            ))

    def success_callback(self):
        ob = Zsh(self.ctx)
        ob.export_path(os.path.dirname(self.ctx.installInfo[self.name()].ExecuteFileLocation))

        gopath = os.path.join(self.ctx.config.BinDirectory, "gopath")
        gobin = os.path.join(gopath, 'bin/')

        ob.export("GOPATH", gopath)
        ob.export("GOROOT", self.ctx.installInfo[self.name()].InstallLocation)
        ob.export_path(gobin)
