import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import alphashape


def find_edges_with(i, edge_set):
    i_first = [j for (x, j) in edge_set if x == i]
    i_second = [j for (j, x) in edge_set if x == i]
    return i_first, i_second


def stitch_boundaries(edges):
    edge_set = edges.copy()
    boundary_lst = []
    while len(edge_set) > 0:
        boundary = []
        edge0 = edge_set.pop()
        boundary.append(edge0)
        last_edge = edge0
        while len(edge_set) > 0:
            i, j = last_edge
            j_first, j_second = find_edges_with(j, edge_set)
            if j_first:
                edge_set.remove((j, j_first[0]))
                edge_with_j = (j, j_first[0])
                boundary.append(edge_with_j)
                last_edge = edge_with_j
            elif j_second:
                edge_set.remove((j_second[0], j))
                edge_with_j = (j, j_second[0])  # flip edge rep
                boundary.append(edge_with_j)
                last_edge = edge_with_j

            if edge0[0] == last_edge[1]:
                break

        boundary_lst.append(boundary)
    return boundary_lst


cities = ["Pittsburgh", "Chicago", "San Francisco", "Detroit", "Houston", "Durham", "Indianapolis", "Birmingham",
          "Orlando",
          "Nashville", "Tampa", "Seattle", "San Antonio", "Cleveland", "Dallas", "Philadelphia", "Columbus",
          "Miami", "Portland", "Los Angeles", "Baltimore", "Charleston", "New York", "Albuquerque", "St. Louis",
          "Denver", "Virginia Beach", "Atlanta", "Boston", "Sacramento", "Phoenix", "Charlotte", "Minneapolis",
          "San Diego", "Salt Lake City"]

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
    pointsInRadius = []
    for oIndex in range(0, len(disOrders)):
        if disOrders[oIndex] > 60:
            break
        point = Point(latOrders[oIndex], lngOrders[oIndex])
        if polygon.contains(point):
            pointsInRadius.append(point)
            count += 1
            countUS += 1
        total += 1
        totalUS += 1

    latsInRadius = [p.x for p in pointsInRadius]
    lngsInRadius = [p.y for p in pointsInRadius]

    inRadiusData = {
        'Lat': latsInRadius,
        'Lng': lngsInRadius
    }
    inRadiusDf = pd.DataFrame(inRadiusData)
    inRadiusDf.to_excel(writer, sheet_name=city + " Inside Orders")

    alphaShape = alphashape.alphashape(pointsInRadius, 5.0)
    alphaShapeLat, alphaShapeLng = alphaShape.exterior.coords.xy
    alphaShapeData = {
        'Lat': alphaShapeLat,
        'Lng': alphaShapeLng
    }
    alphaShapeDf = pd.DataFrame(alphaShapeData)
    alphaShapeDf.to_excel(writer, sheet_name=city + " Boundary Orders")

    percent = "{0:.0%}".format(count / total)
    percentArray.append(percent)
    print(percent)

cities.append("US Total")
percent = "{0:.0%}".format(countUS / totalUS)
percentArray.append(percent)
print("US Total:" + percent)

dataPercent = {'City': cities, 'Percentage': percentArray}
dfPercent = pd.DataFrame(dataPercent)
dfPercent.to_excel(writer, sheet_name="Percentage")
writer.save()

