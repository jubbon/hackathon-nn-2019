#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
from pathlib import Path

from loguru import logger
import geocoder


def normalize_address(address):
    ''' Выполняет нормализацию адреса
    '''
    parts = {}
    for address_part in address.split(","):
        address_part = address_part.strip()
        if re.fullmatch("\\d{6}", address_part):
            parts["postal_index"] = address_part
        elif address_part.startswith("обл "):
            parts["region"] = {
                "type": "область",
                "value": address_part.replace("обл ", "")
            }
        elif address_part.startswith("край "):
            parts["region"] = {
                "type": "край",
                "value": address_part.replace("край ", "")
            }
        elif address_part.startswith("Респ "):
            parts["region"] = {
                "type": "республика",
                "value": address_part.replace("Респ ", "")
            }
        elif address_part.startswith("г "):
            parts["city"] = {
                "type": "город",
                "value": address_part.replace("г ", "")
            }
        elif address_part.startswith("п ЗАТО п. "):
            parts["city"] = {
                "type": "поселок",
                "value": address_part.replace("п ЗАТО п. ", "")
            }
        elif address_part.startswith("ул "):
            parts["street"] = {
                "type": "улица",
                "value": address_part.replace("ул ", "")
            }
        elif address_part.startswith("пр-кт "):
            parts["street"] = {
                "type": "проспект",
                "value": address_part.replace("пр-кт ", "")
            }
        elif address_part.startswith("б-р "):
            parts["street"] = {
                "type": "бульвар",
                "value": address_part.replace("б-р ", "")
            }
        elif address_part.startswith("ш "):
            parts["street"] = {
                "type": "шоссе",
                "value": address_part.replace("ш ", "")
            }
        elif address_part.startswith("тракт "):
            parts["street"] = {
                "type": "тракт",
                "value": address_part.replace("тракт ", "")
            }
        elif address_part.startswith("тупик "):
            parts["street"] = {
                "type": "тупик",
                "value": address_part.replace("тупик ", "")
            }
        elif address_part.startswith("линия "):
            parts["street"] = {
                "type": "линия",
                "value": address_part.replace("линия ", "")
            }
        elif address_part.startswith("сл "):
            parts["street"] = {
                "type": "слобода",
                "value": address_part.replace("сл ", "")
            }
        elif address_part.startswith("мкр "):
            parts["street"] = {
                "type": "микрорайон",
                "value": address_part.replace("мкр ", "")
            }
        elif address_part.startswith("пр-д "):
            parts["street"] = {
                "type": "проезд",
                "value": address_part.replace("пр-д ", "")
            }
        elif address_part.startswith("проезд "):
            parts["street"] = {
                "type": "проезд",
                "value": address_part.replace("проезд ", "")
            }
        elif address_part.startswith("пл "):
            parts["street"] = {
                "type": "площадь",
                "value": address_part.replace("пл ", "")
            }
        elif address_part.startswith("пер "):
            parts["street"] = {
                "type": "переулок",
                "value": address_part.replace("пер ", "")
            }
        elif address_part.startswith("д. "):
            parts["house"] = {
                "type": "дом",
                "value": address_part.replace("д. ", "")
            }
        elif address_part.startswith("к. "):
            parts["building"] = {
                "type": "корпус",
                "value": address_part.replace("к. ", "")
            }
        elif address_part.startswith("стр. "):
            parts["building"] = {
                "type": "строение",
                "value": address_part.replace("стр. ", "")
            }
        else:
            raise RuntimeError(
                f"Unknown address part '{address_part}' for '{address}'")
    return parts


def geocode_address(address, provider):
    ''' Выполняет геокодирование адреса
    '''
    logger.info(f"Geocoding address '{address}'...")
    if provider == "yandex":
        geo = geocoder.yandex(location=address, lang="ru-RU", kind="house")
    elif provider == "osm":
        url = os.getenv("NOMINATIM_URL")
        address_norm = normalize_address(address)
        address_parts = [
            address_norm["city"]["value"],
            "{} {}".format(address_norm["street"]["type"], address_norm["street"]["value"]),
            address_norm["house"]["value"],
        ]
        if "building" in address_norm:
            address_parts.append(address_norm["building"]["value"])
        address = ", ".join(address_parts)
        geo = geocoder.osm(location=address, url=url)
    else:
        logger.warning(f"Unknown geocoder provider '{provider}'")
        return
    logger.debug(geo)
    data = geo.json
    assert isinstance(data, dict)
    data.update(provider=provider)
    return data


def geocode_houses(provider, input_filename, output_filename, encoding="utf-8", force=False):
    '''
    '''
    data = Path(input_filename).read_text(encoding=encoding)
    houses = json.loads(data)
    assert isinstance(houses, list)

    def save(data, encoding):
        '''
        '''
        data = json.dumps(data, ensure_ascii=False, indent=4)
        Path(output_filename).write_text(data, encoding=encoding)

    try:
        data = Path(output_filename).read_text(encoding=encoding)
        geo = json.loads(data)
    except FileNotFoundError:
        geo = dict()
    assert isinstance(geo, dict)

    try:
        for n, house in enumerate(houses):
            address = house["address"]
            address_fullname = address["fullname"]
            if address_fullname not in geo or force:
                try:
                    address_geo = geocode_address(address_fullname, provider)
                    geo[address_fullname] = address_geo
                except Exception as err:
                    logger.error(err)
                    # break
            else:
                logger.debug(f"Skipping geocode for '{address_fullname}'")
            if n % 100 == 0:
                save(geo, encoding=encoding)
    finally:
        save(geo, encoding=encoding)


def main():
    '''
    '''
    force = False
    provider = os.getenv("GEOCODER_PROVIDER")
    if provider:
        geocode_houses(
            provider=provider,
            input_filename="/data/gis.json",
            output_filename=f"/data/geo.{provider}.json",
            force=force
        )
    else:
        logger.error(f"No geocodef provider defined")
