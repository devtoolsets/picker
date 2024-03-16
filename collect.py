#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import argparse
import datetime
import feedparser
import os
import re
import requests
import yaml

from concurrent.futures import ThreadPoolExecutor, as_completed
from html2text import html2text
from lxml import etree
from pathlib import Path
from urllib import parse
from utils import *

requests.packages.urllib3.disable_warnings()

today = datetime.datetime.now().strftime("%Y-%m-%d")
yesterday = datetime.date.today() + datetime.timedelta(-1)
rootPath = Path(__file__).absolute().parent
pattern = re.compile(r'[\\\*\?\|\s/:"<>]')
httpHeader = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/png,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9', }


def writeWiki(config, data: dict = {}):
    output = config["output"]
    wikiPath = rootPath.joinpath(
        f'{output}/daily/{today.split("-")[0]}/{today}.md')

    detail = rootPath.joinpath(
        f'{output}/daily/{today.split("-")[0]}/detail/{today}')
    detail.mkdir(parents=True, exist_ok=True)

    summary = f'# [每日摘要]{today}\n\n'
    for _, feedGroup in enumerate(data):
        for _, feedPages in enumerate(feedGroup):
            pages = feedPages['pages']
            feedPages.pop('pages')
            [summaryURL, summaryTitle], = feedPages.items()
            summary += f'- [{summaryTitle}]({summaryURL})\n'

            for url, page in pages.items():
                summary += f'  - [ ] [{page}]({url})\n'

    with open(wikiPath, 'w+', encoding="utf-8") as file:
        file.write(summary)


def loadConfig(yml: dict):
    feedSet = set()
    node = yml.get('feeds')
    proxy = yml['proxy']['url'] if yml.get(
        'proxy') and yml['proxy']['enable'] else ''
    config = {
        "feeds": [{
            'group': group,
            'path': item["filename"],
            'url': set(),
        }
            for group, item in node.items() if item['enabled']
        ],
        "max_workers": yml['max_workers'] if yml.get('max_workers') else os.cpu_count() * 8,
        "output": yml['output'] if yml.get('output') else 'wiki',
        "update": False,
        "retry": yml['httpRetry'] if yml.get('httpRetry') else 3,
        'timeout': yml['httpTimeout'] if yml.get('httpTimeout') else 3,
        "proxy": {'http': proxy, 'https': proxy} if proxy else {
            'http': None, 'https': None}
    }

    for info in config["feeds"]:
        group = info['group']
        opmlPath = info['path']
        try:
            tree = etree.parse(opmlPath)
            root = tree.getroot()
            for outline in root.xpath('/opml/body//outline[@xmlUrl]'):
                url = outline.get('xmlUrl').strip().rstrip('/')
                short = url.split('://')[-1].split('www.')[-1]
                if not [item for item in feedSet if short in item]:
                    feedSet.add(url)
                    info['url'].add(url)

        except Exception as e:
            config["feeds"].remove(info)
            config["update"] = True
            node[group]['enabled'] = False
            colorPrint.failed(f"[-] Failed parse '{opmlPath}' {e}")

    colorPrint.focus(f'[+] {len(feedSet)} feeds')
    return config


def parseFeed(url: str, response: requests.models.Response):
    updateFeeds = {}
    try:
        content = feedparser.parse(response.content)
        for entry in content.entries:
            day = entry.get('published_parsed')
            if not day:
                day = entry.get('updated_parsed')

            publishDay = datetime.date(day[0], day[1], day[2])
            if publishDay >= yesterday:
                updateFeeds[entry.link] = pattern.sub(
                    '-', entry.title.split('\n')[0])

        colorPrint.success(
            f'[+] {content.feed.title} {url} {len(updateFeeds)}/{len(content.entries)}')

        if updateFeeds:
            return {url: pattern.sub('-', content.feed.title.split('\n')[0]),
                    'pages': updateFeeds}

    except Exception as e:
        colorPrint.failed(f'[-] failed parse {url} {e}')


def httpGet(executor, url: str, **params):
    for count in range(params['retry']):
        try:
            response = requests.get(url, headers=httpHeader, verify=False,
                                    timeout=params['timeout'],
                                    proxies=params['proxy'])
            if response.status_code < 400:
                return params['process'](url, response)
            else:
                colorPrint.failed(
                    f'[-] Status code {response.status_code} for "{url}"')

        except Exception as e:
            colorPrint.failed(
                f'[-] failed {count+1} times to get "{url}"|{e}')


def worker(executor, iterators, operation, **params):
    result = []
    tasks = [executor.submit(operation, executor, iterator, **params)
             for iterator in iterators]
    for task in as_completed(tasks):
        temp = task.result()
        if temp:
            result.append(temp)

    return result


def pickLatestPage(executor, order, **params):
    group = params["feeds"][order]
    argv = {
        'process': parseFeed,
        'proxy': params['proxy'],
        'timeout': params['timeout'],
        'retry': params['retry']
    }

    return worker(executor, group.get('url'), httpGet, **argv)


def job(args, yamlConfig):
    config = loadConfig(yamlConfig)
    with ThreadPoolExecutor(config['max_workers']) as executor:
        results = worker(executor, range(len(config["feeds"])),
                         pickLatestPage, **config)

    writeWiki(config, results)
    return config


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', help='Update config file', required=False)
    parser.add_argument('--config', help='Specify config file', required=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = argument()
    yamlConfig = {}

    if args.config:
        configPath = Path(args.config).expanduser().absolute()
    else:
        configPath = rootPath.joinpath('config/config.yml')

    with open(configPath, encoding="utf-8") as stream:
        yamlConfig = yaml.safe_load(stream)

    if job(args, yamlConfig)['update']:
        with open(configPath, mode='w', encoding="utf-8") as stream:
            yaml.safe_dump(yamlConfig, stream, sort_keys=False)
