# -*- coding: utf-8 -*-
"""
Created on Fri May  6 12:46:54 2022

@author: Ahmad Mojiri
"""
from projdirs import datadir
import os
import numpy as np
import pandas as pd
import json, io, requests, platform
import PySAM.Pvwattsv8 as PVWatts, Windpower

################################################################
def pv_gen(capacity):
    """
    Parameters
    ----------
    capacity in kW

    Returns system powr generated in W for each hour in a year
    
    """
    pv = PVWatts.new()
    
    
    #dir = datadir + ['\SAM_INPUTS\SOLAR\\', '/SAM_INPUTS/SOLAR/'][platform.system()=='Linux']
    #file_name = ['pvfarm_pvwattsv8_win','pvfarm_pvwattsv8_linux'][platform.system()=='Linux']
    module = pv
    
    dir = datadir + os.sep + 'SAM_INPUTS' + os.sep + 'SOLAR' + os.sep 
    file_name = 'pvfarm_pvwattsv8'
    with open(dir + file_name + ".json", 'r') as file:
        data = json.load(file)
        data['solar_resource_file'] = dir + 'SolarSource.csv'
        for k,v in data.items():
            if k != "number_inputs":
                module.value(k, v)
    
    # module.SystemDesign.system_capacity = capacity
    pv.execute()
    output = np.array(pv.Outputs.gen)
    return(output.tolist())

#################################################################
def wind_gen(hub_height=150):
    """
    Parameters
    ----------
    Capacity will be added later

    Returns wind powr generated in W for each hour in a year
    
    """
    wind = Windpower.new()
    
    #dir = datadir + ['\SAM_INPUTS\WIND\\', '/SAM_INPUTS/WIND/'][platform.system()=='Linux']
    #file_name = ['windfarm_windpower_win','windfarm_windpower_linux'][platform.system()=='Linux']
    module = wind
    dir = datadir + os.sep + 'SAM_INPUTS' + os.sep + 'WIND' + os.sep 
    file_name = 'windfarm_windpower'
    
    with open(dir + file_name + ".json", 'r') as file:
        data = json.load(file)
        data['wind_resource_filename'] = dir + 'WindSource.srw'
        for k,v in data.items():
            if k != "number_inputs":
                module.value(k, v)
    file.close()
    # module.SystemDesign.system_capacity = capacity
    wind.Turbine.wind_turbine_hub_ht = hub_height
    wind.execute()
    output = np.array(wind.Outputs.gen)
    return(output.tolist())

#################################################################
def solcast_weather(location):
    """
    The function download tmy weather data from Solcast under a research
    account.

    Parameters
    ----------
    location : List object
         includes [latitude,longitude] of the location

    Returns a savd csv file in the format that can be used with SAM for PV
    modelling.
    """
    base_url = 'https://api.solcast.com.au/'
    tool = 'tmy_hourly?api_key='
    key = 'YNEmGUM8_CfnWlNPinB9d3EnlGVpFwWV'
    Parameters = {}
    Parameters = dict(zip(['api_key','format','latitude','longitude'],
                          [key,'x-sam+csv']+ location,
                          ))
    
    response = requests.get(base_url+tool,params=Parameters)
    print('Connection Status:', response.status_code)
    response.close()
    
    path = r'C:\Nextcloud\HILT-CRC---Green-Hydrogen\DATA\SAM_INPUTS\WEATHER_DATA'
    text_file = open(path + "\weather_data_solcast.csv", "w")
    text_file.write(response.text)
    text_file.close()
    print('Weather data was downloaded from Solcast database!')

 #################################################################
def SolarResource(Location):
    """
    Parameters
    ----------
    None
        
    Returns
    -------
    copies the weather data into SOLAR folder for SAM.

    """
    WD_file = 'weather_data_%s.csv'%(Location)
    parent_directory = os.path.dirname(os.getcwd())
    path = parent_directory + os.sep + 'DATA' + os.sep + 'SAM_INPUTS' + os.sep + 'WEATHER_DATA'    
    data = pd.read_csv(path + os.sep + WD_file)
    data_text = data.to_csv(index=False, lineterminator='\n')
    path = parent_directory + os.sep + 'DATA' + os.sep + 'SAM_INPUTS' + os.sep + 'SOLAR'
    
    text_file = open(path + os.sep + "SolarSource.csv", "w")
    text_file.write(data_text)
    text_file.close()
    print('Solar data file was generated from Solcast database!')

 #################################################################
