#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simpy


class Route():
    ''' Маршрут общественного транспорта
    '''
    def __init__(self, env, uid, dumpsters, target):
        '''
        '''
        self.env = env
        # Уникальный идентификатор наряда
        self.uid = uid
        # Список контейнерных площадок
        self.dumpsters = dumpsters
        # Полигон, на который вывозится мусор
        self.target = target
        # Идентификатор автомобиля, который выполняет наряд
        self.vehicle_uid = None
        self.resource = simpy.Resource(self.env)

    @property
    def state(self):
        ''' Возвращает текущее состояние наряда
        '''
        return dict(
            timestamp=self.env.now,
            uid=self.uid
        )

    def set_vehicle(self, vehicle_uid):
        '''
        '''
        assert vehicle_uid
        self.vehicle_uid = vehicle_uid
