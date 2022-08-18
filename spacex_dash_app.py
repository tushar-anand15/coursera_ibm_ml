# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_site_options = list(spacex_df['Launch Site'].unique())
launch_site_options.append('All')

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options = launch_site_options, value='All',clearable=False,searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=min_payload, max=max_payload,tooltip={"placement": "bottom", "always_visible": True},value=[min_payload,max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id ='success-pie-chart',component_property='figure'),
     Input(component_id = 'site-dropdown',component_property = 'value')
)
def display_pie_chart(value):
    if value=='All':
        filt_df = spacex_df.groupby('Launch Site',as_index=False)['class'].value_counts()
        filt_df = filt_df.loc[filt_df['class']==1]
        fig = go.Figure(go.Pie(
        name = "",
        values = filt_df['count'],
        labels = filt_df['Launch Site'],
        #text = class_values['hovertext'],
        hovertemplate = "%{label} <br>Percentage: %{percent}"
    ))
        fig.update_layout(
            title = dict(text = f"Successful launches for all stations",x=0.5),
            legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.30
    ))

    else:
        filt_df = spacex_df.loc[spacex_df['Launch Site']==value]
        class_values = filt_df['class'].value_counts().to_frame()
        class_values.reset_index(inplace=True)
        class_values['hovertext'] = value
        class_values['labels'] = class_values['index'].replace(to_replace=[0,1],value=['Failure','Success'])
        #labels = ['Failure','Success']
        fig = go.Figure(go.Pie(
        name = "",
        values = class_values['class'],
        labels = class_values['labels'],
        text = class_values['hovertext'],
        hovertemplate = "%{label} <br>Percentage: %{percent} </br> %{text}"
    ))
        fig.update_layout(
            title = dict(text = f"Successful vs Failed launch counts",x=0.5),
            legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.30
    )
            )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id ='success-payload-scatter-chart',component_property='figure'),
     Input(component_id = 'payload-slider',component_property = 'value')
)
def display_scatterplot(value):
    filt_df = spacex_df[spacex_df['Payload Mass (kg)'].between(value[0],value[1])]
    filt_df['labels'] = filt_df['class'].replace(to_replace=[0,1],value=['Failure','Success'])
    # fig = go.Figure(data=go.Scatter(y=filt_df['class'],
    #                             x=filt_df['Payload Mass (kg)'],
    #                             mode='markers',
    #                             marker_color = filt_df['Booster Version Category']
    #                             )) # hover text goes here

    fig = px.scatter(filt_df,x='Payload Mass (kg)', y='class',color='Booster Version Category')

    fig.update_layout(
        title = dict(text = f"Launch results based on payload mass",x=0.5),
        legend=dict(title='Booster Version',
    yanchor="bottom",
    y=0.99,
    xanchor="left",
    x=0.99
)
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
