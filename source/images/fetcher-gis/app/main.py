#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
from pathlib import Path
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from openpyxl import load_workbook
from openpyxl import Workbook

from loguru import logger

from storage import handle_brief
from storage import handle_passport
from storage import handle_company


store = {}


def is_need_data(region, address, data_type):
    '''
    '''
    return True
    directory = os.path.join(*[part.strip() for part in address.split(",")])
    path = Path(f"/data/{directory}")
    f = path / f"{data_type}.json"
    if not f.exists():
        return True
    return False

    # for _, house in store.items():
    #     meta = house["meta"]
    #     if address != meta["address"]:
    #         continue
    #     if "brief" not in house:
    #         return False
    #     if "passport" not in house:
    #         return False
    #     return True
    # return False


@contextmanager
def open_link_in_new_tab(browser, link_element, before_switch_hook=None):
    '''
    Запускает отдельную вкладку браузера и выполняет действия в ней
    '''
    # Save the window opener (current window, do not mistaken with tab... not the same)
    main_window = browser.current_window_handle

    # Create new tab
    actions = ActionChains(browser)
    actions.move_to_element(link_element).key_down(Keys.CONTROL).click(link_element).key_up(Keys.CONTROL).perform()

    if before_switch_hook:
        before_switch_hook(browser)

    # Переключение на созданную вкладку
    browser.switch_to.window(browser.window_handles[1])
    try:
        yield browser
    finally:
        # Close tab
        browser.close()
        # Put focus on current window which will be the window opener
        browser.switch_to_window(main_window)


def get_brief_data(address, browser, link_element, timeout=30):
    ''' Получает краткую информацию о доме
    '''
    data = {}
    with open_link_in_new_tab(browser, link_element) as tab:
        try:
            wait = WebDriverWait(tab, timeout)
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, "form-base__form-value"),
                    "Тип дома"
                )
            )

            for table in browser.find_elements_by_class_name("register-card__table"):
                for row in table.find_elements_by_xpath("tbody/tr"):
                    attr_name = row.find_element_by_xpath("td[1]").text
                    attr_name = attr_name.replace(":", "")

                    attr_value = row.find_element_by_xpath("td[2]").text
                    attr_value = "" if attr_value == "-" else attr_value

                    data[attr_name] = attr_value
        except Exception as err:
            pass
            # tab.save_screenshot(f"/data/screenshots/brief {address}.png")
            # raise
    return data


def get_company(address, browser, link_element, timeout=30):
    ''' Получает информацию об исполнителях услуг в доме
    '''
    data = {}
    with open_link_in_new_tab(browser, link_element) as tab:
        try:
            wait = WebDriverWait(tab, timeout)
            wait.until(
                EC.text_to_be_present_in_element((
                    By.CLASS_NAME, "_word-break_all"),
                    "Информация об организации"
                )
            )

            for table in browser.find_elements_by_class_name("info-card__table"):
                for row in table.find_elements_by_xpath("tbody/tr"):
                    try:
                        attr_name = row.find_element_by_xpath("td/div/div[1]").text
                        attr_value = row.find_element_by_xpath("td/div/div[2]").text
                        data[attr_name] = attr_value
                    except NoSuchElementException:
                        pass
        except Exception as err:
            tab.save_screenshot(f"/data/screenshots/company {address}.png")
            raise
    return data


