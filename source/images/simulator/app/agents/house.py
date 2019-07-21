#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from datetime import datetime


class House():
    ''' Дом
    '''

    emission_probabilty_by_hours = {
        0: 0, 1: 0, 2: 0, 3: 0, 4: 0.02, 5: 0.05, 6: 0.1,
        7: 0.15, 8: 0.11, 9: 0.08, 10: 0.05, 11: 0.03,
        12: 0.02, 13: 0.02, 14: 0.02, 15: 0.02, 16: 0.03, 17: 0.05,
        18: 0.1, 19: 0.07, 20: 0.05, 21: 0.03, 22: 0, 23: 0
    }

    def __init__(self, env, uid, latitude, longitude, dumpster_uid, daily_emission):
        self.env = env
        # Уникальный идентификатор дома
        self.uid = uid
        # Широта
        self.latitude = latitude
        # Долгота
        self.longitude = longitude
        # Идентификатор мусорной площадки
        self.dumpster_uid = dumpster_uid
        # Ежедневная норма генерации мусора
        self.daily_emission = daily_emission
        # Текущий объем сгенерированного мусора
        self.current_emission = 0
        # Суммарный объём сгенерированного мусора
        self.total_emission = 0

        assert round(sum([v for k, v in self.emission_probabilty_by_hours.items()]), 1) == 1.0

        self.action = env.process(self.run())

    @property
    def state(self):
        '''
        '''
        return dict(
            timestamp=self.env.now,
            uid=self.uid,
            latitude=self.latitude,
            longitude=self.longitude,
            dumpster_uid=self.dumpster_uid,
            current_emission=round(self.current_emission, 2),
            total_emission=round(self.total_emission, 2),
        )

    def callback(self, event):
        '''
        '''
        self.env.set_house_state(self.state)

    def run(self, min_timeout=60, max_timeout=600):
        '''
        '''
        while True:
            timeout = int(random.uniform(min_timeout, max_timeout))
            yield self.env.timeout(timeout)

            # Закидывание мусора в контейнер
            try:
                dt = datetime.fromtimestamp(self.env.now)
                probability = self.emission_probabilty_by_hours.get(dt.hour, 0) / (3600.0 / timeout)
                self.current_emission = round(
                    random.uniform(self.daily_emission * probability * 0.8,
                                   self.daily_emission * probability * 1.2), 2)
                if self.current_emission:
                    dumpster = self.env.get_dumpster(self.dumpster_uid)
                    # if self.env.debug:
                    #     print(f"[{self.env.now}] {dt} Pushing garbage {self.current_emission} from '{self.uid}' to container '{self.dumpster_uid}'. Already: {dumpster.value}", flush=True)

                    p = self.env.process(dumpster.add(self.current_emission))
                    p.callbacks.append(self.callback)
                    yield p
                    self.total_emission += self.current_emission
            except KeyError:
                if self.env.debug:
                    print(f"Container '{self.dumpster_uid}' not found", flush=True)
