import pandas as pd

df = pd.read_excel(r'~/Documents/workplace/deliver-service-copy/src/main/resources/Albuquerque.xlsx')
print(df[["Distance"]])