def get_passport(address, browser, link_element, timeout):
    ''' Получает электронный папорт дома
    '''
    def before_switch_hook(browser, timeout):
        '''
        Подтверждение формирования электронного паспорта дома
        '''
        wait = WebDriverWait(browser, timeout)
        elem = wait.until(
            EC.visibility_of_element_located(
            (By.CLASS_NAME, "btn-action"))
        )
        elem.click()
        WebDriverWait(browser, timeout).until(EC.staleness_of(elem))

    data = {}

    from functools import partial
    before_switch_hook = partial(before_switch_hook, timeout=timeout)

    with open_link_in_new_tab(browser, link_element, before_switch_hook) as tab:
        try:
            wait = WebDriverWait(tab, timeout)
            wait.until(
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, "form-base__control-label"), "Дата формирования электронного паспорта"
                )
            )

            table = tab.find_element_by_class_name("attr-body-content")
            if table:
                for row in table.find_elements_by_xpath("table/tbody/tr"):
                    attr_name = row.find_element_by_xpath("td//label").text
                    for prefix in (
                            "2.2",
                            "2.3",
                            "2.4",
                            "2.5",
                            "2.6",
                            "2.7",
                            "2.8",
                            "2.9.1",
                            "2.9.2",
                            "2.10",
                            "2.11",
                            "2.12",
                            "2.13",
                            "2.14",
                            "2.15.1",
                            "2.15.2",
                            "2.15.3",
                            "2.15",
                            "2.16",
                            "2.17",
                    ):
                        if attr_name.startswith("{}.".format(prefix)):
                            attr_name = attr_name.replace("{}.".format(prefix), "")
                            attr_name = attr_name.replace(":", "").strip()

                            attr_value = row.find_element_by_xpath("td[last()]").text

                            if attr_value:
                                data[attr_name] = attr_value
                            break
        except Exception as err:
            tab.save_screenshot(f"/data/screenshots/passport {address}.png")
            raise
    return data


def houses(region, data_types, filter_list, skip=None):
    '''
    Генератор, возвращающий информацию о жилых домах
    '''
    assert isinstance(region, (list, tuple))
    assert len(region) == 2
    region_uid, region_name = region

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.set_window_size(1920, 1024)
    browser.maximize_window()
    browser.get("https://dom.gosuslugi.ru/#!/houses")

    browser.find_element_by_link_text("Поиск дома по ОМС").click()
    browser.implicitly_wait(10)  # seconds
    browser.find_element_by_class_name("select2-container").click()
    elem = browser.find_element_by_class_name("select2-search")
    elem2 = elem.find_element_by_xpath("input")
    elem2.send_keys(region_name)

    wait = WebDriverWait(browser, 60)
    wait.until(
        EC.text_to_be_present_in_element(
            (By.CLASS_NAME, "select2-result-label"), region_name))
    elem2.send_keys(Keys.ENTER)

    browser.find_element_by_xpath("//button[contains(.,'Найти')]").click()

    wait.until(
        EC.text_to_be_present_in_element((By.XPATH, '//h4'), "Всего записей")
    )

    # Установка максимально возможного количества домов на одной странице
    try:
        next_page = browser.find_element_by_xpath("//a/span[text()='следующая']")
        select_count = browser.find_element_by_id("count")
        for option in select_count.find_elements_by_tag_name('option'):
            pass
        logger.info(f"Setting {option.text} houses per page...")
        option.click()
        wait = WebDriverWait(browser, 20)
        class_name = "preloader"
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, class_name)))
    except NoSuchElementException:
        # Весь список домов помещается на одной странице
        pass

    count = 0
    while True:
        for elem in browser.find_elements_by_class_name("register-card"):
            count += 1
            if skip and count <= skip:
                logger.warning(f"[{count}] Skipping already available house")
                continue
            try:
                # Адрес дома
                address = elem.find_element_by_xpath("div/span[@class='house-card-address pull-left']").text

                # Фильтрация адреса
                if filter_list and not any(map(lambda s: s in address, filter_list)):
                    logger.warning(f"[{count}] Skipping address '{address}'...")
                    continue
                logger.info(f"[{count}] Processing address '{address}'...")

                data = dict(
                    address=dict(
                        fullname=address
                    )
                )

                timeout = 20
                if is_need_data(region_uid, address, "brief"):
                    try:
                        # Ссылка на краткую информацию о доме
                        link_element = elem.find_element_by_link_text("Сведения об объекте жилищного фонда")
                        brief = get_brief_data(address, browser, link_element, timeout=timeout)
                        if brief:
                            data.update(brief=brief)
                    except Exception as err:
                        logger.error(f"{err}")
                else:
                    logger.warning(f"[{count}] Skipped brief")

                # if is_need_data(region_uid, address, "company"):
                #     try:
                #         # Ссылка на управляющую компанию
                #         link_element = elem.find_element_by_link_text("Информация об исполнителях услуг")
                #         company = get_company(address, browser, link_element, timeout=timeout)
                #         if company:
                #             data.update(company=company)
                #     except Exception as err:
                #         logger.error(f"{err}")
                #         data.update(company={})
                # else:
                #     logger.warning(f"[{count}] Skipped company")

                # if is_need_data(region_uid, address, "passport"):
                #     try:
                #         # Ссылка на электронный паспорт дома
                #         link_element = elem.find_element_by_link_text("Электронный паспорт дома")
                #         passport = get_passport(address, browser, link_element, timeout=timeout)
                #         if passport:
                #             data.update(passport=passport)
                #     except Exception as err:
                #         logger.error(f"{err}")
                # else:
                #     logger.warning(f"[{count}] Skipped passport")

                yield data
            except Exception as err:
                logger.error(f"[{count}] Error: {err}")

        # Переход к следующей партии домов
        try:
            next_page = browser.find_element_by_xpath("//a/span[text()='следующая']")
            next_page.click()
            WebDriverWait(browser, 60).until(EC.staleness_of(elem))
        except NoSuchElementException:
            # Обработан весь список домов
            break

    browser.quit()


