#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from invoke import task
import geojson

from .. import logger

from .overpass import api


OVERPASS_QUERY = '''
area[name="{region_name}"];
(
  node(area);
  <;
) -> .a;
(
  rel.a
    [name="{region_name}"]
    ["boundary"="administrative"]
    ;
);
(._;>;);
out;
'''


def nodes(result):
    '''
    '''
    ways = dict()
    for way in result.ways:
        nodes = way.get_nodes(resolve_missing=True)
        first_node = nodes[0].id
        last_node = nodes[-1].id
        # Прямой порядок
        ways.setdefault(first_node, {})[last_node] = nodes
        # Обратный порядок
        ways.setdefault(last_node, {})[first_node] = nodes[::-1]

    way_id = list(ways.keys())[0]
    prev_way_id = None
    while ways:
        logger.debug(f"Обрабатывается '{way_id}'")
        if way_id not in ways:
            logger.warning(f"{way_id} not found in ways")
            break
        way = ways.pop(way_id)
        next_ways = list(way.keys())
        logger.debug(f"next_ways: {next_ways}")
        for next_way_id in next_ways:
            if next_way_id == prev_way_id:
                continue
            for node in way[next_way_id]:
                yield node
            prev_way_id = way_id
            way_id = next_way_id
            break


@task
def boundary(ctx, region_name, debug=False):
    ''' Возвращает административную границу региона
    '''
    level = "DEBUG" if debug else "INFO"
    logger.remove(0)
    logger.add(sys.stderr, level=level)

    if not region_name:
        return
    result = api(
        query=OVERPASS_QUERY.format(region_name=region_name)
    )

    points = list()
    for node in nodes(result):
        longitude = float(node.lon)
        latitude = float(node.lat)
        points.append((longitude, latitude))

    feature = geojson.Feature(
        geometry=geojson.Polygon([points])
    )
    print(feature)
