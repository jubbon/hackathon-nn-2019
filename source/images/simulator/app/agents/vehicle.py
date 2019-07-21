#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import math

# import requests

# from shapely.geometry import shape

from loguru import logger
from datetime import timedelta


class Vehicle():
    ''' Единица общественного транспорта (автобус, трамвай, троллейбус, поезд метро)
    '''
    def __init__(self, env, thread, capacity=0, value=0):
        self.env = env
        # Пассажировместимость
        self.capacity = capacity
        # Текущая загруженность
        self.value = value
        # Маршрут
        self.thread = thread
        # Время отправления с начальной остановки
        self.departured_time = self.env.now
        # Остановки, которые уже проехал
        self.arrived_stops = dict()
        # Start the run process everytime an instance is created.
        self.action = env.process(self.run())

    # @property
    # def state(self):
    #     '''
    #     '''
    #     return dict(
    #         timestamp=self.env.now,
    #         uid=self.uid,
    #         latitude=self.latitude,
    #         longitude=self.longitude,
    #         velocity=self.velocity,
    #         direction=self.direction,
    #         number=self.number,
    #         owner=self.owner,
    #         capacity=self.capacity,
    #         value=round(self.value),
    #         percent_level=min(round(float(self.value), 3) / self.capacity, 1)
    #     )

    # def callback(self, event):
    #     '''
    #     '''
    #     self.env.set_vehicle_state(self.state)

    # def on_movement(self, event):
    #     '''
    #     '''
    #     if self.env.now % 10 == 0:
    #         self.env.set_vehicle_state(self.state)

    # def move_to_route(self, route, after_step_handler=None):
    #     ''' Выполняет движение по маршруту
    #     '''
    #     try:
    #         legs = route["trips"][0]["legs"]
    #     except KeyError:
    #         legs = route["routes"][0]["legs"]

    #     for leg in legs:
    #         for step in leg["steps"]:
    #             geometry = step["geometry"]
    #             path = shape(geometry)
    #             duration = int(round(step["duration"] * 2))
    #             for n in range(duration):
    #                 distance = float(n) / duration
    #                 point = path.interpolate(distance=distance, normalized=True)
    #                 self.latitude = round(point.y, 6)
    #                 self.longitude = round(point.x, 6)
    #                 timeout = self.env.timeout(1)
    #                 timeout.callbacks.append(self.on_movement)
    #                 yield timeout

    #             # coords = step["geometry"]["coordinates"][-1]
    #             # self.longitude, self.latitude = coords
    #         if after_step_handler:
    #             yield from after_step_handler()

    # def movement_for_load_dumpsters(self):
    #     ''' Движение через контейнерные площадки
    #     '''
    #     if not self.order:
    #         return

    #     # Формирование маршрута
    #     coordinates = [(self.longitude, self.latitude)]
    #     for dumpster_uid, dumpster in self.order.dumpsters.items():
    #         coordinates.append([dumpster.longitude, dumpster.latitude])
    #     coordinates = ";".join([f"{point[0]},{point[1]}" for point in coordinates])
    #     url = f"http://osrm.vehicle:5000/trip/v1/car/{coordinates}"
    #     params = dict(
    #         steps="true",
    #         geometries="geojson",
    #         # overview="full"
    #     )
    #     response = requests.get(url, params=params)
    #     route = response.json()
    #     status = route["code"]
    #     if status != "Ok":
    #         print(route, flush=True)
    #         return

    #     # Движение по маршруту
    #     yield from self.move_to_route(
    #         route,
    #         after_step_handler=self.load_dumpster
    #     )

    # def movement_for_unload_garbage(self):
    #     ''' Движение на полигон
    #     '''
    #     # Задание местоположение полигона
    #     target = self.order.target
    #     target_latitude = target["latitude"]
    #     target_longitude = target["longitude"]

    #     # Формирование маршрута из текущей точки
    #     points = [
    #         (self.longitude, self.latitude),
    #         (target_longitude, target_latitude)
    #     ]
    #     coordinates = ";".join([f"{p[0]},{p[1]}" for p in points])
    #     url = f"http://osrm.vehicle:5000/route/v1/car/{coordinates}"
    #     params = dict(steps="true", geometries="geojson")
    #     response = requests.get(url, params=params)
    #     route = response.json()
    #     status = route["code"]
    #     if status != "Ok":
    #         print(route, flush=True)
    #         return

    #     # Следование по маршруту
    #     yield from self.move_to_route(
    #         route,
    #         after_step_handler=None
    #     )

    #     # Выгрузка мусора на полигоне
    #     p = self.env.process(
    #         self.unload_garbage(duration=20 * 60)
    #     )
    #     p.callbacks.append(self.callback)
    #     yield p

    # def load_dumpster(self):
    #     ''' Загружает контейнеры с контейнерной плоащдки
    #     '''
    #     try:
    #         for dumpster_uid, dumpster in self.order.dumpsters.items():
    #             if not math.isclose(dumpster.latitude, self.latitude, abs_tol=1e-4):
    #                 continue
    #             if not math.isclose(dumpster.longitude, self.longitude, abs_tol=1e-4):
    #                 continue

    #             # Текущая загруженность контейнера
    #             current_value = dumpster.value

    #             # Загрузка мусора на контейнерной площадке
    #             p = self.env.process(
    #                 self.load_garbage(value=current_value, duration=120)
    #             )
    #             p.callbacks.append(self.callback)
    #             yield p

    #             yield from dumpster.clear()
    #             break
    #     except KeyError:
    #         print(f"Container '{dumpster_uid}' not found", flush=True)

    def run(self):
        '''
        '''
        trace = self.thread["trace"]
        meta = self.thread["meta"]
        while True:
            # Движение по маршруту
            for feature in trace["features"]:
                properties = feature["properties"]
                route_time = properties["route_time"]
                stop_id = properties["stop_id"]
                if stop_id in self.arrived_stops:
                    continue
                eta = self.departured_time + round(route_time * 60)
                if self.env.now >= eta:
                    # Прибыл на остановку
                    self.arrived_stops[stop_id] = {
                        "eta": eta,
                        "entered": 0, # TODO
                        "exited": 0 # TODO
                    }
                    stop_name = properties["name"]
                    route_type = meta['route_type']
                    logger.info(f"[{self.env.current_time}] На остановку '{stop_name}' прибыл {self.env.vehicle_type(route_type)}, следующий по маршруту {meta['route_ref']}")
                    # TODO
            yield self.env.timeout(self.env.interval)

    # def load_garbage(self, value, duration):
    #     ''' Загружает мусор из контейнера в машину
    #     '''
    #     self.value += value
    #     if self.env.debug:
    #         print(f"[{self.env.now}] Loading garbage {value}. Current value: {self.value}", flush=True)
    #     yield self.env.timeout(duration)

    # def unload_garbage(self, duration):
    #     ''' Выгружает мусор из машины
    #     '''
    #     self.value = 0
    #     yield self.env.timeout(duration)
