import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

cities = ["Pittsburgh", "Chicago", "San Francisco", "Detroit", "Houston", "Durham", "Indianapolis", "Birmingham", "Orlando",
          "Nashville", "Tampa", "Seattle", "San Antonio", "Cleveland", "Dallas", "Philadelphia", "Columbus",
          "Miami", "Portland", "Los Angeles", "Baltimore", "Charleston", "New York", "Albuquerque", "St. Louis",
          "Denver", "Virginia Beach", "Atlanta", "Boston", "Sacramento", "Phoenix", "Charlotte", "Minneapolis", "San Diego", "Salt Lake City"]

xlOrders = pd.ExcelFile(r'./resources/output/orderIn60Miles.xlsx')
xlPolys = pd.ExcelFile(r'./resources/output/polygons.xlsx')

writer = pd.ExcelWriter('./resources/output/polyIn60MilesPercent.xlsx')

countUS = 0
totalUS = 0
percentArray = []
for city in cities:
    print(city)
    dfPolysCity = xlPolys.parse(city)
    latPolys = dfPolysCity["Lat"]
    lngPolys = dfPolysCity["Lng"]

    dfOrdersCity = xlOrders.parse(city)
    latOrders = dfOrdersCity["Lat"]
    lngOrders = dfOrdersCity["Lng"]
    disOrders = dfOrdersCity["Distance"]

    if len(latPolys) == 0:
        percentArray.append("100%")
        print("100%")
        countUS += len(disOrders)
        totalUS += len(disOrders)
        continue

    polyList = []
    for pIndex in range(0, len(latPolys)):
        polyList.append([latPolys[pIndex], lngPolys[pIndex]])
    polygon = Polygon(polyList)

    count = 0
    total = 0
    for oIndex in range(0, len(disOrders)):
        if disOrders[oIndex] > 60:
            break
        point = Point(latOrders[oIndex], lngOrders[oIndex])
        if polygon.contains(point):
            count += 1
            countUS += 1
        total += 1
        totalUS += 1
    percent = "{0:.0%}".format(count / total)
    percentArray.append(percent)
    print(percent)

cities.append("US Total")
percent = "{0:.0%}".format(countUS / totalUS)
percentArray.append(percent)
print("US Total:" + percent)

dataPercent = {'City': cities, 'Percentage': percentArray}
dfPercent = pd.DataFrame(dataPercent)
dfPercent.to_excel(writer)
writer.save()
