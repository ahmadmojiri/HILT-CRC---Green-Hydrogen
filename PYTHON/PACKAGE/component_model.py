# -*- coding: utf-8 -*-
"""
Created on Fri May  6 12:46:54 2022

@author: Ahmad Mojiri
"""
from projdirs import datadir

import numpy as np
import pandas as pd
import json, io, requests
import PySAM.Pvwattsv8 as PVWatts, Windpower

################################################################
def pv_gen(capacity):
    """
    Parameters
    ----------
    capacity in W

    Returns system powr generated in W for each hour in a year
    
    """
    pv = PVWatts.new()
    
    dir = datadir + '\SAM INPUTS\SOLAR\\'
    file_name = 'pvfarm_pvwattsv8'
    module = pv
    
    with open(dir + file_name + ".json", 'r') as file:
        data = json.load(file)
        for k,v in data.items():
            if k != "number_inputs":
                module.value(k, v)
    
    module.SystemDesign.system_capacity = capacity/1000
    pv.execute()
    output = np.array(pv.Outputs.gen)*1000
    return(output.tolist())

#################################################################
def wind_gen():
    """
    Parameters
    ----------
    Capacity will be added later

    Returns wind powr generated in W for each hour in a year
    
    """
    wind = Windpower.new()
    
    dir = datadir + '\SAM INPUTS\WIND\\'
    file_name = 'windfarm_windpower'
    module = wind
    
    with open(dir + file_name + ".json", 'r') as file:
        data = json.load(file)
        for k,v in data.items():
            if k != "number_inputs":
                module.value(k, v)
    
    # module.SystemDesign.system_capacity = capacity/1000
    wind.execute()
    output = np.array(wind.Outputs.gen)*1000
    return(output.tolist())

#################################################################
def WindSource(Lat,Lon):
    """
    The function gets the TMY data from PVGIS:
        API = https://re.jrc.ec.europa.eu/api/v5_2/tmy
    
    Parameters
    ----------
    lat: Latitude
    long: longitude

    Returns a csv file in .srw format for wind farm modelling in SAM
        
    """
    url = 'https://re.jrc.ec.europa.eu/api/v5_2/tmy'

    Params = {'lat':Lat,
              'lon':Lon}
    
    response = requests.get(url,params=Params)
    print('Status:', response.status_code)
    response.close()
    text = response.text
    
    text2 = 'time(UTC)'+ text.split('\ntime(UTC)')[1]
    text3 = text2.replace('\r\n\r\n','').split('T2m:')[0]
    
    data = io.StringIO(text3)
    data = pd.read_csv(data)
    data_10 = data.iloc[:,[1,7,8,9]].copy()
    data_10.SP=data_10.SP/101325
    data_10 = data_10.rename(columns = {'T2m':'T', 'WS10m':'S', 'WD10m':'D', 'SP':'P'})
    heading_10 = pd.DataFrame({'T':['Temperature','C',10], 'S':["Speed", 'm/s',10],
                               'D':["Direction",'degrees',10], 'P':['Pressure','atm',10]})
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
    
    data.loc[-1] = 16*['Latitude:%d'%(Lat)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    data.loc[-1] = 16*['Longitude:%d'%(Lon)]
    data.index = data.index+1
    data.sort_index(inplace=True)
    
    data_text = data.to_csv(header=False, index=False, line_terminator='\n')
    # data_text = 'Latitude:%d'%(Lat)+'\n' + 'Longitude:%d'%(Lon)+'\n' + data_text
    path = r'C:\Nextcloud\HILT-CRC---Green-Hydrogen\DATA\SAM INPUTS\WIND'
    
    text_file = open(path + "\WindSource.csv", "w")
    text_file.write(data_text)
    text_file.close()
    return('Wind source file was created!')
    
##################################################################
def SolarResource(Lat,Lon):
    """
    The function gets the TMY data from PVGIS:
        API = https://re.jrc.ec.europa.eu/api/v5_2/tmy
    
    Parameters
    ----------
    lat: Latitude
    long: longitude

    Returns a epw file in .epw format for PV modelling in SAM
        
    """
    url = 'https://re.jrc.ec.europa.eu/api/v5_2/tmy'

    Params = {'lat':Lat,
              'lon':Lon,
              'outputformat':'epw'}
    
    response = requests.get(url,params=Params)
    print('Status:', response.status_code)
    response.close()
    
    data_text = response.text.replace('\r','')
    path = r'C:\Nextcloud\HILT-CRC---Green-Hydrogen\DATA\SAM INPUTS\SOLAR'
    text_file = open(path + "\SolarSource.epw", "w")
    text_file.write(data_text)
    text_file.close()
    return('Solar source file was created!') 
    
    
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
    Z0 = 0.003
    U_H = U_anem * np.log(Z/Z0)/np.log(Z_anem/Z0)
    return(U_H)   