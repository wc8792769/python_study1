#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pint_pandas
from pint import UnitRegistry

from china_water_use.constants import SUMMARY, select_items

ureg = UnitRegistry()  # 注册单位
# 使用这里的注册单位成为 Pandas-pint 的注册单位，详见：
# https://github.com/hgrecco/pint-pandas/blob/master/notebooks/pint-pandas.ipynb
pint_pandas.PintType.ureg = ureg
# 为了让pandas-pint 可以画图，需要这样注册，详见：
# https://github.com/hgrecco/pint-pandas/blob/master/notebooks/pint-pandas.ipynb
pint_pandas.PintType.ureg.setup_matplotlib()
ureg.define("TMC = 1e8 m ** 3")

UNITS = {}
UNITS.update({item: "km ** 3" for item in SUMMARY})

# 农业灌溉
irrigated_WUI = select_items(sectors=["IRR"], measurements=["WUI"])
UNITS.update({item: "mm * kha**-1" for item in irrigated_WUI})

irrigated_area = select_items(sectors=["IRR"], measurements=["Magnitude"])
UNITS.update({item: "kha" for item in irrigated_area})

irrigated_WU = select_items(sectors=["IRR"], measurements="WU")
UNITS.update({item: "mm" for item in irrigated_WU})
