#!/usr/bin/env python3

from msetup.base.package_version_info import PackageVersionInfo
from msetup.base.path_file import PathFile, ExportFile
from msetup.base.program import Program


class Zsh(Program):
    @classmethod
    def name(cls) -> str:
        return "zsh"

    @classmethod
    def newVersion(cls) -> PackageVersionInfo:
        return PackageVersionInfo(Version="1", PackageURL="")

    def export_path(self, path):
        PathFile.export_path(path)

    def export(self, key, value):
        ExportFile.add(key, value)
