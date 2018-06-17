#!/usr/bin/env python3
import io
import os.path
import shutil
import ssl
import string
import subprocess
import tarfile
import urllib.parse
import urllib.request
import  util
import base.install_info
import  base.config
import base.package_version_info
import  util.parse


def open_file_by_url(url):
    out_file = io.BytesIO()
    with urllib.request.urlopen(url, timeout=3600, context=ssl._create_unverified_context()) as response:
        if response.status != 200:
            raise Exception("Fail to get {}, HTTP code{}".format(url, response.status))

        data = response.read()
        out_file.write(data)
        out_file.flush()
        out_file.seek(0)

    return out_file


def is_same_directory(path1: str, path2: str) -> bool:
    return path1.rstrip('/') == path2.rstrip('/')


def install_source_code_tgz(config: base.config.Config, options: base.install_info.InstallationInfo) -> base.install_info.InstallationInfo:
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
    with open('/Users/ganxiangle/Library/Mobile Documents/com~apple~CloudDocs/Workspace/fooltwo.me/go1.10.3.darwin-amd64.tar.gz', 'rb') as out_file:
    #with open_file_by_url(options.PackageURL) as out_file:
        tf = tarfile.open(fileobj=out_file)
        src_dir_name = util.parse.find_first_level_of_tagfile(tf)

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

        resolvedInfo = base.install_info.InstallationInfo(*options)
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