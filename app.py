"""
Asymmetric Cryptoization Dashboard
Standalone version for Render deployment
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os

# ============ DATA LOADING ============

# Load pre-processed data
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'monthly_data.csv')

def load_data():
    """Load the pre-processed monthly data."""
    df = pd.read_csv(DATA_PATH)
    df['month'] = pd.to_datetime(df['month'])
    return df

# ============ CONSTANTS ============

COLORS = {
    'Stablecoins': '#4A7C59',  # Green
    'Unbacked': '#E59400',      # Orange
}

# ============ APP SETUP ============

app = dash.Dash(
    __name__,
    title="Asymmetric Cryptoization",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

server = app.server  # For Render

# ============ LAYOUT ============

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Asymmetric Cryptoization", style={'marginBottom': '5px'}),
        html.P("Stablecoins in EMDEs, unbacked crypto in AEs — evidence from 16 exchanges", 
               style={'color': '#666', 'fontSize': '16px', 'marginTop': '0'}),
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("View:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.RadioItems(
                id='view-type',
                options=[
                    {'label': ' Percentage', 'value': 'pct'},
                    {'label': ' Volume (USD)', 'value': 'abs'},
                ],
                value='pct',
                inline=True,
                style={'display': 'inline-block'}
            ),
        ], style={'display': 'inline-block', 'marginRight': '40px'}),
        
        html.Div([
            html.Label("Crypto type:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Checklist(
                id='crypto-types',
                options=[
                    {'label': ' Stablecoins', 'value': 'Stablecoins'},
                    {'label': ' Unbacked', 'value': 'Unbacked'},
                ],
                value=['Stablecoins', 'Unbacked'],
                inline=True,
                style={'display': 'inline-block'}
            ),
        ], style={'display': 'inline-block'}),
    ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '0 20px'}),
    
    # Chart
    dcc.Graph(id='main-chart', style={'height': '500px'}),
    
    # Footer
    html.Div([
        html.P([
            "Data: 16 exchanges, 27 fiat currencies (excl. USD), Jan 2020–Jan 2026. ",
            html.A("Read the full article on LinkedIn", href="https://linkedin.com/in/emilianogiupponi", target="_blank"),
            " | ",
            html.A("GitHub", href="https://github.com/emilianogiupponi", target="_blank"),
        ], style={'fontSize': '12px', 'color': '#888'}),
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1000px', 'margin': '0 auto'})

# ============ CALLBACKS ============

@app.callback(
    Output('main-chart', 'figure'),
    [Input('view-type', 'value'),
     Input('crypto-types', 'value')]
)
def update_chart(view_type, crypto_types):
    df = load_data()
    
    if not crypto_types:
        crypto_types = ['Stablecoins', 'Unbacked']
    
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=['Advanced Economies (AEs)', 'Emerging Markets (EMDEs)'],
        horizontal_spacing=0.08
    )
    
    y_col = 'pct' if view_type == 'pct' else 'volume_usd'
    
    for i, region in enumerate(['AEs', 'EMDEs'], 1):
        region_data = df[df['region'] == region]
        
        for crypto_type in crypto_types:
            type_data = region_data[region_data['crypto_type'] == crypto_type].sort_values('month')
            
            if view_type == 'abs':
                y_values = type_data[y_col] / 1e9  # Convert to billions
                hover_template = '%{x|%b %Y}<br>$%{y:.1f}B<extra></extra>'
            else:
                y_values = type_data[y_col]
                hover_template = '%{x|%b %Y}<br>%{y:.1f}%<extra></extra>'
            
            fig.add_trace(
                go.Bar(
                    x=type_data['month'],
                    y=y_values,
                    name=crypto_type,
                    marker_color=COLORS[crypto_type],
                    showlegend=(i == 1),
                    hovertemplate=hover_template
                ),
                row=1, col=i
            )
    
    y_title = 'Share (%)' if view_type == 'pct' else 'Volume (USD billions)'
    y_range = [0, 100] if view_type == 'pct' else None
    
    fig.update_layout(
        barmode='stack',
        height=450,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=50, r=50, t=50, b=80),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    
    fig.update_yaxes(title_text=y_title, range=y_range, row=1, col=1)
    fig.update_yaxes(range=y_range, row=1, col=2)
    fig.update_xaxes(tickformat='%Y', dtick='M12')
    
    return fig

# ============ RUN ============

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
