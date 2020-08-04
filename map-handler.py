import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

xlOrders = pd.ExcelFile(r'./resources/output/orderIn60Miles.xlsx')
xlPolys = pd.ExcelFile(r'./resources/output/polygons.xlsx')
xlPercents = pd.ExcelFile(r'./resources/output/polyIn60MilesPercent.xlsx')

# import street map
street_map = gpd.read_file('./resources/tl_2018_us_necta/tl_2018_us_necta.shp')
# designate coordinate system
crs = {'init': 'EPSG:4326'}

index = 0
dfPercents = xlPercents.parse("Percentage")
for city in dfPercents["City"]:
    print(city)
    if city == "Boston" or city == "US Total":
        continue
    dfOrders = xlOrders.parse(city)
    dfPolys = xlPolys.parse(city)

    dfOrdersInside = xlPercents.parse(city + " Inside Orders")
    dfOrdersBoundary = xlPercents.parse(city + " Boundary Orders")

    # zip x and y coordinates into single feature
    geometryOrders = [Point(x, y) for x, y in zip(dfOrders['Lng'], dfOrders['Lat'])]
    # geometryPolys = [Point(x, y) for x, y in zip(dfPolys['Lng'], dfPolys['Lat'])]
    geometryPolys = [Point(x, y) for x, y in zip(dfOrdersBoundary['Lng'], dfOrdersBoundary['Lat'])]

    # create GeoPandas dataframe
    geoDfOrders = gpd.GeoDataFrame(dfOrders, crs=crs, geometry=geometryOrders)

    geoDfPolys = gpd.GeoDataFrame(dfOrdersBoundary, crs=crs, geometry=geometryPolys)
    polygon = Polygon(geoDfPolys['geometry'].tolist())
    geoDfPolys = gpd.GeoDataFrame(geometry=[polygon], crs=crs)

    geoDfPolysArea = geoDfPolys.copy()
    geoDfPolysArea = geoDfPolysArea.to_crs({'init': 'epsg:32633'})
    geoDfPolysArea["area"] = geoDfPolysArea['geometry'].area / 10 ** 6  # km2
    orderDensity = len(dfOrdersInside) / geoDfPolysArea["area"][0]
    # print(orderDensity)

    # create figure and axes, assign to subplot
    fig, ax = plt.subplots(figsize=(15, 15))

    # add .shp mapfile to axes
    street_map.plot(ax=ax, alpha=0.4, color='grey')

    # add geodataframe to axes
    geoDfPolys.boundary.plot(color=None, edgecolor='k', ax=ax)
    geoDfOrders.plot(column='Distance', ax=ax, alpha=0.5, legend=True, markersize=4)
    # geoDfOrders.plot(ax=ax, alpha=0.5, legend=True, markersize=4)

    # add title to graph
    plt.title(city + " (" + dfPercents["Percentage"][index] + " inside, " +
              "{:.2f}".format(orderDensity) + " orders/km2, Total Area: " +
              "{:.2f}".format(geoDfPolysArea["area"][0]) + "km2)",
              fontsize=15, fontweight='bold')

    # set latitiude and longitude boundaries for map display
    xMin = min(geoDfOrders['Lng'])
    xMax = max(geoDfOrders['Lng'])

    yMin = min(geoDfOrders['Lat'])
    yMax = max(geoDfOrders['Lat'])

    plt.xlim(xMin, xMax)
    plt.ylim(yMin, yMax)
    # show map
    # plt.show()
    plt.savefig("./resources/output/figures/" + city + ".png")
    index += 1

