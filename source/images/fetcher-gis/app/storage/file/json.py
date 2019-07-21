#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from . import make_sure_directory_exists


def load(filename, encoding='utf-8'):
    ''' Загружает информацию из файл в формате JSON
    '''

    def read_data(f, encoding):
        '''
        '''
        return json.loads(f.read(), encoding=encoding)

    data = None
    if str(filename).endswith('.gz'):
        import gzip
        with gzip.open(filename, mode='rt', encoding=encoding) as f:
            data = read_data(f, encoding)
    else:
        with open(filename, mode='rt', encoding=encoding) as f:
            data = read_data(f, encoding)
    assert isinstance(data, (dict, list, tuple))
    return data


def save(filename, data, encoding='utf-8'):
    ''' Сохраняет информацию в файл в формате JSON
    '''
    assert isinstance(data, (dict, list, tuple))

    make_sure_directory_exists(filename)
    if filename.endswith('.gz'):
        import gzip
        with gzip.open(filename, mode='wt', encoding=encoding) as f:
            write_data(f, data)
    else:
        with open(filename, mode='wt', encoding=encoding) as f:
            write_data(f, data)


def write_data(f, data):
    ''' Сохраняет данные в формате JSON
    '''
    assert isinstance(data, (dict, list, tuple))
    f.write(json.dumps(data, indent=4, ensure_ascii=False))
