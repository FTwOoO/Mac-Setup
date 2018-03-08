#!/usr/bin/env python3
import collections
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
