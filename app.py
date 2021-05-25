#!/usr/bin/env python
# coding: utf-8

# # Uttarakhand Industrial Information System
#
# Last Modified: 12/03/2021
#
# Author: Manaruchi Mohapatra

# ### Import Required Libraries


import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import os
import dash_table
import base64
import smtplib, ssl
from glob import glob
import flask
import random

# ### Files Setup


cur_path = os.getcwd()
#---------------Paths------------------------------------------------------
area_list_csv_path = os.path.join(cur_path, 'support_files', 'area_list.csv')
#--------------------------------------------------------------------------

with open(os.path.join(cur_path, 'json', 'DIS_Merged_for_Dash.geojson')) as f:
    dis_json = json.load(f)

#Data for main basic map
df = pd.read_csv(os.path.join(cur_path, 'json', 'data.csv'))

#Data for search dropdown content
area_list_df = pd.read_csv(area_list_csv_path)
area_list = area_list_df['label']

#Data for basemaps list
basemap_list_df = pd.read_csv(os.path.join(cur_path, 'support_files', 'basemap_list.csv'))
basemap_list_dict = [{'label': r[0], 'value': r[1]} for i,r in basemap_list_df.iterrows()]

#Data for Plot Details
plot_details_df = pd.read_csv(os.path.join(cur_path, 'support_files', 'plot_details.csv'))
plot_details_col_list = plot_details_df.columns
plot_details_UID_list = plot_details_df['UID'].values

#Data for Plot Details - Administrator Mode
plot_details_admin_file = os.path.join(cur_path, 'support_files', 'plot_details.csv')
plot_details_admin_df = pd.read_csv(plot_details_admin_file)
for c in plot_details_admin_df.columns:
    if(c[:7] == 'Unnamed'):
        plot_details_admin_df = plot_details_admin_df.drop([c],axis = 1)

#Data for User Info
user_info_csv_path = os.path.join(cur_path, 'support_files', 'user_list.csv')

#Graphics Folder
graphics_folder_path = os.path.join(cur_path, 'graphics')

#Additional Data Layers folder
addnl_data_layer = os.path.join(cur_path, 'additional_layers')

#Uttarakhand District JSON
with open(os.path.join(cur_path, 'json', 'uk_district.geojson')) as f:
    z = json.load(f)

#Park Names CSV
park_names_position_path = os.path.join(cur_path, 'support_files', 'park_names_position.csv')
park_details_csv_path = os.path.join(cur_path, 'support_files', 'park_details.csv')

#Download Folder
download_files_container_folder = os.path.join(cur_path, 'download_content')

# ## Setup for SMTP


port = 465  # For SSL
password = "RBS@1234"

sender_email = "jjjhkrmntest@gmail.com"


# ### Dash App Definition


FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.COSMO, FONT_AWESOME,
                                              'https://fonts.googleapis.com/css2?family=Roboto&display=swap'], update_title=None)

app.title = "Uttarakhand Industrial Information System"


# ## Global Variables


is_logged_in = False
session_user_name = ''
user_info_dict = {'First Name': '',
                  'Middle Name': '',
                  'Last Name': '',
                  'DOB': ''}


# ## App Layout


header_elements = [
                html.Div(html.H1('Uttarakhand Industrial Information System', className = 'navbar-brand'), className = 'navbar-brand-bar'),
                html.Div([

                    html.Img(src = 'http://www.rbasedservices.com/wp-content/uploads/2020/06/cropped-RBS_LOGO.png', className = 'navbar-logo', id = 'rbs-logo'),
                    html.Img(src = 'https://www.siidcul.com/upload/header/SIIDCUL.jpg', className = 'navbar-logo'),
                    html.Img(src = 'https://www.saferspaces.org.za/cache/ce_img_cache/local/520d1943832aab5c/German-Cooperation-GIZ-topdown1_270_232_80.jpg', className = 'navbar-logo', id = 'giz-logo'),
                    html.Img(src = 'https://www.siidcul.com/upload/header/SIIDCUL.jpg', className = 'navbar-logo', id = 'siidcul-logo'),
                    dbc.Tooltip("State Industrial Development Corporation of Uttarakhand Limited", target = 'siidcul-logo'),
                    dbc.Tooltip("Deutsche Gesellschaft für Internationale Zusammenarbeit", target = 'giz-logo'),
                    dbc.Tooltip("RBased Services Pvt. Ltd.", target = 'rbs-logo')

                ], className = 'navbar-logo-bar')
            ]



page_layout = html.Div([

    dcc.Location(id='url', refresh=False),

    html.Div(header_elements, className = 'mainheader'),

    html.Div(className = 'navlinks', id='navlinkscallback'),

    dbc.Row(no_gutters=True, className = 'mainarea', id='mainareacallback'),

], className = 'mainbody')


# ### Layout for Basic Web Map


fig = px.choropleth_mapbox(df, geojson=dis_json, locations='id',
                           color_continuous_scale="Viridis",
                           zoom=10, center = {"lat": 29.561, "lon": 78.663},
                           opacity=0.5,
                           labels={'Plot_No':'Plot Number'},
                           hover_data = ['Plot_No', 'UID']
                          )



fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "Google, RBS Pvt. Ltd.",
            "source": [
                "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
            ]
        }
      ])

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update(layout_showlegend=False)

#------------------Search Overlay--------------------------------------------------------
area_list_options = []

for area in area_list:
    area_list_options.append({'label': area, 'value': area})

card_content_1 = [
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(html.I(className="fas fa-search-location fa-2x", id = 'search-icon'), width = 1),
                     dbc.Col(dcc.Dropdown(
                options=area_list_options,
                id = 'area_list_combo',
                className = 'search-combobox',
                value = "All"
            ), width = 10)]),



        ], className = 'searchbox'
    ),
]

card_search = dbc.Card(card_content_1, color="dark", inverse=True)

search_overlay_div = html.Div([

    card_search


    ] ,className = 'search-overlay')


#----------------------------------------------------------------------------------------

#-------------------Settings Overlay-----------------------------------------------------

settings_overlay_div = html.Div([

    dbc.Button(html.I(className = 'fas fa-sliders-h'), color = 'link', id = 'settings-collapse-button'),
    dbc.Tooltip("Basemap and Layer Settings",target = 'settings-collapse-button')
    ] ,className = 'settings-overlay')

settings_overlay_div_expanded = html.Div([

    dbc.Collapse([

            html.P('Basemap', className = 'overlay-form-labels'),
            dbc.Select(id = 'basemap-xyz-input', options = basemap_list_dict, value = "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}", className = 'settings-inp'),
            html.P('Layer Opacity', className = 'overlay-form-labels'),
            dbc.Input(id = 'opacity-input', className = 'settings-inp', value = 0.5, type = 'number',min=0, max=1, step = 0.05),


        ], id = 'settings-exp')

    ] ,id = 'settings-overlay-expanded')

#----------------------------------------------------------------------------------------


#------------------Legend Overlay--------------------------------------------------------

