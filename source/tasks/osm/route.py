#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from itertools import zip_longest

import geojson
import requests
from h3 import h3

from loguru import logger
from invoke import task


@task
def trace_route(ctx, route_dir, osrm_url, stop_time=0, encoding="utf-8", force=False):
    ''' Выполняет трассировку маршрутов общественного транспорта
    '''
    assert route_dir
    assert osrm_url

    stop_time = int(stop_time)

    for route_dir in Path(route_dir).iterdir():
        if not route_dir.is_dir():
            continue
        trace_filename = route_dir / "trace.geojson"
        if not force and trace_filename.exists():
            continue

        logger.info(f"Tracing route '{route_dir}' from {osrm_url}")

        route_filename = route_dir / "route.geojson"
        if not route_filename.is_file():
            logger.warning("File {route_filename} not found")
            continue
        route = geojson.loads(route_filename.read_text(encoding=encoding))
        assert isinstance(route, dict)

        # Обработка данных
        stops = list()
        for feature in route["features"]:
            geometry = feature["geometry"]
            properties = feature["properties"]
            if geometry["type"] == "Point":
                coords = geometry['coordinates']

                h3_addresses = dict()
                for res in (7, 8, 9, 10):
                    h3_addresses[f"h3_address_{res}"] = h3.geo_to_h3(coords[1], coords[0], res)
                properties.update(h3_addresses)

                del feature["geometries"]
                stop_id = properties["StopMetaData"]["id"].replace("stop__", "")
                properties.update(stop_id=stop_id)
                del properties["StopMetaData"]

                if "extra" in properties:
                    properties.update(properties["extra"])
                    del properties["extra"]

                stops.append(feature)


        # Запрос в сервис OSRM
        coordinates = ";".join([
            f"{stop['geometry']['coordinates'][0]},{stop['geometry']['coordinates'][1]}"
            for stop in stops
        ])
        url = f"{osrm_url}/route/v1/car/{coordinates}"
        logger.debug(url)
        params = dict(geometries="geojson", overview="full")
        response = requests.get(url, params=params)
        data = response.json()
        status = data["code"]
        if status != "Ok":
            logger.error(route)
        else:
            features = list()

            route_distance = 0
            route_time = 0
            for route in data["routes"]:
                legs = [None, ] + route["legs"]
                for stop, leg in zip_longest(stops, legs):
                    stop_name = stop["properties"]["name"] if stop else None
                    duration = leg["duration"] if leg else 0
                    route_time += round(duration)
                    distance = leg["distance"] if leg else 0
                    route_distance += distance

                    if "route_time" in stop["properties"]:
                        pass
                    else:
                        stop["properties"].update(
                            route_distance=round(route_distance, 0),
                            route_time=round(route_time / 60, 1),
                            stop_time=round(stop_time / 60, 1))
                    features.append(stop)
                    logger.debug(
                        f"{round(route_distance, 0)}: {round(route_time/60, 1)}: {stop_name}"
                    )
                    route_time += stop_time  # Время посадки-высадки пассажиров
                break

        feat_collection = geojson.FeatureCollection(features)
        data = geojson.dumps(feat_collection, ensure_ascii=False, indent=4)
        trace_filename.write_text(data)
