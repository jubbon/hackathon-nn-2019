#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from loguru import logger


class Area():
    ''' Шестиугольная геообласть
    '''
    def __init__(self, env, h3_address, h3_area):
        self.env = env
        # Уникальный адрес области
        self.h3_address = h3_address
        # Характеристики области
        self.h3_area = h3_area
        # Другие доступные геообласти
        self.available_areas = dict()
        # Остановки в геообласти
        self.available_stops = dict()
        self.action = env.process(self.run())

    def add_stop(self, stop_id, stop_name):
        ''' Добавляет остановку в геообласть
        '''
        self.available_stops[stop_id] = stop_name

    def add_connectivity(self, thread_id, stop_id, stop_name, available_areas):
        ''' Задает информацию о доступности других геообластей
        '''
        for area in available_areas:
            h3_address = area["h3_address"]
            self.available_areas.setdefault(h3_address, list()).append({
                "thread_id": thread_id,
                "stop_id": stop_id,
                "stop_name": stop_name,
                "destination_stop_id": area["destination_stop_id"]
            })

    def emit(self, h3_address_destination, people_count):
        '''
        '''
        if h3_address_destination in self.available_areas:
            threads_to_destintion = self.available_areas[h3_address_destination]
            for thread in threads_to_destintion:
                stop_id = thread["stop_id"]
                self.env.stop(stop_id).add(h3_address_destination, people_count)

    # @property
    # def state(self):
    #     '''
    #     '''
    #     return dict(
    #         timestamp=self.env.now,
    #         uid=self.uid,
    #         latitude=self.latitude,
    #         longitude=self.longitude,
    #         dumpster_uid=self.dumpster_uid,
    #         current_emission=round(self.current_emission, 2),
    #         total_emission=round(self.total_emission, 2),
    #     )

    # def callback(self, event):
    #     '''
    #     '''
    #     self.env.set_house_state(self.state)

    def run(self):
        '''
        '''
        while True:
            yield self.env.timeout(self.env.interval)
