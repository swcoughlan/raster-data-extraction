# import required packages
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.windows import Window

# read raster image
rst = rasterio.open("input/21-07-2021-11-36.tif", mode='r')

# read shapefile with in-situ buoy measurements of turbidity and chl-a (will also work with a csv with GPS points)
shp = gpd.read_file("input/Buoy_Measurements.shp")

# tidy things up
shp = shp.drop(['geometry'], axis=1)  # geometry column isn't needed
column_mapping = {'Timestam_1': 'date_time', 'Longitude_': 'lon', 'Latitude_m': 'lat', 'Turbidity_': 'turb', 'Chlorophyl': 'chl'}
shp.rename(columns=column_mapping, inplace=True)  # rename columns

# function to extract pixel values and calculate average values of a 3x3 grid around the given coordinates
def calc_values(raster, band, lat, lon):
    row, col = raster.index(lon, lat)
    window = Window.from_slices(rows=(row-1, row+2), cols=(col-1, col+2))
    average_value = np.average(raster.read(band, window=window))
    center_pixel_value = raster.read()[band-1, row, col]
    return average_value, center_pixel_value

point_turb = [calc_values(rst, 3, i, j)[1] for i, j in zip(shp['lat'], shp['lon'])]
avg_turb = [calc_values(rst, 3, i, j)[0] for i, j in zip(shp['lat'], shp['lon'])]
point_chl = [calc_values(rst, 1, i, j)[1] for i, j in zip(shp['lat'], shp['lon'])]
avg_chl = [calc_values(rst, 1, i, j)[0] for i, j in zip(shp['lat'], shp['lon'])]

# calculate difference between in-situ/satellite data and write values to a dataframe
shp['sat_turb'], shp['sat_avg_turb'] = point_turb, avg_turb
shp['sat_turb_diff'], shp['sat_avg_turb_diff'] = shp['turb'] - shp['sat_turb'], shp['turb'] - shp['sat_avg_turb'] 
shp['sat_chl'], shp['sat_avg_chl'] = point_chl, avg_chl
shp['sat_chl_diff'], shp['sat_avg_chl_diff'] = shp['chl'] - shp['sat_chl'], shp['chl'] - shp['sat_avg_chl']

# write data to csv
shp.to_csv('output/sample.csv', index=False)