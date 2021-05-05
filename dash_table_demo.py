#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import dash_table
import pandas as pd
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc

df = pd.read_csv(r'E:\Manaruchi\DIS\DIS\support_files\test.csv')

for c in df.columns:

    if(c[:7] == 'Unnamed'):
        df = df.drop([c],axis = 1)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO,
                                                "https://fonts.googleapis.com/css2?family=Lora&display=swap"])

app.layout = html.Div([
        
        dbc.Alert('Dash Data Table Demo for DIS',id = 'alertbox', color = 'success'),
    
        dcc.Loading(dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_size = 50,
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto', 'minWidth': '180px', 'width': '200px', 'maxWidth': '240px', 'textAlign': 'left'
            },
            style_table={'height': '500px', 'overflowY': 'auto', 'margin': '20px', 'width': 'auto',},
            
            style_data = {'font-family': 'Lora', 'font-size': 'small'},
            style_header = {'font-family': 'Lora', 'font-size': 'small'},
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
                } for row in df.to_dict('records')
            ],

        )),
    
    dbc.Button('Save', color = 'primary', id = 'savebutton'),
    
    dbc.Toast(
            "Changes to the database has been recorded.",
            id="modal",
            header="Changes Saved",
            is_open=False,
            dismissable=True,
            icon="primary", duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, 
                   'background-color': 'black', 'color': 'white',
                   'border-radius': '10px'},
        ),
    
    

    ])


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
    
    global df
    
    if n1:    
        
        export_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        
        #print(df.compare(export_df))
        
        export_df.to_csv(r'E:\Manaruchi\DIS\DIS\support_files\test.csv')
        
        df = pd.read_csv(r'E:\Manaruchi\DIS\DIS\support_files\test.csv')
        
        for c in df.columns:
            
            if(c[:7] == 'Unnamed'):
                df = df.drop([c],axis = 1)
          
        df.to_csv(r'E:\Manaruchi\DIS\DIS\support_files\test.csv')
        
        tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],

        
        
        return True, [{"name": i, "id": i} for i in df.columns], df.to_dict('records'), tooltip_data
    
    tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],

        
    return False, [{"name": i, "id": i} for i in df.columns], df.to_dict('records'), tooltip_data


if __name__ == '__main__':
    app.run_server()


# In[ ]:


df


# In[ ]:




