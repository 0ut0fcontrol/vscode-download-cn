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
import re
import tarfile
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests
from tqdm import tqdm

CN_DOMAIN = "vscode.cdn.azure.cn"
TYPE2URL = {
    "win32": "https://update.code.visualstudio.com/latest/win32/stable",
    "win64": "https://update.code.visualstudio.com/latest/win32-x64/stable",
    "deb": "https://update.code.visualstudio.com/latest/linux-deb-x64/stable",
    "rpm": "https://update.code.visualstudio.com/latest/linux-rpm-x64/stable",
    "mac": "https://update.code.visualstudio.com/latest/darwin/stable",
    "server": "https://update.code.visualstudio.com/latest/linux-rpm-x64/stable",
}


def main():
    args = _parse_args()

    url = TYPE2URL[args.type]
    resp = requests.get(url, allow_redirects=False)
    resp.raise_for_status()
    dl_url, fname = replace_domain(resp.next.url, CN_DOMAIN)

    if args.type == "server":
        # before: https://vscode.cdn.azure.cn/stable/ccbaa2d27e38e5afa3e5c21c1c7bef4657064247/code-1.62.3-1637137194.el7.x86_64.rpm
        # after: https://vscode.cdn.azure.cn/stable/ccbaa2d27e38e5afa3e5c21c1c7bef4657064247/vscode-server-linux-x64.tar.gz
        fname = "vscode-server-linux-x64.tar.gz"
        parts = dl_url.split("/")
        parts[-1] = fname
        dl_url = "/".join(parts)

        commit = parts[-2]
        server_dir = Path.home() / ".vscode-server/bin" / commit

    if args.print_only:
        print(dl_url)
    else:
        if args.type == "server":
            if server_dir.exists():
                raise SystemExit(
                    f"\nError: Latest vscode-server(linux) dir exists:\n{server_dir}\n"
                    f"Please delete it if you want to reinstall.\n"
                )
            else:
                download(dl_url, fname)
                server_dir.parent.mkdir(parents=True, exist_ok=True)
                with tarfile.open(fname, "r:gz") as tar:
                    tar.extractall(path="./")
                    Path("./vscode-server-linux-x64").rename(server_dir)
                    print(f"extract vscode-server to {server_dir}")
        else:
            download(dl_url, fname)


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "type",
        choices=TYPE2URL,
        help="The download type",
    )
    parser.add_argument(
        "-p",
        "--print-only",
        action="store_true",
        help="Print url only",
    )
    return parser.parse_args()


def replace_domain(url, domain):
    result = urlparse(url)
    lst = list(result)
    lst[1] = domain
    fname = Path(result.path).name
    return urlunparse(lst), fname


def download(url, fname):
    print(f"Download latest vscode from {url}")
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=fname,
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


if __name__ == "__main__":
    main()