legend_div_contents = [dbc.FormGroup([dbc.Checkbox(id='KV11-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#abfd00', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), '11KV'], html_for='KV11-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='KV33-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#b41080', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), '33KV'], html_for='KV33-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Bridge-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#2268fe', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Bridge'], html_for='Bridge-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Compline-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#67081a', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Compline'], html_for='Compline-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Eline-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#918a00', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Eline'], html_for='Eline-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Footpath-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#7ab0c2', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Footpath'], html_for='Footpath-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='LTLine-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#b54435', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'LTLine'], html_for='LTLine-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Railways-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#d76920', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Railways'], html_for='Railways-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='River-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#0a26a8', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'River'], html_for='River-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Roads-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#F00', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Roads'], html_for='Roads-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Water-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '5px','width': '15px','background-color': '#4a34f1', 'display': 'inline-block','margin-right': '10px','margin-bottom': '4px'}), 'Water'], html_for='Water-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='EPole-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '10px','width': '10px','background-color': '#29bf23', 'border-radius': '50%', 'display': 'inline-block','margin-right': '10px'}), 'EPole'], html_for='EPole-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Label-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '10px','width': '10px','background-color': '#262a61', 'border-radius': '50%', 'display': 'inline-block','margin-right': '10px'}), 'Label'], html_for='Label-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,
dbc.FormGroup([dbc.Checkbox(id='Manhole-checkbox', className='form-check-input', checked = True), dbc.Label([html.Span(style = {'height': '10px','width': '10px','background-color': '#d874be', 'border-radius': '50%', 'display': 'inline-block','margin-right': '10px'}), 'Manhole'], html_for='Manhole-checkbox', className='form-check-label',),], style = {'opacity': 1}, check=True) ,]

legend_names_list = ['11KV', '33KV', 'Bridge', 'Compline', 'Eline', 'Footpath', 'LTLine', 'Railways', 'River', 'Roads', 'Water', 'EPole', 'Label', 'Manhole', 'Fire_Stations', 'Vegetation']
legend_colors_list = ['#abfd00', '#b41080', '#2268fe', '#67081a', '#918a00', '#7ab0c2', '#b54435', '#d76920', '#0a26a8', '#F00', '#4a34f1', '#29bf23', '#262a61', '#d874be', '#482010', '#60a14f']
legend_types_list = ['Line', 'Line', 'Line', 'Line', 'Line', 'Line', 'Line', 'Line', 'Line', 'Line', 'Line', 'Point', 'Point', 'Point', 'Poly', 'Poly']




legend_overlay_div = html.Div([

    html.P('Layers', id = 'legend-layer-caption'),
    html.Div(legend_div_contents, style = {'height':'140px', 'overflow-y':'auto'})


    ] ,className = 'legend-overlay')


#----------------------------------------------------------------------------------------




mapfig = html.Div([search_overlay_div, settings_overlay_div, legend_overlay_div, settings_overlay_div_expanded, dcc.Graph(figure = fig, style = {'height': '100%'}, id = 'basic-map')], className = 'map-first-page')

@app.callback(
    Output("settings-exp", "is_open"),
    [Input("settings-collapse-button", "n_clicks")],
    [State("settings-exp", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("basic-map", "figure"),
    [Input("area_list_combo", "value"), Input('basemap-xyz-input', 'value'),
    Input('opacity-input', 'value'),
    Input('KV11-checkbox', 'checked'),
    Input('KV33-checkbox', 'checked'),
    Input('Bridge-checkbox', 'checked'),
    Input('Compline-checkbox', 'checked'),
    Input('Eline-checkbox', 'checked'),
    Input('Footpath-checkbox', 'checked'),
    Input('LTLine-checkbox', 'checked'),
    Input('Railways-checkbox', 'checked'),
    Input('River-checkbox', 'checked'),
    Input('Roads-checkbox', 'checked'),
    Input('Water-checkbox', 'checked'),
    Input('EPole-checkbox', 'checked'),
    Input('Label-checkbox', 'checked'),
    Input('Manhole-checkbox', 'checked'),
    
     ])
def load_basic_map(area, xyz, opac, KV11_val, KV33_val, Bridge_val, Compline_val, Eline_val, Footpath_val, LTLine_val, 
                  Railways_val, River_val, Roads_val, Water_val, EPole_val, Label_val, Manhole_val):

    layers_which_are_active = []

    if(KV11_val): layers_which_are_active.append('11KV')
    if(KV33_val): layers_which_are_active.append('33KV')
    if(Bridge_val): layers_which_are_active.append('Bridge')
    if(Compline_val): layers_which_are_active.append('Compline')
    if(Eline_val): layers_which_are_active.append('Eline')
    if(Footpath_val): layers_which_are_active.append('Footpath')
    if(LTLine_val): layers_which_are_active.append('LTLine')
    if(Railways_val): layers_which_are_active.append('Railways')
    if(River_val): layers_which_are_active.append('River')
    if(Roads_val): layers_which_are_active.append('Roads')
    if(Water_val): layers_which_are_active.append('Water')
    if(EPole_val): layers_which_are_active.append('EPole')
    if(Label_val): layers_which_are_active.append('Label')
    if(Manhole_val): layers_which_are_active.append('Manhole')

    area_list_df = pd.read_csv(area_list_csv_path)

    fig = px.choropleth_mapbox(df, geojson=dis_json, locations='id',
                        color_continuous_scale="Viridis",
                        zoom=area_list_df[area_list_df['label'] == area]['zoom'].values[0],
                        center = {"lat": area_list_df[area_list_df['label'] == area]['lat'].values[0],
                                            "lon": area_list_df[area_list_df['label'] == area]['lon'].values[0]},
                        opacity=float(opac),
                        labels={'Plot_No':'Plot Number'},
                        hover_data = ['Plot_No', 'UID']
                        )
    
    #Add District Layer

    dist_df = pd.DataFrame()
    dist_df['id'] = [x['id'] for x in z['features']]

    fig.add_trace(go.Choroplethmapbox(geojson=z, locations=dist_df.id, featureidkey = 'properties.dtname', z = dist_df.index,
                                    colorscale="Viridis", showscale=False, name="",
                                    marker_opacity=0, marker_line_width=2))

    for feature in z['features']:
        lats = []
        lons = []
        for cp in feature['geometry']['coordinates'][0]:
            lats.append(cp[1])
            lons.append(cp[0])
            
        fig.add_trace(go.Scattermapbox(
                            lat=lats,
                            lon=lons,
                            mode="lines",
                            hoverinfo='skip',
                            line=dict(width=2, color="#000000")
                        ))

    #Add Additional Layers
    addnl_layers_list = glob(os.path.join(addnl_data_layer, '*.csv'))

    for addnl_f in addnl_layers_list:
        fname = os.path.split(addnl_f)[1][:-4]
        l_type = fname.split('_')[0]
        l_name = fname.split('_')[1]
        l_color = fname.split('_')[2]

        addnl_layers_df = pd.read_csv(addnl_f)

        if(l_type == 'Line'):

            if(l_name in layers_which_are_active):

                fig.add_trace(go.Scattermapbox(
                    lat=addnl_layers_df['lat'],
                    lon=addnl_layers_df['lon'],
                    mode="lines",
                    text=addnl_layers_df['name'],
                    hoverinfo = 'text',
                    showlegend=False,
                    line=dict(width=2, color=l_color)
                ))

        elif(l_type == 'Point'):

            if(l_name in layers_which_are_active):

                fig.add_trace(go.Scattermapbox(
                    lat=addnl_layers_df['lat'],
                    lon=addnl_layers_df['lon'],
                    text=addnl_layers_df['name'],
                    hoverinfo = 'text',
                    showlegend=False,
                    line=dict(width=2, color=l_color)
                ))

        


    # #Add Roads Layer
    # addnl_layers_road_df = pd.read_csv(os.path.join(addnl_data_layer, 'all_roads_csv.csv'))

    

    

    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "Google, RBS Pvt. Ltd.",
                "source": [
                    xyz
                ]
            }
            ])

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update(layout_showlegend=False)

    data_list = list(fig.data)

    data_list_0 = data_list[0]
    data_list_1 = data_list[1]

    data_list[0] = data_list_1
    data_list[1] = data_list_0

    fig.data = tuple(data_list)

    return fig


