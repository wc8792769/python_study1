import csv
import json
import numpy as np

filename1 = r'china_water_use\data\values_data.csv'
filename2 = 'china_water_use\data\items.json'

with open(filename1) as f:
    reader_wu = csv.reader(f)
    line_list = next(reader_wu)

    irrs, citys, years = [], [], []
    for row in reader_wu:
          if row[1] == 'C1':
               irr = float(row[3])
               city = row[1]
               year = row[2]

               irrs.append(irr)
               citys.append(city)
               years.append(year)
               
    # print(irrs)
    # print(citys)
    # print(years)

with open(filename2, encoding='utf-8') as g:
    reader_items = json.load(g)

def trendline(data):
    order=1
    index=[i for i in range(1,len(data)+1)]
    coeffs = np.polyfit(index, list(data), order)
    slope = coeffs[-2]
    return float(slope)

trendline(irrs)


