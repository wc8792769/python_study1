from china_water_use import ChineseWater

# 加载数据
cwu = ChineseWater()

# 组织数据
#
provinces = [
    "Qinghai",
    "Gansu",
    "Neimeng",
    "Ningxia",
    "Shanxi",
    "Shaanxi",
    "Henan",
    "Shandong",
]
# 更新研究范围:
    # - 关注以下省份的城市
    # - 关注用水强度 (WUI)
    # - 关注灌溉行业
cities = cwu.update_scope("Province_n", provinces)
wui = cwu.update_scope("measurements", "WUI")
sectors = cwu.update_scope("sectors", "IRR")
cwu.data.head()

# 转换单位为 mm / km^2
data = cwu.units('mm * km**-2')

# 绘制数据
print(cwu.items)  # 显示缩小关注范围后选定的条目
cwu.scaled_plots("Irrigation water-use intensity (WUI): Maize")