#------------------Details Panel Content--------------------------------------

analysis_graphic = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7N11mFzl3f/x98zarEvc3YhCgkRIgjuFtrS4SwWnhaeGtNAf+rRQ2gdCcbfilKKB4AmahBDiQnbj674zvz9OUgIkWbnvM0fm87quvUhL5nu+JLtzPnOfW0BERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERES+K+J1AyI+FgP6Av2BrkAnoGTLP7d+dQYKt/z+dCB/y6+zgJwtv64BGrf8evOWfzYB1cAmYAOw8Ttf64FVwHKg3vJ/l4iIAoCkvAJgJDAaGAj02/LVH+jhXVvfUgoswwkDW//5JTAXqPCsKxEJNAUASRURYDgwDudmPxoYhXOjD7LlOEFgLvDZln9+BbR42JOIBIACgIRVLrArMBmYAuyFM1yfCqpxwsDbwDvALKDc045ExHcUACQscoFpwEFb/jkKSPO0I/9oBj7FCQOvAa/jzEsQkRSmACBBNhDYHzhiyz9j3rYTGM3AB8BzwKvAx0DC045ERER2Ih3nRn8bsAbnpqUv86/lW/5MD0CjJiIi4hNpOM/wbwbK8P5mGfavjcB9OKMq6W34+xEREbFqCvBPnBuS1zfFVP0qBf6GM5FSRETENSXA2Tgz2L2++enr219fApcBXXb4tyciItIOacDhwFM4u+V5faPT186/6oGHgX3RJGIREemAQuBinJ3tvL6p6atjX4uAC/lm+2MREZEdGgBci7Mnvtc3MH3Z+arAmaTZBxERke+YAjyJs0Wt1zcsfbnz1QDcA4xBRERS3hSc3ee8vjnpK3lfceAFYAIiIpJyJuLsNOf1zUhf3n69AuyGiPiOZvGKbZOAK3F2lQu8WE6ULt0zKChOp6AknYKiNPKL0ykqSSe/KI38onTS0yPk5EUhAlmxKOkZEaLRCNm5UQAa6+M0NSUAqKuJE48naGpMUF3RQk1VC9UVLVRXOl+Vm5vZvL6ZDWub2FDaSFNjwsv/fFviwOPAVcACj3sRkS0UAMSWwcB1wA+9bqS90jMi9OibRffe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'

details_content = [
    dbc.CardHeader("Details"),
    dbc.CardBody(
        [
            html.Img(src = analysis_graphic, className = 'details-logo'),
            dbc.Alert("Click on any plot to see its details.", color="primary", style = {'border-radius': '5px'})
        ], id = 'basic-details-cardbody'
    ),
]


details_div = html.Div([dbc.Card(details_content, color="dark", inverse=True, style = {'height': '100%'})],id = 'details-basic-webmap')
#-----------------------------------------------------------------------------

@app.callback(Output('basic-details-cardbody', 'children'),
             [Input('basic-map', 'clickData')])
def basic_map_click(data_clicked):
    if(data_clicked == None):
        return [html.Img(src = analysis_graphic, className = 'details-logo'),
                dbc.Alert("Click on any plot to see its details.", color="primary", style = {'border-radius': '5px'})]
    else:
        mini_df = plot_details_df[plot_details_df['UID'] == data_clicked['points'][0]['location']].dropna(axis='columns')



        if(len(mini_df) == 0):
            return [dbc.Alert("{}".format(data_clicked['points'][0]['location']), color="success", id = 'basic-details-header'),
                    dbc.Alert("No records found for the selected plot.".format(len(mini_df)), color="primary", style = {'border-radius': '5px'}),
                    ]
        else:

            details_table_body = []

            for c in range(len(mini_df.columns)):

                details_table_body.append(html.Tr([html.Td(mini_df.columns[c], className = 'basic-details-table-header'), html.Td(str(mini_df[mini_df['UID'] == data_clicked['points'][0]['location']][mini_df.columns[c]].values[0]),className = 'basic-details-table-content')]))


            return [dbc.Alert("{}".format(mini_df['Plot Number'].values[0]), color="success", id = 'basic-details-header'),
                    dbc.Table(details_table_body, bordered=True, id = 'basic-details-table')]






# ## Layout Controls


app.layout = page_layout

#Routing
@app.callback([Output('navlinkscallback', 'children'),Output('mainareacallback', 'children')],
              [Input('url', 'pathname')])
