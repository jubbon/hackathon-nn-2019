#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from dataclasses import dataclass


@dataclass
class MapContext:
    region_uid: int = int(os.getenv("YANDEX_MAP_REGION_UID"))
    city: str = os.getenv("YANDEX_MAP_CITY")
    map_bbox: str = os.getenv("YANDEX_MAP_BBOX")

    csrfToken: str = os.getenv("YANDEX_MAP_CSRF_TOKEN")
    sessionId: str = os.getenv("YANDEX_MAP_SESSION_ID")

    @property
    def ll(self):
        bbox_lb, bbox_rt = [p.split(",") for p in self.map_bbox.split("~")]
        return ",".join([
            str(round((float(bbox_rt[0]) + float(bbox_lb[0])) / 2, 5)),
            str(round((float(bbox_rt[1]) + float(bbox_lb[1])) / 2, 5))
        ])

    @property
    def spn(self):
        bbox_lb, bbox_rt = [p.split(",") for p in self.map_bbox.split("~")]

        return ",".join([
            str(round((float(bbox_rt[0]) - float(bbox_lb[0])) / 2, 5)),
            str(round((float(bbox_rt[1]) - float(bbox_lb[1])) / 2, 5))
        ])
