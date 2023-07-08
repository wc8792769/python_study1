#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

# from typing import List, Union

import logging
import os
from typing import Dict, List, Optional, Set

import geopandas as gpd
import pandas as pd

# from IPython import display
from matplotlib import pyplot as plt

from china_water_use.constants import (
    GENERAL_COLUMNS,
    MEASUREMENTS,
    SECTORS,
    make_list,
    select_items,
    selecting,
)
from china_water_use.units import UNITS

logger = logging.getLogger(__name__)
pd.options.display.float_format = "{:,.2f}".format

# get path to the data folder
data_path = os.path.join(os.path.dirname(__file__), "data")

# load dataset
NAME = r"values_data.csv"
DATA = os.path.join(data_path, NAME)
ITEMS = os.path.join(data_path, "items.json")
MAP = os.path.join(data_path, "GIS Shapefile/perfectures.shp")


class ChineseWater:
    """中国用水数据"""

    def __init__(self, data: pd.DataFrame = None):
        if data is None:
            data = pd.read_csv(DATA, index_col=0)
        self._origin = data
        self._time = set(data["Year"].unique())
        self._cities = set(data["City_ID"].unique())
        self._sectors = None
        self._measurements = None
        self._include = set()
        self._exclude = set()

    # def __repr__(self):
    #     display.display(self.show_data())
    #     return f"<[Chinese Water Use] {len(self.cities)} cities, {len(self.active_cols)} items.>"

    @property
    def sectors(self) -> set:
        """用水部门"""
        return selecting(SECTORS, include=self._sectors)

    @property
    def measurements(self) -> set:
        """数据测量范围"""
        return selecting(MEASUREMENTS, include=self._measurements)

    @property
    def data(self) -> pd.DataFrame:
        """根据当前的范围过滤后的数据"""
        time = self.origin["Year"].isin(self.time)
        cities = self.origin["City_ID"].isin(self.cities)
        cols = selecting(self.items, self.include, self.exclude)
        return self.origin.loc[(time & cities), [*GENERAL_COLUMNS, *cols]]

    @property
    def include(self) -> Set[str]:
        """要包括的条目"""
        return self._include or None

    @property
    def exclude(self) -> Set[str]:
        """要排除的条目"""
        return self._exclude or None

    @property
    def cities(self) -> Set[str]:
        """城市"""
        return self._cities

    @property
    def time(self) -> pd.Series:
        """时间"""
        return self._time

    @property
    def origin(self) -> pd.DataFrame:
        """原始数据"""
        return self._origin

    @property
    def items(self) -> Set[str]:
        """根据当前研究的范围，可能的列"""
        return set(select_items(measurements=self.measurements, sectors=self.sectors))

    @property
    def index(self) -> pd.DataFrame:
        """属性列"""
        return self.data[GENERAL_COLUMNS.keys()]

    def update_scope(self, key, include=None, exclude=None):
        """更新本次关心的数据范围，更新'measurements'和'sectors'

        Args:
            key (str)：要更新的范畴，可以是'measurements'或'sectors'。
            include (Union[str, List[str]]，可选）：要包括的研究范围列表。默认为None。
            exclude (Union[str, List[str]]，可选）：要排除的研究范围列表。默认为None。

        Returns:
            set: 更新后的数据范围（集合）。

        Raises:
            KeyError: 如果which不是一个有效的范畴。

        Notes:
            - 对于'measurements'，有效的范围有{"WUI": "用水强度", "WU": "用水量", "Magnitude": "体量"}。
            - 对于'sectors'，有效的范围有{"IRR": "农业", "IND": "工业", "RUR": "农村", "URB": "城市"}。
            - 更新后的数据范围存储在实例变量`_{which}`中。

        Example:
            要更新测量范围并排除'Magnitude'，请按以下方式调用该方法：

            >>> obj.update_scope('measurements'， exclude='Magnitude')
        """
        if key == "measurements":
            scope = selecting(MEASUREMENTS, include=include, exclude=exclude)
        elif key == "sectors":
            scope = selecting(SECTORS, include=include, exclude=exclude)
        elif key == "items":
            self._include.update(make_list(include, keep_none=False))
            self._exclude.update(make_list(exclude, keep_none=False))
            return None
        elif key in GENERAL_COLUMNS:
            key, scope = self._update_samples(key, include, exclude)
        else:
            raise KeyError(f"{key} is not a valid scope.")
        old_scope = getattr(self, key)
        setattr(self, f"_{key}", set(scope) & set(old_scope))

    def _update_samples(self, key, include=None, exclude=None):
        mapping = {"Year": "time", "City_ID": "cities"}
        if key == "Province_n":
            to_select = self.data["Province_n"].unique()
            scope = selecting(to_select, include=include, exclude=exclude)
            mask = self.data.Province_n.isin(scope)
            scope = self.data.loc[mask]["City_ID"].unique()
            return "cities", scope
        if key in mapping:
            key = mapping[key]
            to_select = getattr(self, key)
            scope = selecting(to_select, include=include, exclude=exclude)
        else:
            raise KeyError(f"Invalid update operation: {key}")
        return key, scope

    def clear(self, *args, **scopes: Dict[str, bool]):
        """清除已经添加的关注范围"""
        valid_scopes = "time, cities, measurements, sectors, include, exclude"
        # clear all if not assigned specific scopes.
        if not args and not scopes:
            args = valid_scopes
        clear = []

        def clear_scope(scope):
            if scope not in valid_scopes:
                raise KeyError(f"{scope} is not a valid scope: {valid_scopes}.")
            setattr(self, f"_{scope}", set())
            clear.append(scope)

        for arg in args:
            clear_scope(arg)
        for scope, bool_ in scopes.items():
            if bool_:
                clear_scope(scope)
        logger.info(f"{', '.join(clear)} cleared.")

    # @property
    # def show_versions(self):
    #     return pint_pandas.show_versions()

    # def show_data(self, folding: bool = True, sep: str = ":") -> pd.DataFrame:
    #     dataset = []
    #     for col in self.active_cols:
    #         data = self._get_item_data(col, folding)
    #         # show as this pattern: [level1: level2]
    #         if isinstance(data, pd.DataFrame):
    #             data.columns = [col + sep + c for c in data.columns]
    #         dataset.append(data)
    #     return pd.concat(dataset, axis=1)

    # def get_item(self, item: str, unit: bool = True) -> pd.DataFrame:
    #     """读取周丰老师中国用水数据的函数，选取某个项目"""
    #     selected = self._get_item_data(item, folding=False)
    #     # 获得带单位的输出
    #     if unit:
    #         unit = self.get_unit_of_item(item)
    #         selected = selected.astype(unit)
    #     # 选择该 general_cols 和该 item 下的数据
    #     return pd.concat([self.index, selected], axis=1)

    # def replenish_index(
    #     self, data: Union[pd.Series, pd.DataFrame], name: str = "Unnamed"
    # ) -> pd.DataFrame:
    #     if isinstance(data, pd.Series) and pd.Series.name is None:
    #         data.name = name
    #     return pd.concat([self.index, data], axis=1)

    def get_unit_of_item(self, item: str) -> str:
        """获取某列的单位"""
        try:
            unit = f"pint[{UNITS[item]}]"
        except KeyError as e:
            raise e(f"Not registered unit of item: '{item}'!") from e
        return unit

    # def filter_prefectures(
    #     self, cities: List[str], as_origin: bool = False
    # ) -> pd.DataFrame:
    #     """筛选合适特定的地级市"""
    #     tmp_data = self.origin.droplevel(1, axis=1)
    #     filtered = tmp_data[tmp_data["City_ID"].isin(cities)]
    #     filtered.columns = self.origin.columns
    #     if as_origin:
    #         self.origin = filtered
    #     return filtered

    def units(
        self, converter: Optional[str] = None, dequantify: bool = True
    ) -> pd.DataFrame:
        """将数据集里的特定列转化成指定的单位"""
        result = self.data.copy()
        items = selecting(self.items, self.include, self.exclude)
        if isinstance(converter, str):
            converter = {item: converter for item in items}
        elif isinstance(converter, dict):
            pass
        elif hasattr(converter, "__iter__"):
            converter = {col: converter[i] for i, col in enumerate(items)}
        else:
            raise TypeError(f"Invalid mapping type: {type(converter)}")
        for col in items:
            if unit := self.get_unit_of_item(col):
                result[col] = result[col].astype(unit)
                # print(f'converting {col} from {unit} to {converter[col]}...')
                result[col] = result[col].pint.to(converter[col])
            else:
                logger.warning(f"Failed to get unit of {col}.")
        return result.pint.dequantify().droplevel(1, axis=1) if dequantify else result

    def _cities_shp(self, cities: List[str] = None) -> gpd.GeoDataFrame:
        """获取城市的空间范围信息"""
        if cities is None:
            cities = self.cities
        gdf = gpd.read_file(MAP)
        return gdf[gdf["Perfecture"].isin(cities)]

    # def viz_item_spatially(self, item, year: Union[int, str] = "mean"):
    #     pass

    # def provincial_group(self, data, year: Union[int, str], agg: str = "mean"):
    #     name = data.name
    #     data = self.replenish_index(data)
    #     if type(year) is int:
    #         query = data[data["Year"] == year]
    #     elif type(year) is str:
    #         query = data.groupby("City_ID")[name].agg(agg).reset_index()
    #     df = pd.merge(
    #         left=query,
    #         right=self.geodf,
    #         left_on="City_ID",
    #         right_on="Perfecture",
    #         how="left",
    #     )
    #     return gpd.GeoDataFrame(df)

    # def combine_province(self, data):
    #     return pd.merge(
    #         left=data,
    #         right=self.geodf[["Perfecture", "Province_n"]],
    #         left_on="City_ID",
    #         right_on="Perfecture",
    #         how="left",
    #     )

    # def dequantify(self, data):
    #     return data.pint.dequantify().droplevel(1, axis=1)

    def geodata(self, data=None) -> gpd.GeoDataFrame:
        """转化为空间数据"""
        if data is None:
            data = self.data
        geodf = self._cities_shp(data.City_ID.unique())
        merged = pd.merge(
            left=data,
            right=geodf,
            left_on="City_ID",
            right_on="Perfecture",
            how="left",
        )
        return gpd.GeoDataFrame(merged)

    def scaled_plots(self, col, data=None, ax=None, **kwargs):
        """根据某一列的值制作分级设色专题图"""
        if ax is None:
            _, ax = plt.subplots()
        geodata = self.geodata(data=data)
        legend = kwargs.pop("legend", False)
        # ax = shapefile.boundary.plot(edgecolor="black", lw=1, ls=":", label="YR", ax=ax)
        ax = geodata.plot(
            ax=ax,
            column=col,
            cmap="Reds",
            edgecolor="white",
            linewidth=0.5,
            # scheme="NaturalBreaks",
            k=5,
            legend=legend,
            legend_kwds={
                "loc": "upper left",
                "title": f"{col}",
            },
            **kwargs,
        )
        ax.grid(color="lightgray", ls="--")
        ax.set_xlabel("Longitude [$Degree$]")
        ax.set_ylabel("Latitude [$Degree$]")
        return ax