def display_page(pathname):

    global is_logged_in

    if(pathname == "/"):

        if(is_logged_in):

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'warning', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'primary',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')


                ], className = 'navlinkbuttongroup')

        else:

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'warning', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login"),



                ], className = 'navlinkbuttongroup')

        main_area = [
            dbc.Col(mapfig, width = 10, className = 'mainarea-map'),
            dbc.Col(details_div, width = 2, className = 'mainarea-details'),

            ]

        return navigation_links, main_area

    elif(pathname == "/dis"):

        plot_details_df = pd.read_csv(os.path.join(cur_path, 'support_files', 'plot_details.csv'))
        
        if(is_logged_in):
        
            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'warning', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'primary',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')
                    

                ], className = 'navlinkbuttongroup')
        
        else:

            navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'warning', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login")
                    
                    

                ], className = 'navlinkbuttongroup')
            
            
        #Layout Elements for DIS Page
        #===========================================================================================================
        dis_card_content_panel1 = [
            dbc.CardHeader("Query Filters"),
            dbc.CardBody(
                [
                    html.P('Area (Square KMs)', className = 'dis-control-labels'),
                    dcc.RangeSlider(
                            id = 'dis-area-range-slider',
                            min=0,
                            max=1000000,
                            value=[0, 1000000],
                            marks={
                                0: {'label': '0'},
                                200000: {'label': '0.2'},
                                400000: {'label': '0.4'},
                                600000: {'label': '0.6'},
                                800000: {'label': '0.8'},
                                1000000: {'label': '1'},
                            }
                        ),

                    

                    html.P('Nature of Project', className = 'dis-control-labels'),

                    dcc.Dropdown(
                        id = 'dis-nature-of-project-multiselect',
                        options=[
                            {'label': x, 'value': x} for x in plot_details_df['Nature of Project'].unique()
                        ],
                        multi=True
                    ),

                    html.P('Plot Status', className = 'dis-control-labels'),

                    dcc.Dropdown(
                        id = 'dis-plot-status-multiselect',
                        options=[
                            {'label': x, 'value': x} for x in plot_details_df['Plot Status '].unique()
                        ],
                        multi=True
                    ),

                    html.P('PCB Category', className = 'dis-control-labels'),

                    dcc.Dropdown(
                        id = 'dis-pcb-category-multiselect',
                        options=[
                            {'label': x, 'value': x} for x in plot_details_df['PCB Category'].unique()
                        ], style = {'color': 'black'},
                        multi=True
                    ),





                ], id = 'dis-panel-1-card-body'
            ),
            dbc.CardFooter([dbc.Button('Apply Filter', color = 'primary', id = 'dis-apply-filter'),])
        ]
        dis_panel_1 = dbc.Card(dis_card_content_panel1, color="dark", inverse=True, id = 'dis-panel-1-card')
        
        #Map Area---------------------------------------------------------------------------------------------
        
        plot_details_admin_df = pd.read_csv(plot_details_admin_file)
        
        fig = px.choropleth_mapbox(plot_details_df, geojson=dis_json, locations='UID', 
                           color_continuous_scale="Viridis",
                           zoom=10, center = {"lat": 29.561, "lon": 78.663},
                           opacity=0.8,
                           labels={'Plot Number':'Plot Number'},
                           hover_data = ['Plot Number', 'UID']
                          )


        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": 'traces',
                    "sourcetype": "raster",
                    "sourceattribution": "Google, RBS Pvt. Ltd.",
                    "source": [
                        "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
                    ]
                }
              ])

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update(layout_showlegend=False)

        dis_card_content_panel2 = [
            dbc.CardBody(
                [
                    dcc.Graph(figure = fig, id = 'dis-map')
                    
                ], id = 'dis-panel-2-card-body'
            ),
        ]
        dis_panel_2 = dbc.Card(dis_card_content_panel2, color="dark",  id = 'dis-panel-2-card', outline = True)
        
        #-------------------------------------------------------------------------------------------------------
        analysis_graphic = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7N11mFzl3f/x98zarEvc3YhCgkRIgjuFtrS4SwWnhaeGtNAf+rRQ2gdCcbfilKKB4AmahBDiQnbj674zvz9OUgIkWbnvM0fm87quvUhL5nu+JLtzPnOfW0BERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERES+K+J1AyI+FgP6Av2BrkAnoGTLP7d+dQYKt/z+dCB/y6+zgJwtv64BGrf8evOWfzYB1cAmYAOw8Ttf64FVwHKg3vJ/l4iIAoCkvAJgJDAaGAj02/LVH+jhXVvfUgoswwkDW//5JTAXqPCsKxEJNAUASRURYDgwDudmPxoYhXOjD7LlOEFgLvDZln9+BbR42JOIBIACgIRVLrArMBmYAuyFM1yfCqpxwsDbwDvALKDc045ExHcUACQscoFpwEFb/jkKSPO0I/9oBj7FCQOvAa/jzEsQkRSmACBBNhDYHzhiyz9j3rYTGM3AB8BzwKvAx0DC045ERER2Ih3nRn8bsAbnpqUv86/lW/5MD0CjJiIi4hNpOM/wbwbK8P5mGfavjcB9OKMq6W34+xEREbFqCvBPnBuS1zfFVP0qBf6GM5FSRETENSXA2Tgz2L2++enr219fApcBXXb4tyciItIOacDhwFM4u+V5faPT186/6oGHgX3RJGIREemAQuBinJ3tvL6p6atjX4uAC/lm+2MREZEdGgBci7Mnvtc3MH3Z+arAmaTZBxERke+YAjyJs0Wt1zcsfbnz1QDcA4xBRERS3hSc3ee8vjnpK3lfceAFYAIiIpJyJuLsNOf1zUhf3n69AuyGiPiOZvGKbZOAK3F2lQu8WE6ULt0zKChOp6AknYKiNPKL0ykqSSe/KI38onTS0yPk5EUhAlmxKOkZEaLRCNm5UQAa6+M0NSUAqKuJE48naGpMUF3RQk1VC9UVLVRXOl+Vm5vZvL6ZDWub2FDaSFNjwsv/fFviwOPAVcACj3sRkS0UAMSWwcB1wA+9bqS90jMi9OibRffe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'

        dis_card_content_panel3 = [
            dbc.CardHeader("Details"),
            dbc.CardBody(
                [
                    html.Img(src = analysis_graphic, className = 'details-logo'),
                    dbc.Alert("Click on any plot to see its details.", color="primary", style = {'border-radius': '5px'})
                    
                ] , id = 'dis-panel-3-card-body'
            ),
        ]
        dis_panel_3 = dbc.Card(dis_card_content_panel3, color="dark",  id = 'dis-panel-3-card')
        
        
        #===========================================================================================================

        main_area = [            
                dbc.Col(dis_panel_1, width = 2, className = 'dis-panel-1'),
                dbc.Col(dis_panel_2, width = 8, className = 'dis-panel-2'),
                dbc.Col(dis_panel_3, width = 2, className = 'dis-panel-3')
            ]
        
        return navigation_links, main_area

    elif(pathname == "/admin"):

        if(is_logged_in):

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'warning', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'primary',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')


                ], className = 'navlinkbuttongroup')

            # # Layout for Admin page---------------------------------------------------------------------------------------------------------------------------
            
            plot_details_df = pd.read_csv(os.path.join(cur_path, 'support_files', 'plot_details.csv'))
            
            admin_card_content_panel1 = [
                dbc.CardHeader("Select Industry/Park"),
                dbc.CardBody(
                    [
                        html.P('Park/Industrial Estate', id = 'admin-park-label'),
                        dcc.Dropdown(
                                id="admin-park-select",
                                options=[
                                    {"label": x, "value": x} for x in plot_details_df['Name of Industrial Estate'].unique()],
                                style = {'color': 'black'}
                            ),
                        html.P('UID', id = 'admin-uid-label'),
                        dcc.Dropdown(
                                id="uid-select",
                                
                            ),
                        dbc.Button('Open in Editor', color = 'primary', id = 'admin-open-editor-button'),

                        dbc.Button('Show Dataset', color = 'success', id = 'admin-show-dataset-button', href = '/dataset'),

                        dbc.Modal(
                            [
                                dbc.ModalHeader("Changes Saved"),
                                dbc.ModalBody("Changes made to the dataset has been successfully saved."),

                            ],
                            id="admin-alert-modal", centered = True
                        ),

                    ], className = 'admin-panel-1-card-body'
                ),
            ]
            admin_panel_1 = dbc.Card(admin_card_content_panel1, color="dark", inverse=True, className = 'admin-panel-1-card')

            admin_card_content_panel2 = [
                dbc.CardHeader("Record Editor"),
                dbc.CardBody(
                    [], className = 'admin-panel-2-card-body', id = 'admin-panel-2-card-body'
                ),
            ]
            admin_panel_2 = dbc.Card(admin_card_content_panel2, color="dark",  className = 'admin-panel-2-card', outline = True)

            admin_card_content_panel3 = [
                dbc.CardHeader("Existing Status"),
                dbc.CardBody(
                    [] , className = 'admin-panel-3-card-body', id = 'admin-panel-3-card-body'
                ),
            ]
            admin_panel_3 = dbc.Card(admin_card_content_panel3, color="dark",  className = 'admin-panel-3-card')

            #--------------------------------------------------------------------------------------------------------------------------------------------------------

            main_area = [
                    dbc.Col(admin_panel_1, width = 2, className = 'admin-panel-1'),
                    dbc.Col(admin_panel_2, width = 7, className = 'admin-panel-2'),
                    dbc.Col(admin_panel_3, width = 3, className = 'admin-panel-3')
                ]

        else:

            navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'warning', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login")



                ], className = 'navlinkbuttongroup')

            main_area = [

                    dbc.Alert(
                        [
                            html.H4("You are not Logged In!!!", className="alert-heading"),
                            html.P(
                                "In order to read/write the database, You need to be in Administrator mode. Please Login to continue. "
                            ),

                        ], color = 'danger', className = 'logout-info-div'
                    )
                ]

        return navigation_links, main_area

    elif(pathname == "/park"):

        if(is_logged_in):

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'warning', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'primary',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')


                ], className = 'navlinkbuttongroup')

        else:

            navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'warning', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login")



                ], className = 'navlinkbuttongroup')

        # Map in The Page

        park_pos_df = pd.read_csv(park_names_position_path)

        

        dist_df = pd.DataFrame()
        dist_df['id'] = [x['id'] for x in z['features']]

        parkfig = go.Figure(data = go.Choroplethmapbox(geojson=z, locations=dist_df.id, featureidkey = 'properties.dtname', z = dist_df.index,
                                        colorscale="Viridis", showscale=False, name="",
                                        marker_opacity=0, marker_line_width=2))


        for feature in z['features']:
            lats = []
            lons = []
            for cp in feature['geometry']['coordinates'][0]:
                lats.append(cp[1])
                lons.append(cp[0])
                
            parkfig.add_trace(go.Scattermapbox(
                                lat=lats,
                                lon=lons,
                                mode="lines",
                                hoverinfo='skip',
                                line=dict(width=2, color="#39FF14")
                            ))

        parkfig.add_trace(go.Scattermapbox(
                    lat = park_pos_df['lat'],
                    lon = park_pos_df['lon'],
                    text = park_pos_df['name'],
                    hoverinfo = 'text',
                    showlegend=False,
                    mode = 'markers',
                    marker={'size': 15, 'color': 'red'}
                ))

        parkfig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": 'traces',
                    "sourcetype": "raster",
                    "sourceattribution": "Google, RBS Pvt. Ltd.",
                    "source": [
                        "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
                    ]
                }
            ],
            mapbox = {'center': {'lat': 29.7, 'lon': 78.8}, 'zoom': 8})

        parkfig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        parkfig.update(layout_showlegend=False)

        park_basemap_overlay = html.Div([
                                            html.Span(id='park-basemap-overlay-circle'),
                                            html.P("Park", id = 'park-basemap-overlay-park'),
                                            html.P('Basemap', id = 'park-basemap-overlay-caption'),
                                            dbc.Select(id = 'park-basemap-overlay-dropdown', options = basemap_list_dict, value = "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"),
            
                                        ],id = 'park-basemap-overlay')


        parkmapfig = [park_basemap_overlay, dcc.Graph(figure = parkfig, style = {'height': '100%'}, id = 'park-display-map')]

        #Details Panel

        analysis_graphic = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7N11mFzl3f/x98zarEvc3YhCgkRIgjuFtrS4SwWnhaeGtNAf+rRQ2gdCcbfilKKB4AmahBDiQnbj674zvz9OUgIkWbnvM0fm87quvUhL5nu+JLtzPnOfW0BERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERES+K+J1AyI+FgP6Av2BrkAnoGTLP7d+dQYKt/z+dCB/y6+zgJwtv64BGrf8evOWfzYB1cAmYAOw8Ttf64FVwHKg3vJ/l4iIAoCkvAJgJDAaGAj02/LVH+jhXVvfUgoswwkDW//5JTAXqPCsKxEJNAUASRURYDgwDudmPxoYhXOjD7LlOEFgLvDZln9+BbR42JOIBIACgIRVLrArMBmYAuyFM1yfCqpxwsDbwDvALKDc045ExHcUACQscoFpwEFb/jkKSPO0I/9oBj7FCQOvAa/jzEsQkRSmACBBNhDYHzhiyz9j3rYTGM3AB8BzwKvAx0DC045ERER2Ih3nRn8bsAbnpqUv86/lW/5MD0CjJiIi4hNpOM/wbwbK8P5mGfavjcB9OKMq6W34+xEREbFqCvBPnBuS1zfFVP0qBf6GM5FSRETENSXA2Tgz2L2++enr219fApcBXXb4tyciItIOacDhwFM4u+V5faPT186/6oGHgX3RJGIREemAQuBinJ3tvL6p6atjX4uAC/lm+2MREZEdGgBci7Mnvtc3MH3Z+arAmaTZBxERke+YAjyJs0Wt1zcsfbnz1QDcA4xBRERS3hSc3ee8vjnpK3lfceAFYAIiIpJyJuLsNOf1zUhf3n69AuyGiPiOZvGKbZOAK3F2lQu8WE6ULt0zKChOp6AknYKiNPKL0ykqSSe/KI38onTS0yPk5EUhAlmxKOkZEaLRCNm5UQAa6+M0NSUAqKuJE48naGpMUF3RQk1VC9UVLVRXOl+Vm5vZvL6ZDWub2FDaSFNjwsv/fFviwOPAVcACj3sRkS0UAMSWwcB1wA+9bqS90jMi9OibRffe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'

        details_content = [
            dbc.CardHeader("Details"),
            dbc.CardBody(
                [
                    html.Img(src = analysis_graphic, className = 'details-logo'),
                    dbc.Alert("Click on any plot to see its details.", color="primary", style = {'border-radius': '5px'})
                ], id = 'park-details-cardbody'
            ),
        ]


        park_details_div = html.Div([dbc.Card(details_content, color="dark", inverse=True, style = {'height': '100%'})],id = 'park-basic-webmap')

        


        main_area = [
                dbc.Col(parkmapfig, width = 10, className = 'park-map'),
                dbc.Col(park_details_div, width = 2, className = 'park-details')
            ]

        return navigation_links, main_area

    elif(pathname == "/login"):


        navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'warning', className = 'navlinkbutton-end', href = "/login")

            ], className = 'navlinkbuttongroup')

        email_input = dbc.FormGroup(
            [
                dbc.Label("Username", html_for="example-email"),
                dbc.Input(type="text", id="example-email", placeholder="Enter Username"),

            ]
        )

        password_input = dbc.FormGroup(
            [
                dbc.Label("Password", html_for="example-password"),
                dbc.Input(
                    type="password",
                    id="example-password",
                    placeholder="Enter Password",
                ),

            ]
        )

        submit_button = dbc.Button("Login", color="primary", style = {'width': '100px'}, id = 'login-button')

        card_content = [
            dbc.CardHeader("Login"),
            dbc.CardBody(
                [
                    dbc.Form([email_input, password_input, html.Div(submit_button, className = 'submitbutton')]),

                    dbc.Modal(id="login-message", is_open = False, centered=True),
                    dbc.Button('Forgot Password', color = 'link', className = 'forgot-pass-button', href = '/forgot-password')

                ]
            ),
        ]

        form = dbc.Card(card_content,color="dark", inverse=True, style = {'border-radius': '10px'})

        return navigation_links, html.Div(form, className = 'loginform')

    elif(pathname == "/logout"):



        is_logged_in = False

        navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login"),



                ], className = 'navlinkbuttongroup')

        main_area = [

                    dbc.Alert(
                        [
                            html.H4("Logged Out Successfully!!!", className="alert-heading"),
                            html.P(
                                "You have been logged out successfully. If you wish to login again, click on Login on the top navigation. Alternatively, you can access the application in Guest mode. "
                            ),

                        ], className = 'logout-info-div'
                    )

            ]

        return navigation_links, main_area

    elif(pathname == "/dataset"):


        if(is_logged_in):

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'primary',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')


                ], className = 'navlinkbuttongroup')

            plot_details_admin_df = pd.read_csv(plot_details_admin_file)

            main_area = [

                        html.Div(dbc.Spinner([

                            dbc.Toast(
                                    "Changes to the database has been recorded.",
                                    id="modal",
                                    header="Changes Saved",
                                    is_open=False,
                                    dismissable=True,
                                    icon="primary",
                                    duration=4000,
                                    className = 'database-modal',
                                    style = {
                                        'position': 'fixed',
                                        'top': '85px',
                                        'right': '10px'}
                                ),

                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i} for i in plot_details_admin_df.columns],
                                data=plot_details_admin_df.to_dict('records'),
                                page_size = 50,
                                style_cell={
                                    'whiteSpace': 'normal',
                                    'height': 'auto', 'minWidth': '180px', 'width': '200px', 'maxWidth': '240px', 'textAlign': 'left'
                                },
                                style_table={'height': '500px', 'overflowY': 'auto', 'margin': '20px', 'width': 'auto',
                                             },

                                style_data = {'font-size': 'small', 'font-family': 'Roboto'},
                                style_header = {'font-size': 'small', 'font-family': 'Roboto'},
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    }
                                ],

                                editable=True,
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                selected_columns=[],
                                selected_rows=[],
                                page_action="native",
                                page_current= 0,
                                export_format='xlsx',
                                export_headers='display',
                                tooltip_data=[
                                    {
                                        column: {'value': str(value), 'type': 'markdown'}
                                        for column, value in row.items()
                                    } for row in plot_details_admin_df.to_dict('records')
                                ],

                            ),

                    dbc.Button('Save', color = 'primary', id = 'savebutton', className = 'dataset-save'),



                    ], type = 'grow', color = 'primary'), className = 'dataset-table-container',),






                ]
        else:

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login"),



                ], className = 'navlinkbuttongroup')

            main_area = [

                    dbc.Alert(
                        [
                            html.H4("You are not Logged In!!!", className="alert-heading"),
                            html.P(
                                "In order to read/write the database, You need to be in Administrator mode. Please Login to continue. "
                            ),

                        ], color = 'danger', className = 'logout-info-div'
                    )
                ]

        return navigation_links, main_area


    elif(pathname == "/userinfo"):

        if(is_logged_in):

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'warning',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')


                ], className = 'navlinkbuttongroup')

            main_area = [

                            html.Div([

                                    dbc.Row([
                                            dbc.Col(html.H2([html.I(className="fas fa-user-tie 4x", id = 'userinfo-logo'),'User Details'], className = 'userinfo-h2'), width = 7),
                                            dbc.Col([dbc.Button('Change Password', color = 'primary', id = 'userinfo-change-pwd-button')], width = 5)
                                        ]),

                                    dbc.Row([dbc.Col(html.H3("{} {}".format(user_info_dict['First Name'], user_info_dict['Last Name'])))],
                                            className = 'userinfo-rows'),


                                ], className = 'userinfo-main-container')


                    ]

        else:

            navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login")



                ], className = 'navlinkbuttongroup')

            main_area = [

                        dbc.Alert(
                            [
                                html.H4("You are not Logged In!!!", className="alert-heading"),
                                html.P(
                                    "In order to read/write the database, You need to be in Administrator mode. Please Login to continue. "
                                ),

                            ], color = 'danger', className = 'logout-info-div'
                        )
                    ]

        return navigation_links, main_area

    elif(pathname == '/forgot-password'):

        if(is_logged_in):

            navigation_links = dbc.ButtonGroup([

                    dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                    dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                    dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                    dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                    dbc.Button(html.P(session_user_name, className = "col-12 text-truncate"), color = 'warning',
                               className = 'navlinkbutton', href = "/userinfo", id='username'),
                    dbc.Button([html.I(className = 'fas fa-sign-out-alt', style = {'margin-right': '5px'}), 'Logout'], color = 'danger',
                               className = 'navlinkbutton-logout', href = "/logout"),
                    dbc.Tooltip(session_user_name + " User Details", target = 'username', placement = 'bottom')


                ], className = 'navlinkbuttongroup')



        else:

            navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login")



                ], className = 'navlinkbuttongroup')

        main_area = [

                        html.Div([

                                dbc.Card([
                                    dbc.CardHeader('Forgot Password'),
                                    dbc.CardBody(['E-mail Address',
                                                    dbc.Input(type = 'email', id = 'email-input-forgot-pass'),
                                                    dbc.Button('Submit', id = 'send-verf-code-button', color = 'primary'),
                                                    html.Div(id='forgot-pass-alert')
                                                 ]),

                                ], className = 'forgot-pass-form', color = 'dark', inverse = True)


                            ], className = 'forgot-pass-container')
                    ]

        return navigation_links, main_area

    else:

        navigation_links = dbc.ButtonGroup([

                dbc.Button('Basic Web Map', color = 'secondary', className = 'navlinkbutton-start', href = '/'),
                dbc.Button('DIS Query', color = 'secondary', className = 'navlinkbutton', href = '/dis'),
                dbc.Button('Administrator', color = 'secondary', className = 'navlinkbutton', href = '/admin'),
                dbc.Button('Park Details', color = 'secondary', className = 'navlinkbutton', href = "/park"),
                dbc.Button('Login', color = 'success', className = 'navlinkbutton-end', href = "/login")

            ], className = 'navlinkbuttongroup')

        main_area = [

                dbc.Col([

                    html.H2('404: Looks like you are lost.', className = 'text404'),
                    html.P('The page you are looking for is not available.', className = 'desc404'),
                    html.Div(html.Img(src = "https://cdn.dribbble.com/users/285475/screenshots/2083086/dribbble_1.gif", className = 'image404'), className = 'box404'),


                ], width = 12),
            ]

        return navigation_links, main_area




