#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime

import geojson
from loguru import logger
from h3 import h3
from invoke import task


def load_from_json(filename, encoding="utf-8"):
    ''' Загружает JSON-файл
    '''
    if filename.is_file():
        data = filename.read_text(encoding="utf-8")
        return json.loads(data)


@task
def calc_population(ctx, path, total_population, resolution):
    ''' Высчитывает количество людей, проживающее в отдельной области
    '''
    geo_osm = load_from_json(Path(path) / "geo.osm.json")
    assert isinstance(geo_osm, dict), f"geo_osm has type '{type(geo)}'"

    houses = load_from_json(Path(path) / "gis.json")
    assert isinstance(houses, list), f"houses has type '{type(houses)}'"

    h3_areas = dict()

    total_houses_area = 0.0
    for house in houses:
        try:
            house_area = house["Общая площадь жилых помещений"]
            house_area = house_area.replace(" м2", "").replace(",", ".")
            # logger.debug(house_area)
            if house_area:
                house_area = float(house_area)
            else:
                house_area = 0
        except KeyError:
            house_area = 0

        address = house["address"]["fullname"]
        if address in geo_osm:
            total_houses_area += house_area
            latitiude = geo_osm[address]["lat"]
            longitude = geo_osm[address]["lng"]
            h3_address = h3.geo_to_h3(latitiude, longitude, int(resolution))
            if h3_address in h3_areas:
                h3_areas[h3_address] = h3_areas[h3_address] + house_area
            else:
                h3_areas[h3_address] = house_area

    features = list()
    counted_total_population = 0
    for h3_address, h3_area in h3_areas.items():
        percent_population = h3_area*1.0 / total_houses_area
        population = round(percent_population * int(total_population))
        counted_total_population += population

        geometry = geojson.Polygon(
            [h3.h3_to_geo_boundary(
                h3_address=h3_address,
                geo_json=True)]
        )
        feature = geojson.Feature(
            geometry=geometry,
            id=h3_address,
            properties={
                "h3_address": h3_address,
                "population": population,
                "total_population": total_population,
                "percent_population": round(percent_population*100, 1)
            }
        )
        features.append(feature)
    features.sort(key=lambda feature: feature["id"])
    feat_collection = geojson.FeatureCollection(features)
    print(geojson.dumps(feat_collection, indent=4))
    logger.debug(f"Total population: {counted_total_population}")


@task
def make_migration(ctx, filename):
    '''
    '''
    now = datetime.now()
    with open(filename, mode="rt") as f:
        while True:
            data = f.readline()
            if data:
                dt, h3_address_from, h3_address_to, people_count = data.split(",")
                time_offset = datetime.strptime(dt, "%H:%M")
                time_offset = now.replace(hour=time_offset.hour, minute=time_offset.minute)
                timestamp = round(time_offset.timestamp())
                coords_from = h3.h3_to_geo(h3_address_from)
                coords_to = h3.h3_to_geo(h3_address_to)
                fields = [timestamp, *coords_from, *coords_to, people_count]
                print(",".join([str(f) for f in fields]))
            else:
                break
