#!/usr/bin/env python3
import collections
import os.path
import re
import ssl
import tarfile
import urllib.parse
import urllib.request


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



def find_first_level_of_tagfile(tf: tarfile.TarFile) -> str:
    # 通过遍历tar包里的内容，找到首级目录（如果有多个首级目录，那么此方法不适用)
    _mbs = tf.getmembers()
    counter = collections.Counter()
    for mb in _mbs:
        path = mb.path
        dname = path.split('/')[0]
        counter[dname] += 1

    return counter.most_common(1)[0][0]