# ## Callback for Dataset Page

@app.callback(
    [Output("modal", "is_open"),
     Output('table', 'columns'),
     Output('table', 'data'),
     Output('table', 'tooltip_data')],
    [Input("savebutton", "n_clicks")
     ],
    [State('table', 'data'), State('table', 'columns'), State("modal", "is_open")],
)
def toggle_modal(n1, rows, columns, is_open):

    plot_details_admin_df = pd.read_csv(plot_details_admin_file)
    for c in plot_details_admin_df.columns:
            if(c[:7] == 'Unnamed'):
                plot_details_admin_df = plot_details_admin_df.drop([c],axis = 1)

    if n1:

        export_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])


        export_df.to_csv(plot_details_admin_file)

        plot_details_admin_df = pd.read_csv(plot_details_admin_file)

        for c in plot_details_admin_df.columns:

            if(c[:7] == 'Unnamed'):
                plot_details_admin_df = plot_details_admin_df.drop([c],axis = 1)

        plot_details_admin_df.to_csv(plot_details_admin_file)

        tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in plot_details_admin_df.to_dict('records')
            ],



        return True, [{"name": i, "id": i} for i in plot_details_admin_df.columns], plot_details_admin_df.to_dict('records'), tooltip_data

    tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in plot_details_admin_df.to_dict('records')
            ],


    return False, [{"name": i, "id": i} for i in plot_details_admin_df.columns], plot_details_admin_df.to_dict('records'), tooltip_data