def fetcher_from_gis(region, filter_list=None):
    ''' Загружает данные по жилым домам
    '''
    assert isinstance(region, (list, tuple))
    assert len(region) == 2
    region_uid, region_name = region

    available_houses = list()
    filename = Path("/data/gis.json")
    try:
        with open(filename, mode="rt") as f:
            available_houses = json.loads(f.read())
    except FileNotFoundError:
        pass

    available_house_uids = list()
    for house in available_houses:
        house_uid = house.get("Идентификационный код адреса", "")
        available_house_uids.append(house_uid)
    logger.info(f"Available {len(available_houses)} houses")

    data_types = ("brief", )
    # data_types = ("brief", "company", "passport")
    try:
        logger.info(f"Fetching data from dom.gosuslugi.ru for region '{region_name}'...")

        skip = len(available_houses)
        for n, house in enumerate(houses(region, data_types, filter_list, skip=skip), skip):
            if n % 50 == 0:
                data = json.dumps(available_houses, ensure_ascii=False, indent=4)
                filename.write_text(data, encoding="utf-8")

            address = house["address"]
            logger.info(f"Sending data from for region {address['fullname']}...")
            for data_type in data_types:
                if data_type in house:
                    data = {
                        "address": address,
                        data_type: house[data_type]
                    }
                    if data_type == "brief":
                        brief = house[data_type]

                        house_uid = brief.get("Идентификационный код адреса", "")
                        if house_uid and house_uid in available_house_uids:
                            continue

                        brief.update(address=address)
                        available_houses.append(brief)
                        # handle_brief(ws,
                        #     {
                        #         "region": region_uid,
                        #         "timestamp": time.time()
                        #     },
                        #     data
                        # )
                    elif data_type == "passport":
                        handle_passport(
                            {
                                "region": region_uid,
                                "timestamp": time.time()
                            },
                            data
                        )
                    elif data_type == "company":
                        handle_company(
                            {
                                "region": region_uid,
                                "timestamp": time.time()
                            },
                            data
                        )
    except Exception as err:
        logger.error(f"{err}")
        raise
    finally:
        data = json.dumps(available_houses, ensure_ascii=False, indent=4)
        filename.write_text(data, encoding="utf-8")
        # wb.save(filename)


def main():
    '''
    '''
    region_uid = os.getenv("REGION")
    assert region_uid is not None, "Не задана переменная окружения REGION"
    region_name = os.getenv("REGION_NAME")
    assert region_name is not None, "Не задана переменная окружения REGION_NAME"

    regions = ((region_uid, region_name), )
    logger.debug(regions)
    for region in regions:
        fetcher_from_gis(
            region=region,
            filter_list=os.getenv("FILTER_LIST", "").split(";"))
