#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from datetime import datetime, timedelta

from loguru import logger
# from resources import Order


class Dispatcher():
    ''' Диспетчер
         - отправляет автобус на маршрут в заданное время
    '''

    def __init__(self, env, stop_id, stop_name, interval):
        self.env = env
        self._stop_id = stop_id
        self._stop_name = stop_name
        self._threads = dict()
        # Таймаут
        self.interval = interval

        self.action = env.process(self.run())

    # @property
    # def state(self):
    #     '''
    #     '''
    #     return dict(
    #         timestamp=self.env.now,
    #         uid=self.uid
    #     )

    def add_thread(self, thread_id, thread):
        ''' Привязывает линию маршрута к начальной остановке
        '''
        self._threads[thread_id] = thread

    def run(self):
        '''
        '''
        while True:
            now = datetime.fromtimestamp(self.env.now)
            # Отправка автобуса на линию
            for thread_id, thread in self._threads.items():
                # logger.debug(f"[{now}] Checking thread {thread_id}")
                value = None
                for interval in thread["intervals"]:
                    from_time_offset = datetime.strptime(interval["from"], "%H:%M")
                    from_time_offset = now.replace(
                        hour=from_time_offset.hour,
                        minute=from_time_offset.minute)
                    until_time_offset = datetime.strptime(interval["until"], "%H:%M")
                    until_time_offset = now.replace(
                        hour=until_time_offset.hour,
                        minute=until_time_offset.minute)
                    if now < from_time_offset:
                        break
                    if now > until_time_offset:
                        continue
                    value = interval["value"]
                if value:
                    last_departured = thread.setdefault("last_departured", now)
                    if now >= last_departured + timedelta(minutes=value):
                        route_ref = thread["meta"]["route_ref"]
                        route_type = thread["meta"]["route_type"]
                        logger.info(f"[{self.env.current_time}] C начальной остановки '{self._stop_name}' отправляется {self.env.vehicle_type(route_type)} по маршруту '{route_ref}'")
                        self.env.departure_vehicle(thread)
            yield self.env.timeout(self.interval)
