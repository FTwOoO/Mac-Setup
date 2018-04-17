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

    def export_path(self, path):
        PathFile.export_path( path)

    def export(self, key, value):
        ExportFile.add(key, value)
