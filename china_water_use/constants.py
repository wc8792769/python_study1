#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import itertools
import logging
from typing import Iterable, TypeAlias

from numpy import ndarray

logger = logging.getLogger("constants")

Cols: TypeAlias = Iterable[str]


def make_list(element, keep_none=False):
    """Turns element into a list of itself
    if it is not of type list or tuple."""
    if element is None:
        return None if keep_none else []
    if not isinstance(element, (list, tuple, set, ndarray)):
        element = [element]
    elif isinstance(element, (tuple, set)):
        element = list(element)

    return element


SUMMARY = {
    "Total water use": "总用水量",
    "IND": "工业总用水",
    "IRR": "灌溉总用水",
    "RUR": "农村总用水",
    "URB": "城市总用水",
}

SECTORS = {"IRR": "农业", "IND": "工业", "RUR": "农村", "URB": "城市"}

IRR = {
    "Rice": "水稻",
    "Wheat": "小麦",
    "Maize": "玉米",
    "Vegetables and fruits": "果蔬",
    "Others": "其它",
}
IRR_ITEMS = {
    "WUI": [f"Irrigation water-use intensity (WUI): {crop}" for crop in IRR],
    "WU": [f"Irrigation WU: {crop}" for crop in IRR],
    "Magnitude": [f"Irrigated area: {crop}" for crop in IRR],
}

IND = {
    "Textile": "纺织",
    "Papermaking": "造纸",
    "Petrochemicals": "石化",
    "Metallurgy": "冶金",
    "Mining": "采矿",
    "Food": "食品",
    "Cements": "水泥",
    "Machinery": "机械",
    "Electronics": "电子",
    "Thermal electrivity": "火电",
    "Others": "其它",
}
IND_ITEMS = {
    "Magnitude": [f"Industrial gross value added (GVA): {ind}" for ind in IND],
    "WUI": [f"Industrial WUI: {ind}" for ind in IND],
    "WU": [f"Industrial WU: {ind}" for ind in IND],
}

RUR = {
    "domestic": "人居",
    "livestock": "牲畜",
}
RUR_ITEMS = {
    "Magnitude": [f"Rural {rur} population" for rur in RUR],
    "WUI": [f"Rural {rur} WUI" for rur in RUR],
    "WU": [f"Rural {rur} WU" for rur in RUR],
}

URB = {
    "domestic": "人居",
    "service": "服务业",
}
URB_ITEMS = {
    "WU": ["Urban domestic WU", "Urban service WU"],
    "WUI": ["Urban domestic WUI", "Urban service WUI"],
    "Magnitude": ["Urban domestic population", "Urban service GVA"],
}

ITEMS = {
    "IRR": IRR_ITEMS,
    "IND": IND_ITEMS,
    "RUR": RUR_ITEMS,
    "URB": URB_ITEMS,
}

MEASUREMENTS = {
    "WUI": "用水强度",
    "WU": "用水量",
    "Magnitude": "体量",
}

GENERAL_COLUMNS = {
    "City_ID": "市",
    "Year": "年份",
    "Province_n": "省份",
    # "area": "市面积",
}


def selecting(pool: Cols, include: Cols = None, exclude: Cols = None) -> Cols:
    """从可迭代对象中选取某些条目"""
    include = set(pool) if include is None else set(make_list(include, True))
    exclude = set() if exclude is None else set(make_list(exclude, True))
    if invalid := (set(include) | set(exclude)).difference(pool):
        logger.warning("Invalid items: %s.", invalid)
    included = set(pool).intersection(set(include))
    return included.difference(set(exclude))


def select_items(measurements=None, sectors=None):
    """从原始数据中选择所有数值条目"""
    if measurements is None:
        measurements = ["WUI", "WU"]
    sectors = selecting(SECTORS, include=sectors)
    measurements = selecting(MEASUREMENTS, include=measurements)
    results = []
    for sector in sectors:
        pool = ITEMS[sector]
        results.extend(pool[measurement] for measurement in measurements)
    return list(itertools.chain(*results))


def select(
    include_items=None,
    sectors=None,
    measurements=None,
    general_cols=None,
    include_summary=False,
) -> Cols:
    """根据部门、条目、测量来选择列，返回所有按条件选择的列名"""
    potential_items = select_items(measurements, sectors=sectors)
    columns = sorted(list(selecting(GENERAL_COLUMNS, include=general_cols)))
    items = selecting(potential_items, include=include_items)
    columns.extend(items)
    # 地区总用水量
    if include_summary:
        columns.extend(selecting(SUMMARY, include=sectors))
    return columns
