#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
自动从中国下载vscode。

使用前先预装：

    pip install requests tqdm

使用示例：

    python3 cndlvsc.py deb

查看帮助：

    ./cndlvsc.py --help

更多介绍： https://note.qidong.name/2020/05/dl-vscode-cn/
"""
from argparse import ArgumentParser
from os.path import split
from urllib.parse import urlparse, urlunparse

import requests
from tqdm import tqdm

CN_DOMAIN = 'vscode.cdn.azure.cn'
TYPE2URL = {
    'win32': 'https://update.code.visualstudio.com/latest/win32/stable',
    'win64': 'https://update.code.visualstudio.com/latest/win32-x64/stable',
    'deb': 'https://update.code.visualstudio.com/latest/linux-deb-x64/stable',
    'rpm': 'https://update.code.visualstudio.com/latest/linux-rpm-x64/stable',
    'mac': 'https://update.code.visualstudio.com/latest/darwin/stable',
}


def main():
    args = _parse_args()

    url = TYPE2URL[args.type]
    resp = requests.get(url, allow_redirects=False)
    resp.raise_for_status()
    dl_url, fname = replace_domain(resp.next.url, CN_DOMAIN)

    if args.print_only:
        print(dl_url)
    else:
        download(dl_url, fname)


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'type',
        choices=TYPE2URL,
        help='The download type',
    )
    parser.add_argument(
        '-p',
        '--print-only',
        action='store_true',
        help='Print url only',
    )
    return parser.parse_args()


def replace_domain(url, domain):
    result = urlparse(url)
    lst = list(result)
    lst[1] = domain
    _, fname = split(result.path)
    return urlunparse(lst), fname


def download(url, fname):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


if __name__ == '__main__':
    main()