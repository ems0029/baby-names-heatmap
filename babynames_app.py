import pandas as pd
import numpy as np
import plotly.express as px
import glob
from dash import Dash, html, dcc, callback, Output, Input

combined_df = pd.read_pickle('babyNamesData.pkl')
    
app = Dash(__name__)

app.layout = html.Div([
        dcc.Graph(id='graph-content'),
        html.Div([
            html.Label("Name"),
            dcc.Input(value='John', type='text',id='name_str'),
            html.Br(),
            html.Label("Baby Sex"),
            dcc.RadioItems(["All","M","F"], "All", id='radioButton_sex',inline=True),
            html.Br()
            ], style={'width': '18%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Start Year"),
            dcc.Slider(value=2020,min=1970,max=2022,step=1,id='start_year'),
            html.Br(),

            html.Label("End Year"),
            dcc.Slider(value=2020,min=1970,max=2022,step=1,id='end_year')
            ], style={'width': '80%', 'display': 'inline-block'}),
        ])


@callback(
    Output('graph-content', 'figure'),
    Input('name_str','value'),
    Input('start_year','value'),
    Input('end_year','value'),
    Input('radioButton_sex','value')
)

def update_graph(name_in,start_in,end_in,sex_in):
    # get last 3 years, and a specific name
    name = name_in
    year_start = start_in
    year_end = end_in
    sex_fm = sex_in
    if sex_fm =="All":
        df_all = combined_df
        col = 'mint'
        baby_str = "Babies"
    elif sex_fm == "F":
        df_all = combined_df.loc[(combined_df['Sex']==sex_fm)] 
        col = 'purpor'
        baby_str = "Female Babies"
    elif sex_fm == "M":
        df_all = combined_df.loc[(combined_df['Sex']==sex_fm)] 
        col = 'blues'
        baby_str = "Male Babies"

    if year_start<year_end:
        title_str=f'Percent of {baby_str} Named {name} by State from {year_start} to {year_end}, x1000'
    elif year_start>=year_end:
        year_end=year_start
        title_str=f'Percent of {baby_str} Named {name} by State in {year_start}, x1000'
        
    df_all = df_all.loc[(df_all['Year']>=year_start)&(df_all['Year']<=year_end)]
    df_sub = df_all.loc[(df_all['Name'].str.lower()==name.lower())] 

    df_sub=df_sub.drop(['Year'],axis=1).groupby(by='State').sum(numeric_only=True)
    df_all=df_all.drop(['Year'],axis=1).groupby(by='State').sum(numeric_only=True)
    df_all.rename(columns={"Number":"Total Number"},inplace=True)
    df_sub=pd.concat([df_sub,df_all],axis=1)
    df_sub['Percent x1000'] = df_sub["Number"]/df_sub["Total Number"]*1000
    fig = px.choropleth(df_sub,
                    locations=df_sub.index,
                    locationmode="USA-states",
                    scope="usa",
                    color='Percent x1000',
                    color_continuous_scale=col
                   )
    # center the title
    fig.update_layout(title_text=title_str, title_x=0.5) 
    return fig

if __name__ == '__main__':
    app.run(debug=True)