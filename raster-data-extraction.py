# import required packages
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.windows import Window

# read raster image
rst = rasterio.open("input/21-07-2021-11-36.tif", mode='r')

# read shapefile with in-situ buoy measurements of turbidity and chl-a (will also work with a csv with gps points)
shp = gpd.read_file("input/Buoy_Measurements.shp")

# tidy things up
shp = shp.drop(['geometry'], axis=1) # geometry column isn't needed
dict = {'Timestam_1':'date_time', 'Longitude_':'lon', 'Latitude_m':'lat', 'Turbidity_':'turb', 'Chlorophyl':'chl'}
shp.rename(columns=dict, inplace=True) # rename columns

# function to extract pixel values and calculate average values of 3x3 grid around the coordinates
def compute_values(raster, band, lat, lon):
  row, col = raster.index(lon, lat)
  window = Window.from_slices(rows=(row-1, row+2), cols=(col-1, col+2))
  result = np.average(raster.read(band, window=window))
  raster = raster.read()
  result2 = raster[band-1, row, col]
  return result, result2

# loop through all coordinates in the dataframe to calculate and store turbidity & chl-a values
point_turb = []
avg_turb = []
point_chl = []
avg_chl = []
for i,j in zip(shp['lat'], shp['lon']):
    result, result2 = compute_values(rst, 3, i, j) # turbidity band
    avg_turb.append(result)
    point_turb.append(result2)
    result, result2 = compute_values(rst, 1, i, j) #  chl-a band
    avg_chl.append(result)
    point_chl.append(result2)

# write turbidity and chl-a values to a dataframe
shp['sat_turb'], shp['sat_avg_turb'] = point_turb, avg_turb
shp['sat_turb_diff'] = shp['turb'] - shp['sat_turb'] # calculate difference between in-situ and satellite data
shp['sat_avg_turb_diff'] = shp['turb'] - shp['sat_avg_turb'] 
shp['sat_chl'], shp['sat_avg_chl'] = point_chl, avg_chl
shp['sat_chl_diff'] = shp['chl'] - shp['sat_chl'] 
shp['sat_avg_chl_diff'] = shp['chl'] - shp['sat_avg_chl'] 

# write data to csv
shp.to_csv('output/sample.csv', index=False)


