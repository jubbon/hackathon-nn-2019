#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from loguru import logger
import simpy

from agents import Clock, Dispatcher, Vehicle, Area
from resources import Stop


class City(simpy.Environment):
    ''' Основное окружение, описывающее город
    '''
    debug = False

    def __init__(self, resolution, interval, **kwargs):
        super(City, self).__init__(**kwargs)
        self.interval = interval
        self._resolution = resolution
        self._clock = Clock(self, interval=interval)
        # Виртуальные диспетчеры
        self._dispatchers = dict()
        # Транспортные средства
        self._vehicles = list()
        # Шестиугольные геообласти
        self._areas = dict()
        # Остановки общественного транспорта
        self._stops = dict()

    @property
    def current_time(self):
        '''
        '''
        return datetime.fromtimestamp(self.now).strftime("%H:%M")

    @property
    def resolution(self):
        '''
        '''
        return self._resolution

    # @property
    # def status(self):
    #     '''
    #     '''
    #     # Текущая загрузка всех мусорных контейнеров
    #     total_dumpster_load = 0
    #     for _, dumpster in self._dumpsters.items():
    #         total_dumpster_load += dumpster.state["value"]

    # return {"total_dumpster_load": round(total_dumpster_load, 1)}

    def area(self, h3_address):
        '''
        '''
        if h3_address in self._areas:
            return self._areas[h3_address]

    def add_area(self, h3_address, h3_area):
        ''' Добавляет геообласть
        '''
        self._areas[h3_address] = Area(self, h3_address, h3_area)

    def stop(self, stop_id):
        ''' Возвращается остановка по её идентификатору
        '''
        return self._stops.get(stop_id)

    def add_stop(self, stop_id, stop):
        ''' Добавляет остановку общественного транспорта
        '''
        self._stops[stop_id] = Stop(self, stop_id, stop)

    def add_thread(self, thread_id, thread):
        ''' Добавляет линию маршрута общественного транспорта
        '''
        properties = thread["route"]["properties"]
        # route_id = properties["ThreadMetaData"]["lineId"]
        initial_stop = properties["ThreadMetaData"]["EssentialStops"][0]
        initial_stop_id = initial_stop['id']

        available_areas = list()
        logger.debug(f"Creating connectivity for thread {thread_id}")
        for feature in reversed(thread["trace"]["features"]):
            properties = feature["properties"]
            h3_address = properties[f"h3_address_{self.resolution}"]
            stop_id = properties["stop_id"]
            stop_name = properties["name"]

            if available_areas:
                if h3_address in self._areas:
                    self._areas[h3_address].add_connectivity(thread_id, stop_id, stop_name, available_areas)
                else:
                    logger.warning(f"No area with address {h3_address} ({self.resolution}: {len(self._areas)})")
            available_areas.append(dict(
                h3_address=h3_address,
                destination_stop_id=stop_id
            ))
            if stop_id not in self._stops:
                # Добавляется новая остановка
                self.add_stop(stop_id, stop_name)
                if h3_address in self._areas:
                    self._areas[h3_address].add_stop(stop_id, stop_name)
                else:
                    logger.warning(f"No area with address {h3_address} ({self.resolution}: {len(self._areas)})")

        self._dispatchers.setdefault(
            initial_stop_id,
            Dispatcher(self,
                       stop_id=initial_stop_id,
                       stop_name=initial_stop['name'],
                       interval=self.interval)).add_thread(thread_id, thread)

    def departure_vehicle(self, thread):
        ''' Отправляет транспорт по маршруту
        '''
        assert thread
        self._vehicles.append(Vehicle(self, thread))

    def vehicle_type(self, route_type):
        '''
        '''
        VEHICLE_TYPES = {
            "bus": "автобус",
            "tramway": "трамвай",
            "minibus": "маршрутное такси",
            "trolleybus": "тролейбус",
            "metro": "метро"
        }
        return VEHICLE_TYPES.get(route_type, "транспортное средство")

    @classmethod
    def simulate(cls, resolution, environment, threads, start_time=0, finish_time=None, interval=60):
        ''' Выполняет симуляцию
        '''
        logger.debug("Выполняется симуляция...")
        env = cls(resolution=resolution, initial_time=start_time, interval=interval)

        for h3_address, h3_area in environment.items():
            env.add_area(h3_address, h3_area)
        for thread_id, thread in threads.items():
            env.add_thread(thread_id, thread)
        env.run(until=finish_time)
        return env
