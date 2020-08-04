import os
import pandas as pd

directory = os.fsencode('./resources/raw')

writer = pd.ExcelWriter('./resources/output/orderIn60Miles.xlsx')

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".xlsx"):
        filename = os.path.join(directory, file).decode()
        city = file.decode().split('.')[0]
        print(city)
        df = pd.read_excel(filename)

        dist = df["Distance"]
        distInRadius = list(filter(lambda x: (x <= 60), dist))
        orderInRadius = df["Order ID"][0:len(distInRadius)]
        latInRadius = df["Lat"][0:len(distInRadius)]
        lngInRadius = df["Lng"][0:len(distInRadius)]

        data = {'Order ID': orderInRadius, 'Distance': distInRadius, 'Lat': latInRadius, 'Lng': lngInRadius}
        df2 = pd.DataFrame(data)

        df2.to_excel(writer, sheet_name=city)

writer.save()
