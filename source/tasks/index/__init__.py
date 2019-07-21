#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from h3 import h3

import geojson

from invoke import task

from .. import logger


@task
def split_region(ctx, resolution):
    '''
    '''
    data = "".join(sys.stdin.readlines())
    data = geojson.loads(data)
    geometry = data.geometry
    indexes = h3.polyfill(geo_json=geometry,
                          res=int(resolution),
                          geo_json_conformant=True)
    for index in sorted(indexes):
        print(index)


@task
def indexes_to_geojson(ctx):
    '''
    '''
    data = sys.stdin.readlines()
    indexes = [index.replace('\n', '') for index in data]
    features = []
    for index in indexes:
        if not index:
            continue
        geometry = geojson.Polygon(
            [h3.h3_to_geo_boundary(
                h3_address=index,
                geo_json=True)]
        )
        logger.debug(f"geometry for '{index}': {geometry}")
        feature = geojson.Feature(geometry=geometry,
                                  id=index,
                                  properties={"index": index})
        features.append(feature)
    features.sort(key=lambda feature: feature["id"])
    feat_collection = geojson.FeatureCollection(features)
    print(geojson.dumps(feat_collection, indent=4))
