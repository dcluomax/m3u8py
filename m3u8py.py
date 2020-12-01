#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import urllib
import os
import sys
import glob
import subprocess
import shutil


def get_url_list(host, body):
    lines = body.split('\n')
    ts_url_list = []
    for line in lines:
        if not line.startswith('#') and line != '':
            if line.startswith('http'):
                ts_url_list.append(line)
            else:
                ts_url_list.append('%s/%s' % (host, line))
    return ts_url_list


def get_host(url):
    parts = url.split('//', 1)
    return parts[0] + '//' + parts[1].split('/', 1)[0]


def get_m3u8_body(url):
    print ('read m3u8 file:', url)
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=10,
            pool_maxsize=10, max_retries=10)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    r = session.get(url, timeout=10)
    return r.content


def concat_vids(download_dir, filename):
    read_files = glob.glob(download_dir + '/*.ts')
    with open(filename + '.ts', 'wb') as outfile:
        for f in read_files:
            with open(f, 'rb') as infile:
                outfile.write(infile.read())


def download_ts_file(ts_url_list, download_dir):
    i = 0
    for ts_url in reversed(ts_url_list):
        i += 1
        file_name = ts_url[ts_url.rfind('/'):]
        curr_path = '%s%s' % (download_dir, file_name)
        print '\n[process]: %s/%s' % (i, len(ts_url_list))
        print ('[download]:', ts_url)
        if os.path.isfile(curr_path):
            print '[warn]: already downloaded'
            continue
        myfile = requests.get(ts_url)
        open(curr_path, 'wb').write(myfile.content)


def main(url, filename, download_dir):
    os.chdir(download_dir)
    filename = filename.strip()
    if not os.path.isdir(filename):
        os.mkdir(filename)
    host = get_host(url)
    body = get_m3u8_body(url).decode()
    ts_url_list = get_url_list(host, body)
    print ('total file count:', len(ts_url_list))
    tempfolderdir = os.path.join(download_dir, filename)
    download_ts_file(ts_url_list, tempfolderdir)
    concat_vids(tempfolderdir, filename)
    subprocess.call([
        'ffmpeg',
        '-i',
        filename + '.ts',
        '-acodec',
        'copy',
        '-vcodec',
        'copy',
        filename + '.mp4',
        ])
    os.remove(filename + '.ts')
    shutil.rmtree(filename)


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 2:
        main(args[1], args[2], args[3])
    else:
        print 'Usage:'
        print ('python', args[0], 'm3u8_url', 'file_name', 'save_dir\n')