# ## Callbacks for DIS Page



#Callback to filter data
@app.callback(Output('dis-panel-2-card-body', 'children'),
             [Input('dis-apply-filter', 'n_clicks')],
             [State('dis-area-range-slider', 'value'),
              State('dis-nature-of-project-multiselect', 'value'),
              State('dis-plot-status-multiselect', 'value'),
              State('dis-pcb-category-multiselect', 'value')])
def filter_data_for_dis_map(n, arearange, project_nature, plot_status, pcb_cat):
    if(n):
        
        plot_details_df = pd.read_csv(plot_details_admin_file)

        plot_details_df_original = plot_details_df
        
        #Apply Area Range Filter
        plot_details_df['Geometric Area'] = [float(x) for x in plot_details_df['Geometric Area']]
        plot_details_df = plot_details_df[(plot_details_df['Geometric Area'] >= float(arearange[0])) & (plot_details_df['Geometric Area'] <= float(arearange[1]))]
        
        #Apply Nature of Project Filter
        if(project_nature is not None):
            plot_details_df = plot_details_df[plot_details_df['Nature of Project'].isin(project_nature)]
            
        #Apply Plot Status Filter
        if(plot_status is not None):
            plot_details_df = plot_details_df[plot_details_df['Plot Status '].isin(plot_status)]

        #Apply PCB Category Filter
        if(pcb_cat is not None):
            plot_details_df = plot_details_df[plot_details_df['PCB Category'].isin(pcb_cat)]
        
        plot_details_df['selected'] = [1] * len(plot_details_df)

        fig = px.choropleth_mapbox(plot_details_df_original, geojson=dis_json, locations='UID', 
                           color_continuous_scale="Viridis",
                           zoom=10, center = {"lat": 29.561, "lon": 78.663},
                           opacity=0.6,
                           labels={'Plot Number':'Plot Number'},
                           hover_data = ['Plot Number', 'UID', 'Geometric Area', 'Nature of Project', 'Plot Status ']
                          )

        fig.add_trace(go.Choroplethmapbox(geojson=dis_json, locations= plot_details_df['UID'], z = plot_details_df['selected'],colorscale="agsunset", 
                                    marker_opacity=0.8, marker_line_width=2, showscale = False, name = 'Filtered'))


        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": 'traces',
                    "sourcetype": "raster",
                    "sourceattribution": "Google, RBS Pvt. Ltd.",
                    "source": [
                        "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
                    ]
                }
              ])

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update(layout_showlegend=False)
        
        
        return dcc.Graph(figure = fig, id = 'dis-map')
    
    else:
        
        plot_details_df = pd.read_csv(plot_details_admin_file)
        
        fig = px.choropleth_mapbox(plot_details_df, geojson=dis_json, locations='UID', 
                           color_continuous_scale="Viridis",
                           zoom=10, center = {"lat": 29.561, "lon": 78.663},
                           opacity=0.8,
                           labels={'Plot Number':'Plot Number'},
                           #hover_data = ['Plot Number', 'UID', 'Geometric Area', 'Nature of Project', 'Plot Status ']
                          )


        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_layers=[
                {
                    "below": 'traces',
                    "sourcetype": "raster",
                    "sourceattribution": "Google, RBS Pvt. Ltd.",
                    "source": [
                        "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
                    ]
                }
              ])

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update(layout_showlegend=False)
        
        
        return dcc.Graph(figure = fig, id = 'dis-map')
        
        


