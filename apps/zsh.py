#!/usr/bin/env python3
import os.path
import os.path
import subprocess

from base.install_info import InstallationInfo
from base.package_version_info import PackageVersionInfo
from base.path_file import PathFile, ExportFile
from base.program import Program


class Zsh(Program):
    @classmethod
    def name(cls) -> str:
        return "zsh"

    @classmethod
    def newVersion(cls) -> PackageVersionInfo:
        return PackageVersionInfo(Version="1", PackageURL="")

    def _install(self, packageInfo: PackageVersionInfo):
        zsh_config = os.path.join(self.ctx.config.ConfigDirectory, ".zshrc")
        subprocess.run("zsh {}".format(zsh_config), check=True, shell=True)

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
        zsh_path_config = os.path.join(self.ctx.config.ConfigDirectory, "zsh/path.sh")
        with PathFile(zsh_path_config) as f:
            f.export_path(path)

    def export(self, key, value):
        zsh_path_config = os.path.join(self.ctx.config.ConfigDirectory, "zsh/path.sh")
        with ExportFile(zsh_path_config) as f:
            f.add(key, value)