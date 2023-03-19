#!/usr/bin/env python3

import argparse
import os
import pathlib
import zipfile
from urllib.request import urlretrieve
import urllib

def fetch_zip(commit_hash, zip_dir, *, org='python', binary=False, verbose):
    repo = f'cpython-{"bin" if binary else "source"}-deps'
    url = f'https://github.com/{org}/{repo}/archive/{commit_hash}.zip'

    proxies = {
        'https': 'https://127.0.0.1:1080',
        'http': 'http://127.0.0.1:1080'
    }
    # 需要加上headers， 否则报错: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xa0 in position 8974: invalid start byte
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
    }
    proxy = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    reporthook = None
    if verbose:
        reporthook = print
    zip_dir.mkdir(parents=True, exist_ok=True)
    filename, headers = urlretrieve(
        url,
        zip_dir / f'{commit_hash}.zip',
        reporthook=reporthook,
    )
    return filename


def extract_zip(externals_dir, zip_path):
    with zipfile.ZipFile(os.fspath(zip_path)) as zf:
        zf.extractall(os.fspath(externals_dir))
        return externals_dir / zf.namelist()[0].split('/')[0]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action='store_true')
    p.add_argument('-b', '--binary', action='store_true',
                   help='Is the dependency in the binary repo?')
    p.add_argument('-O', '--organization',
                   help='Organization owning the deps repos', default='python')
    p.add_argument('-e', '--externals-dir', type=pathlib.Path,
                   help='Directory in which to store dependencies',
                   default=pathlib.Path(__file__).parent.parent / 'externals')
    p.add_argument('tag',
                   help='tag of the dependency')
    return p.parse_args()


def main():
    args = parse_args()
    zip_path = fetch_zip(
        args.tag,
        args.externals_dir / 'zips',
        org=args.organization,
        binary=args.binary,
        verbose=args.verbose,
    )
    final_name = args.externals_dir / args.tag
    extract_zip(args.externals_dir, zip_path).replace(final_name)


if __name__ == '__main__':
    main()
