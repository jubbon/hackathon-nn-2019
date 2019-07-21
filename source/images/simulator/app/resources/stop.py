#!/usr/bin/env python
# -*- coding: utf-8 -*-

from loguru import logger


class Stop():
    ''' Остановка общественного транспорта
    '''
    def __init__(self, env, stop_id, stop_name):
        '''
        '''
        self.env = env
        self.stop_id = stop_id
        self.stop_name = stop_name
        # Люди, стоящие на остановке
        self.people = dict()

    def add(self, h3_address_destination, count):
        '''
        '''
        logger.error(f"[{self.env.current_time}] На остановку '{self.stop_name}' пришло {count} человек")
        self.people.setdefault(h3_address_destination, dict())[self.env.now] = count