#To show data in the details panel
@app.callback(Output('dis-panel-3-card-body', 'children'),
             [Input('dis-map', 'clickData')])
def dis_map_click(data_clicked):
    
    plot_details_df = pd.read_csv(plot_details_admin_file)
    
    if(data_clicked == None):
        return [html.Img(src = analysis_graphic, className = 'details-logo'), 
                dbc.Alert("Click on any plot to see its details.", color="primary", style = {'border-radius': '5px'})]
    else: 
        mini_df = plot_details_df[plot_details_df['UID'] == data_clicked['points'][0]['location']].dropna(axis='columns')
        
               
        
        if(len(mini_df) == 0):
            return [dbc.Alert("{}".format(data_clicked['points'][0]['location']), color="success", id = 'basic-details-header'),
                    dbc.Alert("No records found for the selected plot.".format(len(mini_df)), color="primary", style = {'border-radius': '5px'}),
                    ]
        else:
            
            details_table_body = []
        
            for c in range(len(mini_df.columns)):

                details_table_body.append(html.Tr([html.Td(mini_df.columns[c], className = 'basic-details-table-header'), html.Td(str(mini_df[mini_df['UID'] == data_clicked['points'][0]['location']][mini_df.columns[c]].values[0]),className = 'basic-details-table-content')]))
        
            
            return [dbc.Alert("{}".format(mini_df['Plot Number'].values[0]), color="success", id = 'basic-details-header'),
                    dbc.Table(details_table_body, bordered=True, id = 'dis-details-table')]


# ## Login Controls - User Authentication


@app.callback(Output('login-message', 'children'), Output('login-message', 'is_open'),
              [Input("login-button", "n_clicks")],
              [State('example-email', 'value'), State('example-password', 'value'), State('login-message', 'is_open')])
def autheticate_user(n, user, pwd, is_open):

    global is_logged_in
    global session_user_name
    global user_info_dict

    user_df = pd.read_csv(user_info_csv_path)

    if(n):

        mini_df = user_df[user_df['Username'] == user]

        if(len(mini_df) == 0):

            modal_content = [dbc.ModalHeader("Login Unsuccessful."),
                             dbc.ModalBody("No such user exists. Please check your inputs and try again.")]

            return modal_content, True
        else:
            if(mini_df['Password'].values[0] == pwd):

                modal_content = [dbc.ModalHeader("Login Successful."),
                             dbc.ModalBody("Welcome, {}".format(mini_df['First Name'].values[0])),
                             dbc.ModalFooter(dbc.Button("Okay", href="/", className="ml-auto"))]

                is_logged_in = True

                session_user_name = "{} {}".format(mini_df['First Name'].values[0], mini_df['Last Name'].values[0])

                user_info_dict = {'First Name': mini_df['First Name'].values[0],
                                  'Middle Name': mini_df['Middle Name'].values[0],
                                  'Last Name': mini_df['Last Name'].values[0],
                                  'DOB': mini_df['DOB'].values[0],
                                  'Username': mini_df['Username'].values[0],
                                  'Password': mini_df['Password'].values[0]}



                return modal_content, True

            else:
                modal_content = [dbc.ModalHeader("Login Unsuccessful."),
                             dbc.ModalBody("Invalid Password. Please check your inputs and try again.")]

                return modal_content, True


# ## Forgot Password Page Callbacks

@app.callback(Output('forgot-pass-alert', 'children'),
             [Input('send-verf-code-button', 'n_clicks')],
             [State('email-input-forgot-pass','value')])
def forgot_password(n, email):
    user_df = pd.read_csv(user_info_csv_path)

    if(n):
        mini_df = user_df[user_df['E-mail'] == email]

        if(len(mini_df) == 0):
            return dbc.Alert('The E-mail is not associated with any username. Try Again', color = 'danger', className = 'forgot-pass-alert-child')
        else:

            message = """            Subject: Forgot Password for UIIS

            Dear {},

            Password for the user {} is {}.

            RBS Pvt Ltd.""".format(mini_df['First Name'].values[0],mini_df['Username'].values[0],mini_df['Password'].values[0])


            # Create a secure SSL context
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, email, message)

            return dbc.Alert('The password has been sent to {}.'.format(email), color = 'success', className = 'forgot-pass-alert-child')


# ## Callback for Admin Page


selected_admin_uid = ''

@app.callback(Output('uid-select','options'), Input('admin-park-select', 'value'))
def generate_uid_select_values(park):
    plot_details_df = pd.read_csv(os.path.join(cur_path, 'support_files', 'plot_details.csv'))
    return [{"label": x, "value": x} for x in plot_details_df[plot_details_df['Name of Industrial Estate'] == park]['UID']]

@app.callback(Output('admin-panel-2-card-body', 'children'), Output('admin-panel-3-card-body', 'children'),
              Input('admin-open-editor-button', 'n_clicks'),
              State('uid-select', 'value'))
