#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import requests
from invoke import task

from loguru import logger


@task
def fetch_poi(ctx, apikey, bbox, query):
    '''
    '''
    url = "https://search-maps.yandex.ru/v1/"
    params = dict(
        text=query,
        apikey=apikey,
        bbox=bbox,
        lang="ru_RU",
        rspn=1
    )
    response = requests.get(url, params=params)
    data = response.json()
    print(json.dumps(data, ensure_ascii=False, indent=4))
