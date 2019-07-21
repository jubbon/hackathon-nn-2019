#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv

from . import make_sure_directory_exists


def save(filename, data, fields=None, encoding='utf-8'):
    ''' Сохраняет информацию в файл в формате CSV
    '''
    assert isinstance(data, dict)

    fieldnames = fields if fields else data.keys()

    make_sure_directory_exists(filename)
    if filename.endswith('.gz'):
        import gzip
        with gzip.open(filename, mode='at', encoding=encoding) as f:
            write_data(f, data, fieldnames)
    else:
        with open(filename, mode='at', encoding=encoding) as f:
            write_data(f, data, fieldnames)


def write_data(f, data, fieldnames):
    ''' Сохраняет данные в формате CSV
    '''
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # Проверка на пустой файл
    if os.lseek(f.fileno(), 0, os.SEEK_CUR) == 0:
        writer.writeheader()

    writer.writerow(
        {key: value
         for key, value in data.items() if key in fieldnames})
