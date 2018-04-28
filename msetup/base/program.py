#!/usr/bin/env python3
import abc
import os.path

import typing
import msetup.base.context as context
import msetup.base.package_version_info as package_version_info

class Program:
    def __init__(self, ctx: context.Context):
        self._ctx = ctx

    @property
    def ctx(self) -> context.Context:
        return self._ctx

    @abc.abstractclassmethod
    def name(cls) -> str:
        pass

    @classmethod
    def dependencies(cls) -> typing.List:
        return []

    @abc.abstractclassmethod
    def newVersion(cls) -> package_version_info.PackageVersionInfo:
        pass

    @abc.abstractmethod
    def _install(self, packageInfo: package_version_info.PackageVersionInfo):
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

        if not self.ctx.config.Force and originInfo is not None and originInfo.Version == versionInfo.Version:
            if originInfo.InstallLocation and os.path.isdir(originInfo.InstallLocation):
                print("The program[{}] is update to date".format(self.name()))
                return
            elif originInfo.InstallLocation:
                print("Package[{}] not found on path {}".format(self.name(), originInfo.InstallLocation))

        self._install(versionInfo)
        self.success_callback()

