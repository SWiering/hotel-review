import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go

from bson.code import Code
from pymongo import MongoClient

app = dash.Dash(__name__)

ACCESS_TOKEN = 'pk.eyJ1Ijoic2ltb25odmEiLCJhIjoiY2s1OXk2c3BhMTFyaDNwbGprYWowZmZhOSJ9.Alw4kvUDHu7cxG9hB_Ra9Q'
client = MongoClient("localhost:27017")
db = client.hotels

app.layout = html.Div(children=[
    html.H1(children='Hotels in europe'),
    html.Div(id='the_title'),
    dcc.Graph(
        id='topo'
    ),
    dcc.RangeSlider(
        id='my-range-slider',
        min=0,
        max=10,
        step=0.1,
        value=[0, 10]
    ),
    html.Div(id='output-container-range-slider')
])


def custom_mr(c_min, c_max):
    set_map = Code("""
        function(){
            var key = {name: this.name, lng: this.lng, lat: this.lat, score: this.score}
            var value = {
                the_id: this.name,
                count: 1,
                positive: this.positive
            }

            emit(key, value)
        }
        """)

    set_reduce = Code("""
        function(key, values){
            reducedObj = {
                the_id: key,
                count: 0,
                positive: 0,
            }

            values.forEach( function(value) {
                reducedObj.count += value.count;
                reducedObj.positive += value.positive;
            });

            return reducedObj
        }
        """)

    set_finalize = Code("""
        function(key, values){
            fin_obj = {
                name: key.name,
                lat: key.lat,
                lng: key.lng,
                score: this.score,
                reviews: values.count,
                positive: values.positive
            }
            return fin_obj
        }
        """)

    result = db.reviews.map_reduce(set_map, set_reduce, "results", finalize=set_finalize)
    find_result = result.find({"value.score": {
            "$lt": c_max,
            "$gt": c_min}
        },
        {
            '_id': 0,
            'value': 1
        }
    )

    return find_result

# This is to get the data from the map reduce datasset and show the visualization

@app.callback(
    [Output('topo', 'figure'),
   Output('output-container-range-slider', 'children')],
    [Input('the_title', 'children'),
     Input('my-range-slider', 'value')])
def update_charts(title, range):
    try:
        find_result = db.results.find({"value.score": {
                "$lt": range[1],
                "$gt": range[0]}
            },
            {
                '_id': 0,
                'value': 1
            }
        )
    except:
        find_result = custom_mr(range[0], range[1])

    result_list = [x['value'] for x in find_result]
    result_df = pd.DataFrame(result_list)
    result_df['label'] = result_df['name'] + ' Score: ' + result_df['score'].map(str)

    fig = [go.Scattermapbox(
        lat=list(result_df['lat']),
        lon=list(result_df['lng']),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=list(result_df['label'])
    )]

    return [{
        'data': fig,
        'layout': go.Layout(
            autosize=True,
            hovermode='closest',
            mapbox=go.layout.Mapbox(
                accesstoken=ACCESS_TOKEN,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=48.203745,
                    lon=16.335677
                ),
                pitch=0,
                zoom=10
            ),
            height=500
        )
    }, 'Filtering between {} and {}'.format(range[0], range[1])]


if __name__ == '__main__':
    app.run_server(debug=True)