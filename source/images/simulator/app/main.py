#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from datetime import datetime
from pathlib import Path
import json

from loguru import logger

from data import save_to_csv, load_from_json

from city import City


def main():
    '''
    '''
    logger.remove(0)
    logger.add(sys.stdout, format="{time:DD.MM.YYYY HH:mm:ss} {message}", level="INFO")
    logger.add(f"/data/logs/simulator/log.txt", level="DEBUG")

    start_time = 1563760800

    finish_time = 1563760800 + 25 * 60
    # finish_time = 1563825600

    # Загрузка файла с описанием инфраструктуры
    resolution = os.getenv("H3_RES", 8)
    environment = load_from_json(Path(f"/data/environments/environment.{resolution}.json"))
    assert isinstance(environment, dict)

    # Загрузка файла со сценарием
    playbook = dict()
    for playbook_file in Path("/data/playbooks/baseline").iterdir():
        playbook.update(load_from_json(playbook_file))

    # Загрузка активных маршрутов
    active_threads = dict()
    for route_path in Path("/data/routes").iterdir():
        logger.debug(f"Loading thread {route_path}")
        meta_filename = route_path / "meta.json"
        meta = load_from_json(meta_filename)
        route_filename = route_path / "route.geojson"
        route = load_from_json(route_filename)
        trace_filename = route_path / "trace.geojson"
        trace = load_from_json(trace_filename)
        if trace is None:
            logger.warning(f"No trace found for {route_path}")
            continue
        assert isinstance(trace, dict), trace

        line_id = meta["route_uid"].split(".")[0]
        if line_id in playbook:
            active_threads[meta["route_uid"]] = {
                "meta": meta,
                "route": route,
                "trace": trace,
                "intervals": playbook[line_id]["intervals"]
            }
        else:
            logger.warning(f"Route {line_id} not active")
    logger.info(f"Loaded {len(active_threads)} active threads")
    env = City.simulate(
        resolution,
        environment,
        active_threads,
        start_time,
        finish_time,
        interval=60
    )

    #  # Сохранение результатов симуляции
    # dt = datetime.now()
    # path = Path(f"/data/result/{dt:%Y-%m-%d-%H-%M-%S}")
    # print(f"Saving simulation result to {path}", flush=True)
    # save_to_csv(path / "vehicles.csv", list(result.vehicle_states()))
    # save_to_csv(path / "houses.csv", list(result.house_states()))
    # save_to_csv(path / "dumpster.csv", list(result.dumpster_states()))

    # all_data = list()
    # for vehicle in result.vehicle_states():
    #     all_data.append({
    #         "timestamp": vehicle["timestamp"],
    #         "uid": vehicle["uid"],
    #         "type":"vehicle",
    #         "latitude": vehicle["latitude"],
    #         "longitude": vehicle["longitude"],
    #         "radius": 2,
    #         "capacity": vehicle["capacity"],
    #         "value": vehicle["value"],
    #         "percent_level": vehicle["percent_level"]
    #     })
    # for dumpster in result.dumpster_states():
    #     all_data.append({
    #         "timestamp": dumpster["timestamp"],
    #         "uid": dumpster["uid"],
    #         "type":"dumpster",
    #         "latitude": dumpster["latitude"],
    #         "longitude": dumpster["longitude"],
    #         "radius": 10,
    #         "capacity": dumpster["capacity"],
    #         "value": dumpster["value"],
    #         "percent_level": dumpster["percent_level"]
    #     })
    # save_to_csv(path / "all.csv", sorted(all_data, key=lambda x: x['timestamp']))
