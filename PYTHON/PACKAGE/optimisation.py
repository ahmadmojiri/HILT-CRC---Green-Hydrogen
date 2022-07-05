# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 10:28:44 2022

@author: Ahmad Mojiri
"""
from projdirs import optdir
import numpy as np
# import pdb

def make_dzn_file(DT, EL_ETA, BAT_ETA_in, BAT_ETA_out,
                  C_PV, C_WIND, C_EL, C_UG_STORAGE,UG_STORAGE_CAPA_MAX,
                  C_PIPE_STORAGE,PIPE_STORAGE_CAPA_MIN, C_BAT_ENERGY,
                  C_BAT_POWER, CF, PV_REF, PV_REF_POUT, WIND_REF,
                  WIND_REF_POUT, LOAD):

    # pdb.set_trace()    
    string = """
    N = %i;
    
    DT = %.2f;      %% time difference between sample points (hr)
    
    EL_ETA = %.2f;  %% conversion factor of the electrolyser
    BAT_ETA_in = %.2f;   %%charging efficiency of electrochemical battery
    BAT_ETA_out = %.2f;  %%discharging efficiency of electrochemical battery 
    
    C_PV = %.2f;    %% unit cost of PV ($/kW)
    C_WIND =  %.2f;    %% unit cost of Wind farm ($/kW)
    C_EL =  %.2f;    %% unit cost of electrolyser ($/kW)
    C_UG_STORAGE = %.2f;    %% unit cost of hydrogen storage ($/kgH)
    UG_STORAGE_CAPA_MAX = %.2f; %%maximum size of underground storage $/(kg of H2)
    C_PIPE_STORAGE = %.2f; %% unit cost of storage with line packing $/(kg of H2)
    PIPE_STORAGE_CAPA_MIN = %.2f; %% minimum size of line packing (kg of H2)
    
    C_BAT_ENERGY = %.2f;   %% unit cost of electrochemical battery energy ($/kWh)
    C_BAT_POWER = %.2f;   %% unit cost of electrochemical battery power ($/kWh)
    
    RES_H_CAPA = %.2f;       %% reserved hydrogen for lowered capcaity factor
    
    PV_REF = %.2f;       %%the capacity of the reference PV plant (kW)
    
    %% Power output time series from reference PV plant (W)
    PV_REF_POUT = %s;                                  
     
     
    WIND_REF = %.2f;  %% the capacity of the refernce wind plant (kW)
    
    %% power output time series from the reference wind plant (W)
    WIND_REF_POUT = %s;  
    
    %% load timeseries (kgH/s)                             
    LOAD = %s;                              
    """ %(len(LOAD), DT, EL_ETA, BAT_ETA_in, BAT_ETA_out,
      C_PV, C_WIND, C_EL, C_UG_STORAGE, UG_STORAGE_CAPA_MAX, C_PIPE_STORAGE,
      PIPE_STORAGE_CAPA_MIN, C_BAT_ENERGY,
      C_BAT_POWER,(1-CF)*sum(LOAD)*DT*3600, PV_REF, str(PV_REF_POUT), WIND_REF,
      str(WIND_REF_POUT), str(LOAD))

    with open(optdir + "hydrogen_plant_data.dzn", "w") as text_file:
        text_file.write(string)
        
        
#####################################################################
def optimise(simparams):
    """
    Parameters
    ----------
    simparams : a dictionary including the following parameters:
        DT, ETA_PV, ETA_EL, C_PV, C_W, C_E, C_HS, CF, pv_ref_capa,
                  W, pv_ref_out, L

    Returns
    -------
    a list of outputs including the optimal values for CAPEX, p-pv, p_w, p_e,
    e_hs

    """
    make_dzn_file(**simparams)
    mzdir = r'C:\\Program Files\\MiniZinc\\'
    from subprocess import check_output
    output = str(check_output([mzdir + 'minizinc', "--soln-sep", '""',
                               "--search-complete-msg", '""', "--solver",
                               "COIN-BC", optdir + "hydrogen_plant.mzn",
                               optdir + "hydrogen_plant_data.dzn"]))
    
    output = output.replace('[','').replace(']','').split('!')
    for string in output:
        if 'CAPEX' in string:
            results = string.split(';')
    
    results = list(filter(None, results))
    
    RESULTS = {}
    for x in results:
        RESULTS[x.split('=')[0]]=np.array((x.split('=')[1]).split(',')).astype(float)        
    
    return(  RESULTS  )


######################################################################

