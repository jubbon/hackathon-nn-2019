#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import aiohttp
import asyncio
import async_timeout

from loguru import logger

from storage import storage
from map import MapContext


async def api(query, map_context, extra_params=None, timeout=5, interval=15):
    '''
    '''
    base_url = "https://yandex.ru/maps/api/masstransit"
    headers = {
        'authority': 'yandex.ru',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': f'https://yandex.ru/maps/{map_context.region_uid}/{map_context.city}/?l=masstransit&ll={map_context.ll}&z=12',
        'Cache-Control': 'no-cache',
        'x-relpath-y': f'https://yandex.ru/maps/{map_context.region_uid}/{map_context.city}/?l=masstransit&ll={map_context.ll}&z=12',
        'cookie': 'maps_los=1; mda=0; bltsr=1; _ym_uid=15392036931063700574; ys_fp=form-requestid%3D1542630967341969-437346063404833501211166-man1-3614; my=Yy4BAQA=; font_loaded=YSv1; yandexuid=953446291539203684; yandex_login=kulikov.dmitry.1980; L=QU9iVV4FAERAZGpbRlxWRlpOAl1wcUBfBzZVUAw+RFgmXh0aMTxtf09gZQ==.1561612906.13909.323428.3a7bc55eb9a2250da090c1455f3e1597; KIykI=1; yandex_gid=11083; i=ngqNHbHO+w6vBVymDU2RO5RuQE5x5WBE6cSDk1XK4K/zxJq+KffhKtTcCCL2ummIR1DnZMiK/3reqR+cTn3I1wn8fw4=; ys=diskchrome.8-22-3#udn.cDrQmtGD0LvQuNC60L7QsiAg0JTQvNC40YLRgNC40Lk%3D#ymrefl.4C4E65820092A07A#wprid.1562302774355274-1369178222406513060200035-vla1-0241; Session_id=3:1563121813.5.0.1539203705568:G2XMHw:87.1|122224395.0.2|1130000021848514.2315863.2.2:2315863|252039578.2832422.2.2:2832422|1130000036028374.7461374.2.2:7461374|1130000037816072.14556677.2.2:14556677|202136.440475.7eZvZX83HRjVtM6k43L5VE-s7lY; sessionid2=3:1563121813.5.0.1539203705568:G2XMHw:87.1|122224395.0.2|1130000021848514.-1.0|252039578.-1.0|1130000036028374.-1.0|1130000037816072.-1.0|202136.698280.yR5VrUQ4bvjje41lF3dxKyZf6aY; EIXtkCTlX=1; _ym_isad=1; zm=m-white_bender.webp.css-https%3Awww_670DT4M4ktA5vI566aB-X9yVf0o%3Al; _ym_d=1563163355; yabs-frequency=/4/00010000001whWnT/Y8HoS6Ws8Hg-FMreDYVRIx1mQ3OW/; yp=1594699355.nt.computers#1578931360.szm.1%3A1920x1080%3A1920x958#1563349626.gpauto.61_52401%3A105_318756%3A2793956%3A3%3A1563176826'
    }

    url = "/".join((base_url, query))
    params = dict(
        ajax=1,
        locale='ru_RU',
        csrfToken=map_context.csrfToken,
        sessionId=map_context.sessionId,
    )
    if extra_params:
        params.update(**extra_params)
    while True:
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                logger.debug(f"Fetching data from '{url}', params={params}")
                data = await fetch(
                    session=session,
                    url=url,
                    params=params,
                    timeout=timeout
                )
                yield data["data"]
        except asyncio.TimeoutError:
            logger.error(f"Timeout {timeout} seconds for '{url}'")
        except Exception as err:
            logger.error(f"{err}")

        logger.info(f"Sleeping for {interval} seconds...")
        await asyncio.sleep(interval)


async def fetch(session, url, params, timeout=5):
    '''
    '''
    async with async_timeout.timeout(timeout):
        async with session.get(url, params=params) as response:
            return await response.json(content_type=None)


async def fetch_routes(storage, map_context, interval=15):
    ''' Собирает информацию о маршрутах общественного транспорта
    '''
    assert storage
    assert map_context

    while True:
        for route_uid, route in storage._routes.items():
            if "features" in route:
                # Геометрия маршрута уже получена
                continue

            logger.info(f"Fetching route {route_uid}")
            lineId, threadId = route_uid.split(".")
            extra_params = dict(
                lineId=lineId,
                skipApplyBounds="true",
                threadId=threadId,
            )
            gen = api("getLine", map_context, extra_params)
            async for data in gen:
                if data is None:
                    logger.warning("data is empty")
                assert isinstance(data, dict), f"{data} is {type(data)}"
                features = data["activeThread"]
                if "MapsUIMetaData" in features:
                    del features["MapsUIMetaData"]
                for feature in features["features"]:
                    if "properties" not in feature:
                        feature["properties"] = dict()
                    else:
                        properties = feature["properties"]
                        if "currentTime" in properties:
                            del properties["currentTime"]
                storage._routes.setdefault(route_uid, {}).update(features=features)
                storage.save_routes(route_uid)
                break
            break
        logger.info(f"Waiting for {interval} seconds...")
        await asyncio.sleep(interval)


async def fetch_vehicles(storage, map_context):
    ''' Получает отметки о положении автобусов
    '''
    assert storage
    assert map_context

    extra_params = dict(
        ll=map_context.ll,
        spn=map_context.spn,
        lang='ru'
    )
    gen = api("getVehiclesInfoWithRegion", map_context, extra_params)
    calls = 0
    async for data in gen:
        if data is None:
            continue
        assert isinstance(data, dict), f"{data} is {type(data)}"
        vehicles = data["vehicles"]
        # Текущее время
        now = datetime.now()
        for vehicle in vehicles:
            assert isinstance(vehicle, dict)
            logger.debug(vehicle["properties"]["VehicleMetaData"])

            vehicle_info = vehicle["properties"]["VehicleMetaData"]["Transport"]
            vehicleId = vehicle_info["id"]
            lineId = vehicle_info["lineId"]
            threadId = vehicle_info["threadId"]
            route_uid = ".".join((lineId, threadId))
            route_ref = vehicle_info["name"]
            route_type = vehicle_info["type"]
            storage._routes.setdefault(route_uid, {}).update(route_uid=route_uid,
                                                    route_ref=route_ref,
                                                    route_type=route_type)

            trace_line = storage._traces.setdefault(f"{now:%Y%m%d}", {}).setdefault(lineId, {})
            trace_line.update(route_ref=route_ref, route_type=route_type)
            trace_line.\
                setdefault("intervals", {}).\
                setdefault(now.hour, set()).\
                add(vehicleId)
        calls += 1
        if calls % 50:
            storage.save_traces()

        logger.info(f"Total routes: {len(storage._routes)}")


def main():
    '''
    '''
    root = "/data"
    with storage(root) as s:
        map_context = MapContext()
        loop = asyncio.get_event_loop()
        loop.create_task(fetch_vehicles(s, map_context))
        loop.create_task(fetch_routes(s, map_context))
        loop.run_forever()
        loop.close()
        logger.info("Close")
