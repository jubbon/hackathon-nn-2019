#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path

import geojson
from h3 import h3
from invoke import task
from loguru import logger


def load_from_json(filename, encoding="utf-8"):
    ''' Загружает JSON-файл
    '''
    if filename.is_file():
        data = filename.read_text(encoding="utf-8")
        if data:
            return json.loads(data)


@task
def create_environment(ctx, path, resolution, output_format="json"):
    ''' Создает файл в формате JSON с описанием окружения
    '''
    environment = dict()

    # Загрузка регионов
    filename = Path(path) / "region" / f"indexes.{resolution}.geojson"
    if not filename.is_file():
        logger.error(f"File {filename} not found")
        return
    data = load_from_json(filename)
    if not data:
        logger.error(f"File {filename} is empty")
        return
    assert isinstance(data, dict)
    for feature in data["features"]:
        properties = feature["properties"]
        h3_address = properties["index"]
        environment[h3_address] = {
            "population": 0,
            "infrastructure": {
                "home": 0.0,
                "mall": 0.0,
                "education": 0.0,
                "health": 0.0,
                "industrial": 0.0,
                "commercial": 0.0,
                "sport": 0.0,
                "entertaiment": 0.0,
                "attractions": 0.0,
                "transport": 0.0
            }
        }

    # Загрузка количества жителей
    populations = dict()
    home_areas = dict()
    data = load_from_json(Path(path) / "houses" / f"population.{resolution}.geojson")
    assert isinstance(data, dict)
    total_population = 0
    for feature in data["features"]:
        properties = feature["properties"]
        h3_address = properties["h3_address"]
        populations[h3_address] = properties["population"]
        home_areas[h3_address] = properties["percent_population"]
        total_population += populations[h3_address]

    poi_path = Path(path) / "infrastructure"
    pois = dict()

    for feature in data["features"]:
        properties = feature["properties"]
        h3_address = properties["h3_address"]
        environment.setdefault(h3_address, {})["population"] = populations.get(h3_address, 0)
        environment.setdefault(h3_address, {})["infrastructure"] = {
            "home": round(home_areas.get(h3_address, 0), 2),
            "mall": 0.0,
            "education": 0.0,
            "health": 0.0,
            "industrial": 0.0,
            "commercial": 0.0,
            "sport": 0.0,
            "entertaiment": 0.0,
            "attractions": 0.0,
            "transport": 0.0
        }

    for filename_poi in poi_path.iterdir():
        logger.debug(f"Processing {filename_poi}")
        data = load_from_json(filename_poi)
        assert isinstance(data, dict)
        for rank, poi in enumerate(data["features"], 1):
            longitude = latitude = None
            properties = poi["properties"]
            company = properties["CompanyMetaData"]
            geometry = poi["geometry"]
            if geometry["type"] == "Point":
                coordinates = geometry["coordinates"]
                longitude, latitude = coordinates
            else:
                logger.warning(f"{geometry['type']}")
            h3_address = h3.geo_to_h3(latitude, longitude, int(resolution))
            categories = [cat['class'] for cat in company["Categories"] if 'class' in cat]

            for category in categories:
                environment.setdefault(h3_address, {}).setdefault("poi", []).append({
                    "name": company["name"],
                    "address": company["address"],
                    "category": category,
                    "rank": rank
                })

                if category in ("malls", ):
                    category = "mall"
                elif category in ("university", "theater education",
                                    "scientific organization", "college",
                                    "school", "further education",
                                    "theological school",
                                    "educational center"):
                    category = "education"
                elif category in ("theatre", "night club", "cinemas",
                                    "spa", "beauty", "restaurants",
                                    "entertainments", "musicclub",
                                    "concert hall", "cafe", "bars",
                                    "events hall", "karaoke",
                                    "cultural center", "amusement"):
                    category = "entertaiment"
                elif category in ("industrial enterprise", "haulier", "building materials"):
                    category = "industrial"
                elif category in ("railway terminal", "railway station",
                                    "airports", "travel"):
                    category = "transport"
                elif category in ("online store", "gastro market",
                                    "food market", "clothes shop",
                                    "accountants", "legal services",
                                    "real estate", "furniture store",
                                    "exhibition center", "doors", "tailor",
                                    "finishing works", "greengrocery",
                                    "office"):
                    category = "commercial"
                elif category in ("fitness", "skating rink",
                                    "climbing wall", "stadium",
                                    "swimming pool", "market", "supermarket",
                                    "sport school"):
                    category = "sport"
                elif category in ("massage", "medicine", "sportcenter",
                                    "center health", "emergency", "dental",
                                    "private practitioners"):
                    category = "health"
                elif category in ("orthodox church", "mosque", "museum"):
                    category = "attractions"
                value_dict = environment.setdefault(h3_address, {})["infrastructure"] = {
                    "home": round(home_areas.get(h3_address, 0), 2),
                    "mall": 0.0,
                    "education": 0.0,
                    "health": 0.0,
                    "industrial": 0.0,
                    "commercial": 0.0,
                    "sport": 0.0,
                    "entertaiment": 0.0,
                    "attractions": 0.0,
                    "transport": 0.0
                }
                current_value = value_dict[category]
                value_dict[category] = current_value + 1
                pois.setdefault(category, list()).append(poi)

    if output_format == "json":
        for h3_address, desc in environment.items():
            infrastructure = desc["infrastructure"]
            for category, count in infrastructure.items():
                try:
                    infrastructure[category] = round(count / len(pois[category]) *
                                                    100, 1)
                except KeyError:
                    pass
        print(json.dumps(environment, ensure_ascii=False, indent=4))
    elif output_format == "geojson":
        features = []
        for h3_address, desc in environment.items():
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
                    "population": desc.get("population", 0),
                    "infrastructure": desc.get("infrastructure", {}),
                    "poi": desc.get("pois", {})
                }
            )
            features.append(feature)
        features.sort(key=lambda feature: feature["id"])
        feat_collection = geojson.FeatureCollection(features)
        print(geojson.dumps(feat_collection, indent=4))
    else:
        logger.error(f"Unknown output format {output_format}")


@task
def check_environment(ctx, filename):
    ''' Выполняет проверку окружения
    '''
    filename = Path(filename)
    if not filename.is_file():
        logger.error(f"File {filename} not found")
        return
    data = load_from_json(filename)
    if not data:
        logger.error(f"File {filename} is empty")
        return

    assert isinstance(data, dict)
    total_population = 0
    total_features = 0
    if "features" in data:
        for feature in data["features"]:
            properties = feature["properties"]
            population = properties["population"]
            total_population += population
            total_features += 1
    else:
        for h3_address, feature in data.items():
            population = feature.get("population", 0)
            total_population += population
            total_features += 1
    print(f"Total features: {total_features}")
    print(f"Total population: {total_population}")