#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simpy


class Dumpster():
    ''' Площадка с мусорными контейнерами
    '''

    def __init__(self, env, uid, latitude, longitude, capacity, count=1, init=0.1):
        '''
        '''
        assert capacity, f"capacity: {capacity}"
        assert count, f"count: {count}"

        self.env = env
        # Уникальный идентификатор контейнерной площадки
        self.uid = uid
        # Широта контейнерной площадки
        self.latitude = latitude
        # Долгота контейнерной площадки
        self.longitude = longitude
        # Количество контейнеров на контейнерной площадке
        self.count = count
        # Максимальная емкость
        self.capacity = capacity * self.count
        # Наряд на вывоз мусора
        self.order_uid = None
        self.resource = simpy.Container(
            self.env,
            capacity=self.capacity * 10,
            init=init
        )

    @property
    def percent_level(self):
        '''
        '''
        value = round(self.resource.level, 2)
        return round(value / self.capacity, 3)

    @property
    def state(self):
        ''' Возвращает текущее состояние
        '''
        value = round(self.resource.level, 2)
        return dict(
            timestamp=self.env.now,
            uid=self.uid,
            latitude=self.latitude,
            longitude=self.longitude,
            count=self.count,
            capacity=self.capacity,
            value=value,
            percent_level=min(self.percent_level, 1),
            overflow=self.percent_level > 1.0
        )

    def set_order(self, order_uid):
        ''' Устанавливает наряд на вывоз мусора
        '''
        self.order_uid = order_uid

    def callback(self, event):
        '''
        '''
        self.env.set_dumpster_state(self.state)

    @property
    def value(self):
        return self.resource.level

    def clear(self):
        ''' Очищает мусорный контейнер
        '''
        p = self.resource.get(self.value)
        p.callbacks.append(self.callback)
        self.order_uid = None
        yield p

    def add(self, value):
        ''' Добавляет мусор в мусорный контейнер
        '''
        try:
            p = self.resource.put(value)
            p.callbacks.append(self.callback)
            yield p
        except ValueError:
            print(f"Container '{self.uid}' is overflow", flush=True)
