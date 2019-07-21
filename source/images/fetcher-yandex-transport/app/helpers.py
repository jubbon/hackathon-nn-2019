#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import contextlib
import errno


@contextlib.contextmanager
def directory_exists(path):
    """ Менеджер контекста для создания каталога
    """
    path = str(path)
    try:
        try:
            if not os.path.isdir(path):
                os.makedirs(path)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
        yield
    finally:
        pass
