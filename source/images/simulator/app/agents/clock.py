#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from loguru import logger


class Clock():
    '''
    '''
    def __init__(self, env, interval):
        self.env = env
        self.interval = interval
        self.action = env.process(self.run())

    def gen_data(self, now, f):
        '''
        '''
        while True:
            data = f.readline()
            if data:
                dt, h3_address_from, h3_address_to, people_count = data.split(",")
                time_offset = datetime.strptime(dt, "%H:%M")
                time_offset = now.replace(hour=time_offset.hour, minute=time_offset.minute)
                if time_offset <= now:
                    yield {
                        "time_offset": time_offset,
                        "h3_address_from": h3_address_from,
                        "h3_address_to": h3_address_to,
                        "people_count": people_count
                    }
                else:
                    break

    def run(self):
        '''
        '''
        with open("/data/playbooks/example.csv", mode="rt") as f:
            while True:
                now = datetime.fromtimestamp(self.env.now)
                for data in self.gen_data(now, f):
                    h3_address_from = data["h3_address_from"]
                    h3_address_to = data["h3_address_to"]
                    people_count = data["people_count"]
                    self.env.area(h3_address_from).emit(h3_address_to, people_count)
                yield self.env.timeout(self.interval)