def load_admin_editor(n, uid):

    global selected_admin_uid

    selected_admin_uid = uid

    if(n):

        plot_details_admin_df = pd.read_csv(plot_details_admin_file)
        for c in plot_details_admin_df.columns:
            if(c[:7] == 'Unnamed'):
                plot_details_admin_df = plot_details_admin_df.drop([c],axis = 1)

        mini_admin_df = plot_details_admin_df[plot_details_admin_df['UID'] == uid]

        if(len(mini_admin_df) == 0):
            return1 = dcc.Loading([html.H1(uid),
                                dbc.Alert([dbc.Row([
                                                    dbc.Col(html.I(className = "fas fa-exclamation-circle 2x"),width = 1),
                                                    dbc.Col(html.P('No record found for the selected UID'), width = 11)
                                                ]),


                                          ], color = 'danger', className='record-unavailable-alert')
                               ])

            return2 = dcc.Loading([html.H3(uid),
                                dbc.Alert([dbc.Row([

                                                    dbc.Col(html.P('No record found for the selected UID'), width = 12)
                                                ]),


                                          ], color = 'danger', className='record-unavailable-alert')
                               ])

            return return1, return2
        else:

            df_for_table = pd.DataFrame()
            df_for_table['Properties'] = mini_admin_df.columns
            df_for_table['Values'] = mini_admin_df.values[0]

            admin_data_table_editor = dash_table.DataTable(
                    id='admin-data-table-editor',
                    columns=[{"name": i, "id": i} for i in df_for_table.columns],
                    data=df_for_table.to_dict('records'),
                    style_cell={'textAlign': 'left',
                                'whiteSpace': 'normal',
                                'minWidth': '50%', 'width': '50%', 'maxWidth': '50%',
                                'height': 'auto',},
                    style_data = {'font-size': 'small', 'font-family': 'Roboto'},
                    style_header = {'font-size': 'small', 'font-family': 'Roboto', 'font-weight': 'bold'},
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],

                    editable=True,

                    tooltip_data=[
                        {
                            column: {'value': str(value), 'type': 'markdown'}
                            for column, value in row.items()
                        } for row in df_for_table.to_dict('records')
                    ],


                )

            return1 = dcc.Loading([dbc.Row([dbc.Col(html.H1(uid), width = 10, id = 'admin-uid-h1'),
                                         dbc.Col(dbc.Button('Save Changes', color = 'primary', id = 'admin-save-changes-button'), width = 2)]),
                                html.Div(admin_data_table_editor, className = 'admin-table-container')
                               ])

            return2 = dcc.Loading([html.H3(uid),
                                html.Div(dbc.Table.from_dataframe(df_for_table, striped=True, bordered=True, hover=True), className = 'admin-existing-details-container')
                               ])

            return return1, return2

@app.callback(Output('admin-alert-modal', 'is_open'),
             [Input('admin-save-changes-button', 'n_clicks')],
             [State('admin-data-table-editor', 'data'),
              State('admin-data-table-editor', 'columns'),
              State("admin-alert-modal", "is_open")])
def admin_save_changes(n, rows, columns, is_open):

    global selected_admin_uid

    if(n):
        export_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])

        plot_details_admin_df = pd.read_csv(plot_details_admin_file)
        for c in plot_details_admin_df.columns:
            if(c[:7] == 'Unnamed'):
                plot_details_admin_df = plot_details_admin_df.drop([c],axis = 1)

        for c in plot_details_admin_df.columns:
            plot_details_admin_df.loc[plot_details_admin_df['UID'] == selected_admin_uid, c] = export_df[export_df['Properties'] == c]['Values'].values[0]


        plot_details_admin_df.to_csv(plot_details_admin_file)

        return True


#Callbacks for Park Page
@app.callback(Output('park-display-map', 'figure'), [Input('park-basemap-overlay-dropdown', 'value')])
def change_park_map_acoording_to_basemap(basemap):
    park_pos_df = pd.read_csv(park_names_position_path)

    dist_df = pd.DataFrame()
    dist_df['id'] = [x['id'] for x in z['features']]

    parkfig = go.Figure(data = go.Choroplethmapbox(geojson=z, locations=dist_df.id, featureidkey = 'properties.dtname', z = dist_df.index,
                                    colorscale="Viridis", showscale=False, name="",
                                    marker_opacity=0, marker_line_width=2))


    for feature in z['features']:
        lats = []
        lons = []
        for cp in feature['geometry']['coordinates'][0]:
            lats.append(cp[1])
            lons.append(cp[0])
            
        parkfig.add_trace(go.Scattermapbox(
                            lat=lats,
                            lon=lons,
                            mode="lines",
                            hoverinfo='skip',
                            line=dict(width=2, color="#39FF14")
                        ))

    parkfig.add_trace(go.Scattermapbox(
                lat = park_pos_df['lat'],
                lon = park_pos_df['lon'],
                text = park_pos_df['name'],
                hoverinfo = 'text',
                showlegend=False,
                mode = 'markers',
                marker={'size': 15, 'color': 'red'}
            ))

    parkfig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "Google, RBS Pvt. Ltd.",
                "source": [
                   basemap
                ]
            }
        ],
        mapbox = {'center': {'lat': 29.7, 'lon': 78.8}, 'zoom': 8})

    parkfig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    parkfig.update(layout_showlegend=False)

    return parkfig

@app.callback(Output('park-details-cardbody', 'children'), [Input('park-display-map', 'clickData')])
def get_park_data_to_details_panel(data_clicked):

    if(data_clicked == None):
        return [html.Img(src = analysis_graphic, className = 'details-logo'),
                dbc.Alert("Click on any park to see its details.", color="primary", style = {'border-radius': '5px'})]
    else:

        

        park_details_df = pd.read_csv(park_details_csv_path)

        mini_df = park_details_df[park_details_df['Industrial Estate Name'] == data_clicked['points'][0]['text']].dropna(axis='columns')


        if(len(mini_df) == 0):
            return [dbc.Alert("{}".format(data_clicked['points'][0]['text']), color="success", id = 'details-caption-alert'),
                    dbc.Alert("No records found for the selected park.", color="primary", style = {'border-radius': '5px'}),
                    ]
        else:

            rand_identifier = random.randint(122456,998345)

            mini_df.to_csv(os.path.join(download_files_container_folder, 'CSV_{}.csv'.format(rand_identifier)), index = None)

            details_table_body = []

            for c in range(len(mini_df.columns)):

                details_table_body.append(html.Tr([html.Td(mini_df.columns[c], className = 'basic-details-table-header'), html.Td(str(mini_df[mini_df['Industrial Estate Name'] == data_clicked['points'][0]['text']][mini_df.columns[c]].values[0]),className = 'basic-details-table-content')]))


            return [dbc.Alert("{}".format(mini_df['Industrial Estate Name'].values[0]), color="success", id = 'details-caption-alert'),
                    dbc.Button([html.I(className = 'fas fa-file-csv', style = {'margin-right': '5px'}), 'Download CSV'], outline=True, color="Success", id = 'park-details-download-csv', href = '/download_content/CSV_{}.csv'.format(rand_identifier)),
                    dbc.Button([html.I(className = 'fas fa-file-pdf', style = {'margin-right': '5px'}), 'Download PDF'], outline=True, color="Danger", id = 'park-details-download-pdf'),
                    dbc.Table(details_table_body, bordered=True, id = 'basic-details-table')]


@app.server.route('/download_content/<path:path>')
def serve_static(path):
    root_dir = os.getcwd()
    return flask.send_from_directory(
        os.path.join(root_dir, 'download_content'), path
    )


if __name__ == "__main__":
    app.run_server()

