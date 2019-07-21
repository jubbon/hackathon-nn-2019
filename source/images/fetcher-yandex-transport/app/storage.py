#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pickle
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from helpers import directory_exists


class Storage():
    '''
    '''
    def __init__(self, root, encoding="utf-8"):
        '''
        '''
        self._path = Path(root)
        self._encoding = encoding
        self._routes = dict()
        self._traces = dict()

    def load_routes(self):
        ''' Загружает маршруты
        '''
        for filename in self._path.glob("routes/*/meta.json"):
            logger.debug(f"Loading routes from {filename}")
            route_uid = filename.parent.name
            data = filename.read_text(encoding=self._encoding)
            route = json.loads(data)
            assert isinstance(route, dict)
            self._routes.setdefault(route_uid, {}).update(**route)

            filename_features = filename.parent / "route.geojson"
            if filename_features.is_file():
                data = filename_features.read_text(encoding=self._encoding)
                features = json.loads(data)
                self._routes.setdefault(route_uid, {}).update(features=features)
        # logger.debug(self._routes)

    def load_traces(self, dt):
        ''' Загружает трассировки
        '''
        assert dt
        filename = self._path / "traces" / f"{dt:%Y%m%d}.pickle"
        if filename.is_file():
            logger.debug(f"Loading traces from {filename}")
            data = pickle.loads(filename.read_bytes())
            self._traces.setdefault(f"{dt:%Y%m%d}", {}).update(data)
            logger.debug(self._traces)
        else:
            logger.warning(f"No traces found for {dt:%Y%m%d}")

    def save_routes(self, route_uid=None):
        ''' Сохраняет маршруты
        '''
        logger.debug(f"Saving routes to {self._path}...")
        for uid, route in self._routes.items():
            if route_uid and uid != route_uid:
                continue

            filename = self._path / "routes" / uid / "route.geojson"
            with directory_exists(filename.parent):
                data = route["features"]
                filename.write_text(
                    json.dumps(data, ensure_ascii=False, indent=4),
                    encoding=self._encoding)

            filename = self._path / "routes" / uid / "meta.json"
            with directory_exists(filename.parent):
                data = dict(route_uid=route["route_uid"],
                            route_ref=route["route_ref"],
                            route_type=route["route_type"])
                filename.write_text(
                    json.dumps(data, ensure_ascii=False, indent=4),
                    encoding=self._encoding)

    def save_traces(self, dt=None):
        ''' Сохраняет трассировки
        '''
        if dt:
            dates_to_save = [f"{dt:%Y%m%d}", ]
        else:
            dates_to_save = self._traces.keys()

        for date in dates_to_save:
            filename_json = self._path / "traces" / f"{date}.json"
            logger.debug(f"Saving traces to {filename_json}")
            data = {}
            traces = self._traces.get(f"{date}", {})
            for route_id, trace in traces.items():
                data[route_id] = dict(
                    route_ref=trace["route_ref"],
                    route_type=trace["route_type"]
                )
                for from_hour, vehicles in trace["intervals"].items():
                    until_hour = from_hour + 1
                    if until_hour == 24:
                        until_hour = 0
                    data[route_id].setdefault("intervals", list()).append({
                        "from": f"{from_hour:02}:00",
                        "until": f"{until_hour:02}:00",
                        "value": 12.0,
                        "vehicles_count": len(vehicles)
                    })
            with directory_exists(filename_json.parent):
                filename_json.write_text(json.dumps(data,
                                                    ensure_ascii=False,
                                                    indent=4),
                                         encoding=self._encoding)

            filename_pickle = self._path / "traces" / f"{date}.pickle"
            with directory_exists(filename_json.parent):
                filename_pickle.write_bytes(pickle.dumps(traces))


@contextmanager
def storage(root):
    '''
    '''
    storage_ = Storage(root)
    storage_.load_routes()
    storage_.load_traces(datetime.now())
    try:
        yield storage_
    finally:
        storage_.save_routes()
        storage_.save_traces()