def WindSource(Location):
    """
    Generates the wind source data for SAM based on the weather data 
    that is stored in WEATHER folder
    
    Returns
    -------
    None.
    
    """
    WD_file = 'weather_data_%s.csv'%(Location)
    parent_directory = os.path.dirname(os.getcwd())
    path = parent_directory + os.sep + 'DATA' + os.sep + 'SAM_INPUTS' + os.sep + 'WEATHER_DATA'    
    data = pd.read_csv(path + os.sep + WD_file, skiprows=0)
    Lat = data.lat[0]
    Lon = data.lon[0]
    data = pd.read_csv(path + os.sep + WD_file, skiprows=2)
    
    data_10 = data.iloc[:,[5,14,15,16]].copy()
    data_10.Pressure=data_10.Pressure/1013.25
    data_10 = data_10.rename(columns = {'Temperature':'T',
                                        'Wind Speed':'S',
                                        'Wind Direction':'D',
                                        'Pressure':'P'})
    heading_10 = pd.DataFrame({'T':['Temperature','C',10],
                               'S':["Speed", 'm/s',10],
                               'D':["Direction",'degrees',10],
                               'P':['Pressure','atm',10]})
    data_10 = heading_10.append(data_10).reset_index(drop=True)
    data = data_10.copy()
    Z_anem = 10
    
    Z = 40
    data_40 = data_10.copy()
    data_40.iloc[2,:]=Z
    data_temp = data_40.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )
    data_temp.S = S
    data_40 = data_40.iloc[0:3].append(data_temp,ignore_index=True)
    data = pd.concat([data , data_40],axis=1)
    
    Z = 70
    data_70 = data_10.copy()
    data_70.iloc[2,:]=Z
    data_temp = data_70.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )
    data_temp.S = S
    data_70 = data_70.iloc[0:3].append(data_temp,ignore_index=True)
    data = pd.concat([data , data_70],axis=1)
    
    Z = 100
    data_100 = data_10.copy()
    data_100.iloc[2,:]=Z
    data_temp = data_100.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )
    data_temp.S = S
    data_100 = data_100.iloc[0:3].append(data_temp,ignore_index=True)
    data = pd.concat([data , data_100],axis=1)
    
    Z = 130
    data_130 = data_10.copy()
    data_130.iloc[2,:]=Z
    data_temp = data_130.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )
    data_temp.S = S
    data_130 = data_130.iloc[0:3].append(data_temp,ignore_index=True)
    data = pd.concat([data , data_130],axis=1)
    
    Z = 160
    data_160 = data_10.copy()
    data_160.iloc[2,:]=Z
    data_temp = data_160.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )
    data_temp.S = S
    data_160 = data_160.iloc[0:3].append(data_temp,ignore_index=True)
    data = pd.concat([data , data_160],axis=1)
    
    
    data.loc[-1] = 24*['Latitude:%s'%(Lat)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    data.loc[-1] = 24*['Longitude:%s'%(Lon)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    
    data_text = data.to_csv(header=False, index=False, line_terminator='\n')
    
    path = parent_directory + os.sep + 'DATA' + os.sep + 'SAM_INPUTS' + os.sep + 'WIND'
    
    text_file = open(path + "\WindSource.csv", "w")
    text_file.write(data_text)
    text_file.close()
    print("Wind source data file was generated from Solcast database!")
 #################################################################
def WindSource_windlab(Location):
    """
    Generates the wind source data for SAM based on the weather data 
    that is sourced from windlab stored in WEATHER folder
    This data is based on 150m hub height
    
    Returns
    -------
    None.
    
    """
    WD_file = 'weather_data_%s.csv'%(Location)
    
    parent_directory = os.path.dirname(os.getcwd())
    path = parent_directory + os.sep + 'DATA' + os.sep + 'SAM_INPUTS' + os.sep + 'WEATHER_DATA'    
    data = pd.read_csv(path + os.sep + WD_file, skiprows=0)
    Lat = data.lat[0]
    Lon = data.lon[0]
    data = pd.read_csv(path + os.sep + WD_file, skiprows=2)
    
    data_150 = data.iloc[:,[5,14,15,16]].copy()
    data_150.Pressure=data_150.Pressure/1013.25
    data_150 = data_150.rename(columns = {'Temperature':'T',
                                        'Wind Speed':'S',
                                        'Wind Direction':'D',
                                        'Pressure':'P'})
    heading_150 = pd.DataFrame({'T':['Temperature','C',150],
                               'S':["Speed", 'm/s',150],
                               'D':["Direction",'degrees',150],
                               'P':['Pressure','atm',150]})
    #data_150 = heading_150.append(data_150).reset_index(drop=True) # I got a warning for this sentence
    data_150 = pd.concat([heading_150, data_150], ignore_index=True)
    
    data = data_150.copy()
    Z_anem = 150
    
    Z = 10
    data_10 = data_150.copy()
    data_10.iloc[2,:]=Z
    data_temp = data_10.iloc[3:].copy()
    S = data_temp.apply(lambda x:speed(Z, Z_anem, data_temp['S']) )

    #data_temp.S = S # this sentence does not work in my computer
    data_temp.S = S.S
    #data_10 = data_10.iloc[0:3].append(data_temp,ignore_index=True)
    data_10 = pd.concat([data_10.iloc[0:3], data_temp], ignore_index=True)
    
    data = pd.concat([data , data_10],axis=1)
    
        
    data.loc[-1] = 8*['Latitude:%s'%(Lat)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    data.loc[-1] = 8*['Longitude:%s'%(Lon)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    
    data_text = data.to_csv(header=False, index=False, lineterminator='\n')
    path = parent_directory + os.sep + 'DATA' + os.sep + 'SAM_INPUTS' + os.sep + 'WIND'
    text_file = open(path + os.sep + "WindSource.srw", "w") # I got an error if use ./csv format for wind source
    text_file.write(data_text)
    text_file.close()
    print("Wind source data file was generated from Windlab database!")    

 #################################################################
def speed(Z,Z_anem,U_anem):
    """
    This function calculates the logarithmic wind speed as a function of 
    heigth
    
    Parameters
    ----------
    Z: height of interest
    Z_anem: anemometer heigth
    U_anem: wind speed at anemometer height

    Returns wind speed at Z
        
    """
    Z0 = 0.01
    U_H = U_anem * np.log(Z/Z0)/np.log(Z_anem/Z0)
    return(U_H)

    