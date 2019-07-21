#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import json
import errno
from pathlib import Path


def make_sure_directory_exists(filename):
    ''' Создает каталог для заданного файла, если он не существует
    '''
    path = os.path.dirname(os.path.abspath(filename))
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def _write_data(f, data, fieldnames):
    ''' Сохраняет данные в формате CSV
    '''
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # Проверка на пустой файл
    if os.lseek(f.fileno(), 0, os.SEEK_CUR) == 0:
        writer.writeheader()

    for row in data:
        writer.writerow(
            {key: value for key, value in row.items() if key in fieldnames})


def save_to_csv(filename, data, fields=None, encoding='utf-8'):
    ''' Сохраняет информацию в файл в формате CSV
    '''
    assert isinstance(data, list)
    if not data:
        return
    filename = str(filename)
    fieldnames = fields if fields else data[0].keys()

    make_sure_directory_exists(filename)
    if filename.endswith('.gz'):
        import gzip
        with gzip.open(filename, mode='at', encoding=encoding) as f:
            _write_data(f, data, fieldnames)
    else:
        with open(filename, mode='at', encoding=encoding) as f:
            _write_data(f, data, fieldnames)


def load_from_json(filename):
    ''' Загружает данные из JSON-файла
    '''
    if Path(filename).is_file():
        data = json.loads(Path(filename).read_text())
        assert isinstance(data, (dict, list))
        return data
