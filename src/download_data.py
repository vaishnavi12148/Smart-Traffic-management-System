from ucimlrepo import fetch_ucirepo 
import pandas as pd
  
# fetch dataset 
metro_traffic= fetch_ucirepo(id=492) 
  
# data (as pandas dataframes) 
x = metro_traffic.data.features 
y = metro_traffic.data.targets 
df=pd.concat([x,y] ,axis=1)

# Save locally so later phases don't need internet access at all
df.to_csv("data/raw/metro_interstate_traffic_volume.csv", index=False)

print("Saved:", df.shape[0], "rows and", df.shape[1], "columns")
print(df.head())
