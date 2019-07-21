#!/usr/bin/env python
# -*- coding: utf-8 -*-

import overpy

from .. import logger

OVERPASS_URLS = [
    "http://localhost:12345/api/interpreter",
    # "http://overpass.openstreetmap.fr/api/interpreter"
]


def api(query):
    ''' Выполняет запрос к Overpass API
    '''
    for url in OVERPASS_URLS:
        try:
            api = overpy.Overpass(url=url)
            logger.debug(query)
            return api.query(query)
        except Exception as err:
            logger.error(err)
