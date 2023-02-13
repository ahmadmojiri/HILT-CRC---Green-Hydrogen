# -*- coding: utf-8 -*-
"""
@author: Ahmad Mojiri
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import os
from assets.component_model import SolarResource, WindSource_windlab
from assets.optimisation import Optimise
from assets.plotting import prep_results_to_print, prep_results_to_plot
import pdb

colors = {'background': 'whitesmoke',
          'text': 'black'}

# locations = [{'label':'Newman','value':'Newman'},
#              {'label':'Tom Price','value':'Tom_Price'},
#              {'label':'Whyalla','value':'Whyalla'},
#              {'label':'Gladstone','value':'Gladstone'},
#              {'label':'Pinjara','value':'Pinjara'},
#              {'label':'Port Agusta','value':'Port_Augusta'},
#              {'label':'Burnie','value':'Burnie'},]


locations = [{'label':'Burnie 1', 'value':'Burnie 1'},
             {'label':'Burnie 2', 'value':'Burnie 2'},
             {'label':'Burnie 3','value':'Burnie 3'},
             {'label':'Burnie 4','value':'Burnie 4'},
             {'label':'Gladstone 1','value':'Gladstone 1'},
             {'label':'Gladstone 2','value':'Gladstone 2'},
             {'label':'Gladstone 3','value':'Gladstone 3'},
             {'label':'Pilbara 1','value':'Pilbara 1'},
             {'label':'Pilbara 2','value':'Pilbara 2'},
             {'label':'Pilbara 3','value':'Pilbara 3'},
             {'label':'Pilbara 4','value':'Pilbara 4'},
             {'label':'Pinjara 1','value':'Pinjara 1'},
             {'label':'Pinjara 2','value':'Pinjara 2'},
             {'label':'Pinjara 3','value':'Pinjara 3'},
             {'label':'Pinjara 4','value':'Pinjara 4'},
             {'label':'Upper Spencer Gulf 1','value':'Upper Spencer Gulf 1'},
             {'label':'Upper Spencer Gulf 2','value':'Upper Spencer Gulf 2'},
             {'label':'Upper Spencer Gulf 3','value':'Upper Spencer Gulf 3'},
             {'label':'Upper Spencer Gulf 4','value':'Upper Spencer Gulf 4'},
             {'label':'Darwin','value':'Darwin'}]

results_var = [{'label':'PV output', 'value':'pv_pout'},
               {'label':'Wind output', 'value':'wind_pout'},
               {'label':'Curtailed power', 'value':'curtail_p'},
               {'label':'Battery input power', 'value':'bat_pin'},
               {'label':'Battery output power', 'value':'bat_pout'},
               {'label':'Electrolyser input power', 'value':'el_pin'},
               {'label':'Compressor 1 H2 flow', 'value':'comp1_hflow'},
               {'label':'Compressor 2 H2 flow', 'value':'comp2_hflow'},
               {'label':'Compressor 2 input power', 'value':'comp2_pin'},
               {'label':'Reduced H2 output', 'value':'res_hout'},
               {'label':'Pipe H2 output', 'value':'pipe_storage_hout'},
               {'label':'UG H2 output', 'value':'ug_storage_hout'},
               {'label':'UG storage level', 'value':'ug_storage_level'},
               {'label':'Pipe storage level', 'value':'pipe_storage_level'},
               {'label':'Shutdown allowance level', 'value':'reserve_h_level'},
               {'label':'Battery charge level', 'value':'bat_e'},
               {'label':'Load', 'value':'LOAD'},]

storage_types = [{'label':'Salt Cavern','value':'Salt Cavern'},
                 {'label':'Lined Rock Cavern','value':'Lined Rock'}]

Layout= {'xaxis':{'showline':True, 'linewidth':1.25,
                  'mirror':True,'linecolor':'black',
                  'nticks':20, 'tickangle':30,
                  'gridcolor':'LightPink'},
         'yaxis':{'showline':True, 'linewidth':1.25,
                  'mirror':True,'gridcolor':'LightPink'},
         'legend':{'yanchor':"bottom", 'y':1,
                   'xanchor':"left",'x':0.1,'orientation':'h'},
                   'plot_bgcolor': colors['background'],
           'title':'',
           'font': {'color': colors['text']}  }



app = dash.Dash(__name__,requests_pathname_prefix='/app/')

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

server=app.server



app.layout = html.Div([
            dbc.Row(dbc.Col(html.H1('Green H2'),
                            width={'size':6, 'offset':5}
                      )),
            
            dbc.Row(dbc.Col(html.H2('Solar Thermal Group - Australian National University'),
                            width={'size':7, 'offset':3}
                      )),
            
            
            dbc.Row([
                     dbc.Col(children= html.Div('Electrolyser efficiency:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     
                     dbc.Col(dcc.Input(id="EL_ETA", type="number",
                                       value=0.7,
                                       min=0.5,
                                       max=1.0,
                                       step=0.1,
                                       style={}),
                             width={'size':1, 'offset':0}
                             ),
                     
                     
                     
 #Location                     
                     dbc.Col(dcc.Loading(
                                id="Lolcation_Status",
                                type="default",
                                children= html.Div('None has been selected!',
                                                   id='location_status',
                                                   style={'textAlign': 'right'})),
                             width={'size':2, 'offset':1}
                             ),
                     
                     dbc.Col(dcc.Dropdown( id='location_selector',
                                          options=locations,
                                          multi=False,
                                          searchable=True,
                                          placeholder='Select a location!'
                                    ),width={'size':2, 'offset':0}
                                 ),
                    
                     ]),

   
            
#Battery charging efficiency            
            dbc.Row([dbc.Col(children= html.Div('Battery charging efficiency:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     
                     dbc.Col(dcc.Input(id="BAT_ETA_IN", type="number",
                                       value=0.95,
                                       min=0.1, max=1.0,
                                       step=0.05, style={}),
                             width={'size':1, 'offset':0}
                             ),
 #Storage type             
            dbc.Col(children= html.Div('UG Storage type:',
                                       style={'textAlign': 'right'}),
                width={'size':2, 'offset':1}
                ),
                     
            dbc.Col(dcc.Dropdown( id='storage_selector',
                                 options=storage_types,
                                 multi=False,
                                 searchable=True,
                                 placeholder='Select UG storage'
                           ),width={'size':2, 'offset':0}
                        ),
                     ]),



                     
   
            
#Battery discharging efficiency            
            dbc.Row([
                    dbc.Col(children= html.Div('Battery discharging efficiency:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                    
                     dbc.Col(dcc.Input(id="BAT_ETA_OUT", type="number",
                                       min=0.1, max=1.0,
                                       value=0.95,
                                       step=0.05, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     
                     
                     ]),

            
#Cost of PV            
            dbc.Row([
                    dbc.Col(children= html.Div('Unit cost of PV:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="C_PV", type="number",
                                       min=0.0,
                                       value=1122,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),
            
            
#Cost of Wind            
            dbc.Row([
                    dbc.Col(children= html.Div('Unit cost of Wind:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="C_WIND", type="number",
                                       min=0.0,
                                       value=1455,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),


            
#Cost of Electrolyser            
            dbc.Row([
                    dbc.Col(children= html.Div('Unit cost of Electrolyser:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="C_EL", type="number",
                                       min=0.0,
                                       value=1067,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),
            
#UG_STORAGE_CAPA_MAX            
            dbc.Row([
                    dbc.Col(children= html.Div('UG storage max capacity:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="UG_STORAGE_CAPA_MAX", type="number",
                                       min=0.0,
                                       value=1e8,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('kg of H2',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),
            
            
#C_PIPE_STORAGE            
            dbc.Row([
                    dbc.Col(children= html.Div('Unit cost of pipe storage:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="C_PIPE_STORAGE", type="number",
                                       min=0.0,
                                       value=516,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kg of H2',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),
            
            
#PIPE_STORAGE_CAPA_MIN            
            dbc.Row([
                    dbc.Col(children= html.Div('Pipe storage min capacity:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="PIPE_STORAGE_CAPA_MIN", type="number",
                                       min=0.0,
                                       value=1e5,
                                       step=1000, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('kg of H2',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),
            
   
            
#C_BAT_ENERGY            
            dbc.Row([
                    dbc.Col(children= html.Div('Battery energy unit price:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="C_BAT_ENERGY", type="number",
                                       min=0.0,
                                       value=196,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kWh',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1})
                     ]),
            

#C_BAT_POWER            
            dbc.Row([
                    dbc.Col(children= html.Div('Battery power unit price:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="C_BAT_POWER", type="number",
                                       min=0,
                                       value=405,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
#CF            
            dbc.Row([
                    dbc.Col(children= html.Div('Capcaity factor:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="CF", type="number",
                                       min=1, max=100,
                                       value=100,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('Percent[%]',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
            
            
#Load            
            dbc.Row([
                    dbc.Col(children= html.Div('Load:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="LOAD", type="number",
                                       min=0.0,
                                       value=5.0,
                                       step=0.05, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('kgH2/s',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
            
           


#Run optimisation
            dbc.Row([dbc.Col(html.Button('Optimise!',
                                         id='Optimise',
                                         n_clicks=0),
                                width={'size':1, 'offset':1}
                                   ),
                     
#print results
                    
                     dbc.Col(dcc.Loading(
                                    id="OPTIMISATION_TEXT",
                                    type="default",
                                    children= html.Div('Progress!',
                                                       id='optimisation_text')),
                                 width={'size':1, 'offset':0}
                                 ),
            
                    dbc.Col(dcc.Textarea(id='Output',
                                         value='',
                                         readOnly=True,
                                         style={'width':'100%','height':200}
                                         ),
                                         width={'size':3, 'offset':2}
                            
                            ),
            
                     ]),
            
#Export output
            dbc.Row([
                
                dbc.Col([html.Button('Export!', id='export', n_clicks=0),
                        dcc.Download(id='download_csv')],
                                width={'size':1, 'offset':5}
                                   )
                     ]),
            
             
#Choose plotting variabe
           
            dbc.Row(dbc.Col(dcc.Dropdown( id='variable_selector',
                                          options=results_var,
                                          multi=True,
                                          searchable=True,
                                          placeholder='Choose a variable!'
                                    ),width={'size':2, 'offset':1}
                                 ),
                    ),
            
#Download timeseries
            dbc.Row([
                
                dbc.Col([html.Button('Download data!', id='download', n_clicks=0),
                        dcc.Download(id='download_data_csv')],
                                width={'size':1, 'offset':1}
                                   )
                     ]),
            
            
            dbc.Row(dbc.Col(dcc.Graph(id='GraphI',figure={'data':[]}),
                            width={'size':10, 'offset':1}
                        )),
            

            
#Interest rate            
            dbc.Row([
                    dbc.Col(children= html.Div('Interest rate:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="interest_rate", type="number",
                                       min=0.0,
                                       value=7.8,
                                       step=0.1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('Percent [%]',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
            
#Lifetime            
            dbc.Row([
                    dbc.Col(children= html.Div('Lifetime:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="lifetime", type="number",
                                       min=0.0,
                                       value=25,
                                       step=1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('Years',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),

#FOM PV            
            dbc.Row([
                    dbc.Col(children= html.Div('FOM PV:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="pv_fom", type="number",
                                       min=0.0,
                                       value=12.7,
                                       step=0.1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),



#FOM WIND            
            dbc.Row([
                    dbc.Col(children= html.Div('FOM Wind:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="wind_fom", type="number",
                                       min=0.0,
                                       value=18.7,
                                       step=0.1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
            

#FOM Electrolyser            
            dbc.Row([
                    dbc.Col(children= html.Div('FOM Electrolyser:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="elec_fom", type="number",
                                       min=0.0,
                                       value=37.3,
                                       step=0.1, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kW',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),


#VOM PV            
            dbc.Row([
                    dbc.Col(children= html.Div('VOM PV:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="pv_vom", type="number",
                                       min=0.0,
                                       value=0,
                                       step=0.001, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kWh',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),



#VOM WIND            
            dbc.Row([
                    dbc.Col(children= html.Div('VOM Wind:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="wind_vom", type="number",
                                       min=0.0,
                                       value=0,
                                       step=0.001, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kWh',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
            

#VOM Electrolyser            
            dbc.Row([
                    dbc.Col(children= html.Div('VOM Electrolyser:',
                                                style={'textAlign': 'right'}),
                             width={'size':2, 'offset':0}
                             ),
                     dbc.Col(dcc.Input(id="elec_vom", type="number",
                                       min=0.0,
                                       value=0.075,
                                       step=0.001, style={}),
                             width={'size':1, 'offset':0}
                             ),
                     dbc.Col(children= html.Div('USD/kWh',
                                                style={'textAlign': 'left'}),
                             width={'size':1, 'offset':1}
                             ),
                     ]),
            
            
#Calculate LCOH2
            dbc.Row([dbc.Col(html.Button('Calculate LCOH2!',
                                         id='LCOH2',
                                         n_clicks=0),
                                width={'size':1, 'offset':2}
                                   )
                     ]),
            
            
#plot LCOH2            
            dbc.Row(dbc.Col(dcc.Graph(id='graph_LCOH2',figure={'data':[]}),
                            width={'size':5, 'offset':1}
                        )),


            ])









              

#-------------------------------------
@app.callback(
            [Output('OPTIMISATION_TEXT','children'),
             Output('Output', 'value')],
            [Input('Optimise','n_clicks'),
             State('EL_ETA', 'value'),
             State('BAT_ETA_IN', 'value'),
             State('BAT_ETA_OUT', 'value'),
             State('C_PV', 'value'),
             State('C_WIND', 'value'),
             State('C_EL', 'value'),
             State('UG_STORAGE_CAPA_MAX', 'value'),
             State('C_PIPE_STORAGE', 'value'),
             State('PIPE_STORAGE_CAPA_MIN', 'value'),
             State('C_BAT_ENERGY', 'value'),
             State('C_BAT_POWER', 'value'),
             State('LOAD', 'value'),
             State('CF', 'value'),
             State('location_selector','value'),
             State('storage_selector','value')],
             prevent_initial_call=True
            )
def optimise(click, el_eta, bat_eta_in, bat_eta_out, c_pv, c_wind, c_el,
             ug_storage_capa_max, c_pipe_stprage, pipe_storage_capa_min,
             c_bat_energy, c_bat_power, load, cf, location, storage_type):
      try:
          SolarResource(location)
      except:
          text = 'Error: Choose a location!'
          results_to_print = 'None'
      else:
          SolarResource(location)
          WindSource_windlab(location)
          simparams = dict(EL_ETA = el_eta,       
                           BAT_ETA_in = bat_eta_in, 
                           BAT_ETA_out = bat_eta_out,  
                           C_PV = c_pv,          
                           C_WIND = c_wind,        
                           C_EL = c_el,          
                           UG_STORAGE_CAPA_MAX = ug_storage_capa_max, 
                           C_PIPE_STORAGE = c_pipe_stprage,
                           PIPE_STORAGE_CAPA_MIN = pipe_storage_capa_min, 
                           C_BAT_ENERGY = c_bat_energy,        
                           C_BAT_POWER = c_bat_power,        
                             ) 
          text = 'Completed!'
          results = Optimise(load, cf, storage_type, simparams)
          global RESULTS
          RESULTS = prep_results_to_print(results,simparams)
          
          OUTPUT = str(RESULTS).replace(', ',',\n ').replace('{', '').replace('}', '').replace("'",'').replace(',','')
          
          global data_to_plot
          data_to_plot = prep_results_to_plot(results, simparams, location)
      SolarResource(location)    
      return ([text,OUTPUT])





#Choose the location and update weather data
@app.callback(
            [Output('location_status','children')],
            [Input('location_selector','value')],
            prevent_initial_call=True
             )
def update_weather_data(location):
    try:
        SolarResource(location)
    except:
        text = '%s has been selected'%(location)
    else:
        SolarResource(location)
        WindSource_windlab(location)
        text = 'Weather data updated!'
    return([text])
            


#Export the results
@app.callback(Output("download_csv", "data"),
              Input("export", "n_clicks"),
              prevent_initial_call=True,
              )
def export(n_clicks):
    data = pd.DataFrame(RESULTS,index=[0])
    return dcc.send_data_frame(data.to_csv, "Results.csv")




#Download Timeseries
@app.callback(Output("download_data_csv", "data"),
              Input("download", "n_clicks"),
              State('variable_selector','value'),
              prevent_initial_call=True,
              )
def download(n_clicks,variables):
    cols = ['time'] + variables
    data = data_to_plot[cols]
    return dcc.send_data_frame(data.to_csv, "Timeseries.csv")




#plot the selected variables
@app.callback(
            [Output('GraphI', 'figure')],
            [Input('variable_selector','value')],
            prevent_initial_call=True
             )
def update_graph(variables):
      plot_data=[]
      chart={'data': plot_data}            
      for col in variables:
          plot_data = plot_data + [go.Scatter(x=data_to_plot.time,
                                              y=data_to_plot[col],
                                              name=col)]
          layoutI = Layout.copy()
          chart={'data': plot_data,
                 'layout': layoutI }
      
      return([chart])

            


if __name__ == '__main__':
     app.run_server(debug=False,host='0.0.0.0')
