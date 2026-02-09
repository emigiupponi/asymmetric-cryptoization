"""
Asymmetric Cryptoization Dashboard
Full version for Render deployment - matching local dashboard style
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
import requests
import base64
from datetime import datetime

# ============ CONSTANTS ============

AE_CURRENCIES = {'AUD', 'CAD', 'CHF', 'CZK', 'EUR', 'GBP', 'JPY', 'KRW', 'SGD', 'USD'}
EMDE_CURRENCIES = {'AED', 'ARS', 'BRL', 'COP', 'ERN', 'IDR', 'INR', 'MNT', 'MXN', 'NGN', 
                   'PLN', 'RON', 'RUB', 'SCR', 'THB', 'TRY', 'UAH', 'ZAR'}

STABLECOINS = {'usdt', 'usdc', 'busd', 'dai', 'tusd', 'usdp', 'gusd', 'frax', 'lusd', 
               'usdd', 'eurs', 'eurt', 'pyusd', 'fdusd', 'usde'}

# ============ WORLD BANK DATA STYLE ============
# Exact values from https://data.worldbank.org/main.css
# body { background: #f2f3f6; color: #50595E; font-family: "OpenSans", sans-serif; }
# a { color: #0071BC; } a:hover { color: #0066a9; }
# h1,h2,h3... { color: #08151e; font-weight: 600; line-height: 140%; }
# .tabs .tab-item a { height: 47px; padding: 10px 20px; color: #557387; }
# .tabs .tab-item a.active { border-bottom: 2px solid #0071BC; color: #0071BC; font-weight: 600; }
# .wrapper { max-width: 90%; width: 1160px; margin: 0 auto; }
# .button { background: #f6f7f8; box-shadow: 0 2px 0 #eff0f1; border-radius: 2px; padding: 4px 20px; }
# .button.primary { background: #F16067; box-shadow: 0 2px 0 #d9565d; color: #FFF; }
# label { font-size: 12px; text-transform: uppercase; margin: 0 0 4px; }
# .select select { background: #f2f3f6; box-shadow: 0 2px 0 #ebecef; font-weight: 600; }

# World Bank Brand Colors (exact from CSS)
WB = {
    'primary': '#0071BC',           # Links, active tabs, focus
    'primary_hover': '#0066a9',     # Link hover
    'primary_active': '#0071BC',    # Link active
    'text': '#50595E',              # Body text color
    'text_dark': '#333333',         # Headings h1-h6 (80% grey, never pure black)
    'text_muted': '#6C6F73',        # Muted text, labels
    'text_light': '#666666',        # Inactive tabs, secondary text (softer grey)
    'background': '#f2f3f6',        # Page background (grey)
    'surface': '#FFFFFF',           # Cards, panels, header
    'border': '#e4e9ec',            # Main borders
    'border_light': '#f6f7f8',      # Light borders, disabled
    'button_bg': '#f6f7f8',         # Button background
    'button_shadow': '#eff0f1',     # Button box-shadow
    'button_secondary_bg': '#f2f3f6',  # Secondary button bg
    'button_secondary_shadow': '#ebecef',  # Secondary button shadow
    'red': '#F16067',               # Primary CTA button
    'red_shadow': '#d9565d',        # Primary button shadow
    'highlight': '#E8F6FE',         # Highlighted selection
    'modal_bg': '#f2f3f6',          # Modal background
}

# Chart colors (FSB style: BTC/USDT 100% opacity, rest 50%)
COLORS = {
    # Unbacked: Naranja BTC
    'btc': '#E59400',                      # BTC naranja 100%
    'Unbacked': 'rgba(229, 148, 0, 0.5)',  # Resto unbacked 50%
    'eth': 'rgba(229, 148, 0, 0.5)',       # ETH mismo tono 50%
    'other unbacked': 'rgba(229, 148, 0, 0.5)',
    # Stablecoins: Verde USDT
    'usdt': '#4A7C59',                     # USDT verde 100%
    'Stablecoins': 'rgba(74, 124, 89, 0.5)',  # Resto stables 50%
    'usdc': 'rgba(74, 124, 89, 0.5)',      # USDC mismo tono 50%
    'usdc + other': 'rgba(74, 124, 89, 0.5)',
    # Regiones (mismo esquema)
    'AEs': '#E59400',                      # AEs naranja
    'EMDEs': '#4A7C59',                    # EMDEs verde
    'otros': '#999999',                    # Gris para otros
}

# Typography - OpenSans (clean, elegant)
FONT = "'Open Sans', 'Segoe UI', Roboto, sans-serif"

# ============ STYLES (from WB CSS) ============

# Body/Container - exact from WB CSS: body { background: #f2f3f6; color: #50595E; ... }
CONTAINER_STYLE = {
    'fontFamily': FONT,
    'fontSize': '16px',              # font-size: 1.6rem
    'lineHeight': '140%',            # line-height: 140%
    'color': WB['text'],             # color: #50595E
    'backgroundColor': WB['background'],  # background: #f2f3f6
    'margin': '0',
    'padding': '0',
    'minHeight': '100vh',
    'textAlign': 'center',
    'fontWeight': 'normal',          # font-weight: normal
    'position': 'relative',          # position: relative
    'WebkitFontSmoothing': 'antialiased',
}

# Header - #header from WB CSS: background: #fff; border-bottom for separation
HEADER_STYLE = {
    'backgroundColor': WB['surface'],  # background: #fff
    'fontSize': '14px',                 # font-size: 1.4rem
    'height': 'auto',
    'textAlign': 'right',
    'position': 'relative',
    'borderBottom': f"1px solid {WB['border']}",  # border-bottom like WB header
}

# #header .wrapper from WB CSS
HEADER_INNER_STYLE = {
    'maxWidth': '90%',
    'width': '1160px',
    'margin': '0 auto',
    'padding': '0',
    'height': '40px',                   # height: 40px
    'display': 'flex',
    'alignItems': 'center',             # align-items: center
    'justifyContent': 'space-between',  # justify-content: space-between
    'textAlign': 'center',
}

# Main content wrapper - .wrapper from WB CSS
WRAPPER_STYLE = {
    'maxWidth': '90%',
    'width': '1160px',
    'margin': '0 auto',
    'padding': '0',
    'textAlign': 'left',
}

# Card style - white with border
CARD_STYLE = {
    'backgroundColor': WB['surface'],
    'border': f"1px solid {WB['border']}",
    'borderRadius': '2px',
    'marginBottom': '20px',
}

# Title styles - h2 size from WB CSS (indicator titles use smaller size)
TITLE_STYLE = {
    'fontFamily': FONT,
    'fontSize': '24px',                 # font-size: 2.4rem (like WB indicator titles)
    'fontWeight': '600',                # font-weight: 600
    'lineHeight': '140%',               # line-height: 140%
    'color': WB['text_dark'],           # color: #08151e
    'margin': '0 0 5px',                # tighter margin like WB
}

# Subtitle/description - p from WB CSS: font-size: 1.3rem; margin: 0 0 20px;
SUBTITLE_STYLE = {
    'fontFamily': FONT,
    'fontSize': '13px',                 # font-size: 1.3rem
    'fontWeight': '400',
    'color': WB['text'],                # color: #50595E (inherited)
    'margin': '0 0 20px',               # margin: 0 0 20px
}

# Tabs style - .tabs from WB CSS: font-size: 1.4rem; position: relative; width: 100%;
TABS_STYLE = {
    'fontSize': '14px',                 # font-size: 1.4rem
    'position': 'relative',
    'width': '100%',
    'marginBottom': '0',
}

# .tabs .tab-item a from WB CSS
TAB_ITEM_STYLE = {
    'display': 'inline-block',
    'padding': '10px 20px',             # padding: 10px 20px
    'cursor': 'pointer',
    'borderBottom': '2px solid transparent',  # border-bottom: 2px solid transparent
    'marginBottom': '-1px',             # margin-bottom: -1px
    'color': WB['text_light'],          # color: #557387
    'fontSize': '14px',
    'textDecoration': 'none',
    'boxSizing': 'border-box',          # box-sizing: border-box
    'height': '47px',                   # height: 47px
    'textAlign': 'center',              # text-align: center
}

# .tabs .tab-item a.active from WB CSS
TAB_ITEM_ACTIVE_STYLE = {
    **TAB_ITEM_STYLE,
    'borderBottomColor': WB['primary'], # border-bottom-color: #0071BC
    'color': WB['primary'],             # color: #0071BC
    'fontWeight': '600',                # font-weight: 600
}

# Chart block - white card with border (like WB cards)
CHART_BLOCK_STYLE = {
    'backgroundColor': WB['surface'],   # background-color: #fff
    'border': f"1px solid {WB['border']}",  # border: 1px solid #e4e9ec
    'borderRadius': '2px',              # border-radius: 2px
    'padding': '20px',
    'boxShadow': 'rgba(0, 0, 0, 0.03) 0 1px 0 0',  # subtle shadow like WB
}

# Sidebar panel - like WB sidebar/dropdown
SIDEBAR_STYLE = {
    'backgroundColor': WB['surface'],   # background: #FFF
    'border': f"1px solid {WB['border']}",  # border: 1px solid #e4e9ec
    'borderRadius': '2px',              # border-radius: 2px
    'boxShadow': 'rgba(0, 0, 0, 0.03) 0 1px 0 0',  # box-shadow from .dropdown .options
}

# Dropdown style
DROPDOWN_STYLE = {
    'width': '100%',
    'marginBottom': '10px',
    'fontFamily': FONT,
    'fontSize': '14px',
}

# Radio/control style - .button from WB CSS
RADIO_STYLE = {
    'display': 'inline-block',
    'marginRight': '16px',
    'fontSize': '14px',
    'color': WB['text'],
}

# Button style - .button from WB CSS
BUTTON_STYLE = {
    'backgroundColor': WB['button_bg'], # background: #f6f7f8
    'border': '0',                      # border: 0
    'borderRadius': '2px',              # border-radius: 2px
    'boxShadow': f"0 2px 0 {WB['button_shadow']}",  # box-shadow: 0 2px 0 #eff0f1
    'color': 'inherit',                 # color: inherit
    'display': 'inline-block',          # display: inline-block
    'padding': '4px 20px',              # padding: 4px 20px
    'fontSize': '14px',                 # font-size: 1.4rem
    'outline': 'none',                  # outline: none
    'textAlign': 'center',              # text-align: center
    'boxSizing': 'border-box',          # box-sizing: border-box
    'cursor': 'pointer',
}

# Label style - label, .label from WB CSS
LABEL_STYLE = {
    'fontSize': '12px',                 # font-size: 1.2rem
    'color': 'inherit',                 # color: inherit
    'margin': '0 0 4px',                # margin: 0 0 4px
    'display': 'block',                 # display: block
    'textTransform': 'uppercase',       # text-transform: uppercase
}

# Select style - .select from WB CSS
SELECT_STYLE = {
    'fontWeight': '600',                # font-weight: 600
    'position': 'relative',
}

# Indicator tag style - span.indicator from WB CSS (the blue tags)
INDICATOR_TAG_STYLE = {
    'backgroundColor': WB['primary'],   # background: #0071BC
    'borderRadius': '2px',              # border-radius: 2px
    'color': '#fff',                    # color: #fff
    'display': 'inline-block',          # display: inline-block
    'fontSize': '14px',                 # font-size: 14px
    'height': '30px',                   # height: 30px
    'lineHeight': '30px',               # line-height: 30px
    'margin': '0 4px 4px 0',            # margin: 0px 4px 0px 0
    'maxWidth': '180px',                # max-width: 180px
    'overflow': 'hidden',               # overflow: hidden
    'textOverflow': 'ellipsis',         # text-overflow: ellipsis
    'padding': '0 12px',                # padding: 0 20px (reduced)
    'whiteSpace': 'nowrap',             # white-space: nowrap
}

# Sidebar analysis panel - grey background like WB sidebar
ANALYSIS_PANEL_STYLE = {
    'backgroundColor': '#f2f3f6',       # light grey background
    'borderRadius': '2px',
    'padding': '0',
    'border': '1px solid #e4e4e4',
}

# Analysis list item style
ANALYSIS_ITEM_STYLE = {
    'display': 'table',
    'width': '100%',
    'padding': '8px 12px',
    'boxSizing': 'border-box',
    'borderBottom': f"1px solid {WB['border']}",
    'backgroundColor': WB['surface'],
    'marginBottom': '1px',
}

# Button group style (for controls like Also Show, Share, Details)
BUTTON_GROUP_STYLE = {
    'display': 'flex',
    'gap': '8px',
    'alignItems': 'center',
}

# ============ DATA LOADING ============

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'full_data.csv')

def load_data():
    """Load the full monthly data."""
    df = pd.read_csv(DATA_PATH)
    df['month'] = pd.to_datetime(df['month'])
    return df

# Load data once at startup
_data = load_data()
_min_date = _data['month'].min()
_max_date = _data['month'].max()

def _month_index(ts):
    return ts.year * 12 + (ts.month - 1)

def _index_to_date(idx):
    year = idx // 12
    month = (idx % 12) + 1
    return pd.Timestamp(year=year, month=month, day=1)

_min_idx = _month_index(_min_date)
_max_idx = _month_index(_max_date)

# Build slider marks (years only)
_marks = {}
for year in range(_min_date.year, _max_date.year + 1):
    idx = year * 12  # January
    if idx >= _min_idx and idx <= _max_idx:
        _marks[idx] = {'label': str(year), 'style': {'fontSize': '11px'}}

# Default: last 24 months
_default_end_idx = _max_idx
_default_start_idx = max(_min_idx, _max_idx - 23)

# Build options
_exchanges = sorted(_data['exchange'].unique())
_fiats = sorted(_data['quote_asset'].unique())
_cryptos = sorted(_data['base_asset'].unique())

EXCHANGE_OPTIONS = [{'label': '🌐 All Exchanges', 'value': 'all'}] + \
                   [{'label': e.title(), 'value': e} for e in _exchanges] + \
                   [{'label': '───── EXCLUDE ─────', 'value': 'SEP_EXCL', 'disabled': True}] + \
                   [{'label': f'❌ {e.title()}', 'value': f'EXCL:{e}'} for e in _exchanges]

# Fiat to country name mapping (complete)
FIAT_TO_COUNTRY_NAME = {
    # LATAM
    'ars': 'Argentina', 'brl': 'Brazil', 'mxn': 'Mexico', 'clp': 'Chile',
    'cop': 'Colombia', 'pen': 'Peru',
    # North America
    'usd': 'USA', 'cad': 'Canada',
    # Europe
    'eur': 'Eurozone', 'gbp': 'UK', 'chf': 'Switzerland', 'pln': 'Poland',
    'czk': 'Czech', 'sek': 'Sweden', 'nok': 'Norway', 'dkk': 'Denmark',
    'ron': 'Romania', 'bgn': 'Bulgaria', 'hrk': 'Croatia',
    # Asia-Pacific
    'jpy': 'Japan', 'krw': 'Korea', 'cny': 'China', 'hkd': 'Hong Kong',
    'sgd': 'Singapore', 'inr': 'India', 'aud': 'Australia', 'nzd': 'New Zealand',
    'thb': 'Thailand', 'php': 'Philippines', 'idr': 'Indonesia', 'myr': 'Malaysia',
    'vnd': 'Vietnam', 'pkr': 'Pakistan', 'bdt': 'Bangladesh', 'lkr': 'Sri Lanka',
    # Middle East / Africa
    'try': 'Turkey', 'sar': 'Saudi Arabia', 'aed': 'UAE', 'ils': 'Israel',
    'zar': 'South Africa', 'egp': 'Egypt', 'ngn': 'Nigeria', 'kwd': 'Kuwait',
    'bhd': 'Bahrain', 'omr': 'Oman', 'qar': 'Qatar', 'jod': 'Jordan',
    # Eastern Europe
    'rub': 'Russia', 'uah': 'Ukraine', 'kzt': 'Kazakhstan',
    # Special
    'scr': 'Seychelles', 'ern': 'Eritrea', 'mnt': 'Mongolia',
}

# Load crypto names from metadata file
def _load_crypto_names():
    metadata_path = os.path.join(os.path.dirname(__file__), 'data', 'reference', 'asset-metadata.csv')
    if os.path.exists(metadata_path):
        df = pd.read_csv(metadata_path, encoding='utf-8')
        return dict(zip(df['codigo'].str.lower(), df['nombre']))
    # Fallback to hardcoded names
    return {
        'btc': 'Bitcoin', 'eth': 'Ethereum', 'usdt': 'Tether', 'usdc': 'USD Coin',
        'xrp': 'Ripple', 'bnb': 'Binance Coin', 'ada': 'Cardano', 'doge': 'Dogecoin',
    }

CRYPTO_NAMES = _load_crypto_names()

# Build fiat options with country names
def _build_fiat_options():
    options = [
        {'label': '⭐ AEs only', 'value': 'SPECIAL:AE'},
        {'label': '⭐ EMDEs only', 'value': 'SPECIAL:EMDE'},
        {'label': '⭐ AEs vs EMDEs', 'value': 'SPECIAL:AE_VS_EMDE'},
        {'label': '─────────────', 'value': 'SEP', 'disabled': True},
    ]
    for f in _fiats:
        country = FIAT_TO_COUNTRY_NAME.get(f, '')
        label = f"{f.upper()} ({country})" if country else f.upper()
        options.append({'label': label, 'value': f})
    
    options.append({'label': '───── EXCLUDE ─────', 'value': 'SEP_EXCL', 'disabled': True})
    for f in _fiats:
        country = FIAT_TO_COUNTRY_NAME.get(f, '')
        label = f"❌ {f.upper()} ({country})" if country else f"❌ {f.upper()}"
        options.append({'label': label, 'value': f'EXCL:{f}'})
    return options

FIAT_OPTIONS = _build_fiat_options()

# Build crypto options with full names
def _build_crypto_options():
    options = [
        {'label': '⭐ Stablecoins vs Unbacked', 'value': 'SPECIAL:STABLE_VS_UNBACKED'},
        {'label': '⭐ USDT+Stables vs BTC+Unbacked (4 series)', 'value': 'SPECIAL:FSB_4CAT'},
        {'label': '⭐ All Stablecoins', 'value': 'SPECIAL:STABLECOINS'},
        {'label': '⭐ All Unbacked', 'value': 'SPECIAL:UNBACKED'},
        {'label': '─────────────', 'value': 'SEP', 'disabled': True},
    ]
    for c in _cryptos:
        name = CRYPTO_NAMES.get(c, '')
        label = f"{c.upper()} ({name})" if name else c.upper()
        options.append({'label': label, 'value': c})
    
    options.append({'label': '───── EXCLUDE ─────', 'value': 'SEP_EXCL', 'disabled': True})
    for c in _cryptos:
        name = CRYPTO_NAMES.get(c, '')
        label = f"❌ {c.upper()} ({name})" if name else f"❌ {c.upper()}"
        options.append({'label': label, 'value': f'EXCL:{c}'})
    return options

CRYPTO_OPTIONS = _build_crypto_options()

# ============ APP SETUP ============

# Custom CSS to remove dropdown borders
CUSTOM_CSS = '''
.Select-control {
    border: none !important;
    background-color: transparent !important;
}
.Select-multi-value-wrapper {
    border: none !important;
}
.Select--multi .Select-value {
    border: none !important;
    background-color: #0071BC !important;
    color: white !important;
}
.Select--multi .Select-value-icon {
    border-right: none !important;
}
'''

app = dash.Dash(
    __name__,
    title="Asymmetric Cryptoization",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True
)

# Inject custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-28ZQMWHPQZ"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-28ZQMWHPQZ');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        /* Dash Dropdown - remove ALL borders */
        .dash-dropdown,
        .dash-dropdown *,
        .Select,
        .Select * {
            border: none !important;
            outline: none !important;
        }
        .dash-dropdown .Select-control {
            background-color: transparent !important;
            box-shadow: none !important;
        }
        /* Menu dropdown - remove border, add shadow */
        .Select-menu-outer,
        .dash-dropdown .Select-menu-outer {
            border: none !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
            margin-top: 2px !important;
        }
        /* Tags - blue like WB */
        .Select--multi .Select-value {
            border: none !important;
            background-color: #0071BC !important;
            color: white !important;
            border-radius: 2px !important;
        }
        .Select--multi .Select-value-icon {
            border: none !important;
        }
        .Select--multi .Select-value-label {
            color: white !important;
        }
        /* Placeholder - grey italic */
        .Select-placeholder {
            color: #999 !important;
            font-style: italic !important;
        }
        /* Menu options */
        .VirtualizedSelectOption {
            padding: 8px 12px !important;
            border: none !important;
        }
        .VirtualizedSelectFocusedOption {
            background-color: #f2f3f6 !important;
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

server = app.server

# ============ LAYOUT ============

app.layout = html.Div(style=CONTAINER_STYLE, children=[
    # ===== HEADER (white bar like WB with border-bottom) =====
    html.Header(style=HEADER_STYLE, children=[
        html.Div(style=HEADER_INNER_STYLE, children=[
            # Logo area
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.Span("Asymmetric Cryptoization", style={
                    'color': WB['text_dark'],
                    'fontSize': '14px',
                    'fontWeight': '600',
                    'fontFamily': FONT,
                }),
                html.Span("Data", style={
                    'color': WB['text_dark'],
                    'fontSize': '12px',
                    'fontWeight': 'bold',
                    'marginLeft': '10px',
                    'paddingLeft': '10px',
                    'borderLeft': f"1px solid {WB['text_dark']}",
                }),
            ]),
        ]),
    ]),
    
    # ===== SELECTOR BAR (white background, grey boxes NO borders, aligned left) =====
    html.Div(style={'backgroundColor': WB['surface'], 'borderBottom': f"1px solid {WB['border']}", 'padding': '15px 0'}, children=[
        html.Div(style={**WRAPPER_STYLE}, children=[
            # Container for dropdowns - width matches chart column (flex:2 = ~66%), aligned LEFT
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '6px', 'width': '66%'}, children=[
                # Each dropdown with grey background, NO border, compact padding, search mode
                html.Div(style={'backgroundColor': WB['background'], 'borderRadius': '2px', 'padding': '4px 8px'}, children=[
                    dcc.Dropdown(
                        id='exchange-selector',
                        options=EXCHANGE_OPTIONS,
                        value=[],
                        multi=True,
                        placeholder='Search exchanges...',
                        searchable=True,
                        optionHeight=35,
                        style={'width': '100%', 'fontSize': '14px', 'border': 'none'}
                    ),
                ]),
                html.Div(style={'backgroundColor': WB['background'], 'borderRadius': '2px', 'padding': '4px 8px'}, children=[
                    dcc.Dropdown(
                        id='fiat-selector',
                        options=FIAT_OPTIONS,
                        value=[],
                        multi=True,
                        placeholder='Search fiat currencies...',
                        searchable=True,
                        optionHeight=35,
                        style={'width': '100%', 'fontSize': '14px', 'border': 'none'}
                    ),
                ]),
                html.Div(style={'backgroundColor': WB['background'], 'borderRadius': '2px', 'padding': '4px 8px'}, children=[
                    dcc.Dropdown(
                        id='crypto-selector',
                        options=CRYPTO_OPTIONS,
                        value=[],
                        multi=True,
                        placeholder='Search crypto assets...',
                        searchable=True,
                        optionHeight=35,
                        style={'width': '100%', 'fontSize': '14px', 'border': 'none'}
                    ),
                ]),
            ]),
        ]),
    ]),
    
    # ===== MAIN CONTENT WRAPPER =====
    html.Div(style={**WRAPPER_STYLE, 'marginTop': '25px', 'marginBottom': '60px'}, children=[
        
        # Title section (dynamic - updated by callback)
        html.Div(id='indicator-title', style={'marginBottom': '10px'}, children=[
            html.H1("Crypto Trading Volume", style=TITLE_STYLE),
            html.P("Select filters to see analysis.", style=SUBTITLE_STYLE),
        ]),
        
        
        # ===== MAIN CONTENT AREA =====
        html.Div(style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap', 'marginTop': '20px'}, children=[
            
            # LEFT: Chart area (wider)
            html.Div(style={'flex': '2', 'minWidth': '500px'}, children=[
                
                # Chart block (white card)
                html.Div(style=CHART_BLOCK_STYLE, children=[
                    # Controls row - flat buttons style (no shadow, like WB)
                    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '16px', 'marginBottom': '16px', 
                                    'alignItems': 'center', 'borderBottom': f"1px solid {WB['border']}", 
                                    'paddingBottom': '12px'}, children=[
                        # View type - flat button style
                        html.Div(children=[
                            dcc.RadioItems(
                                id='view-selector',
                                options=[
                                    {'label': 'Evolution', 'value': 'evolution'},
                                    {'label': 'Ranking', 'value': 'ranking'},
                                ],
                                value='evolution',
                                inline=True,
                                className='wb-radio-buttons',
                                labelStyle={'display': 'inline-block', 'padding': '6px 14px', 'marginRight': '0',
                                           'backgroundColor': 'transparent', 'cursor': 'pointer',
                                           'fontSize': '13px', 'color': WB['text_muted'], 'fontWeight': '400'},
                                inputStyle={'display': 'none'}
                            ),
                        ]),
                        # Frequency
                        html.Div(children=[
                            dcc.RadioItems(
                                id='frequency-selector',
                                options=[
                                    {'label': 'Monthly', 'value': 'M'},
                                    {'label': 'Daily', 'value': 'D'},
                                ],
                                value='M',
                                inline=True,
                                className='wb-radio-buttons',
                                labelStyle={'display': 'inline-block', 'padding': '6px 14px', 'marginRight': '0',
                                           'backgroundColor': 'transparent', 'cursor': 'pointer',
                                           'fontSize': '13px', 'color': WB['text_muted'], 'fontWeight': '400'},
                                inputStyle={'display': 'none'}
                            ),
                        ]),
                        # Stacking
                        html.Div(children=[
                            dcc.RadioItems(
                                id='stacking-selector',
                                options=[
                                    {'label': 'Absolute', 'value': 'absolute'},
                                    {'label': '100%', 'value': 'percent'},
                                ],
                                value='absolute',
                                inline=True,
                                className='wb-radio-buttons',
                                labelStyle={'display': 'inline-block', 'padding': '6px 14px', 'marginRight': '0',
                                           'backgroundColor': 'transparent', 'cursor': 'pointer',
                                           'fontSize': '12px'},
                                inputStyle={'display': 'none'}
                            ),
                        ]),
                        # Metric - flat style
                        html.Div(children=[
                            dcc.RadioItems(
                                id='metric-selector',
                                options=[
                                    {'label': 'Vol. USD', 'value': 'volume_usd'},
                                    {'label': 'Trades', 'value': 'number_of_trades'},
                                ],
                                value='volume_usd',
                                inline=True,
                                className='wb-radio-buttons',
                                labelStyle={'display': 'inline-block', 'padding': '6px 14px', 'marginRight': '0',
                                           'backgroundColor': 'transparent', 'cursor': 'pointer',
                                           'fontSize': '13px', 'color': WB['text_muted'], 'fontWeight': '400'},
                                inputStyle={'display': 'none'}
                            ),
                        ]),
                    ]),
                    
                    # Chart
                    dcc.Graph(id='main-chart', style={'height': '400px'}),
                    
                    # Date slider
                    html.Div(style={'marginTop': '16px'}, children=[
                        dcc.RangeSlider(
                            id='date-slider',
                            min=_min_idx,
                            max=_max_idx,
                            step=1,
                            marks=_marks,
                            value=[_default_start_idx, _default_end_idx],
                            allowCross=False,
                            tooltip={'placement': 'bottom', 'always_visible': False}
                        ),
                        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '8px'}, 
                                 children=[
                            html.Span(id='date-start-label', 
                                     style={'backgroundColor': WB['primary'], 'color': '#fff', 'borderRadius': '2px',
                                            'padding': '3px 10px', 'fontSize': '11px', 'fontFamily': FONT}),
                            html.Span(id='date-end-label',
                                     style={'backgroundColor': WB['primary'], 'color': '#fff', 'borderRadius': '2px',
                                            'padding': '3px 10px', 'fontSize': '11px', 'fontFamily': FONT}),
                        ]),
                    ]),
                    
                    # Hidden chart type selector (controlled by tabs)
                    dcc.RadioItems(
                        id='chart-type-selector',
                        options=[
                            {'label': 'Bar', 'value': 'bar'},
                            {'label': 'Line', 'value': 'line'},
                        ],
                        value='bar',
                        style={'display': 'none'}
                    ),
                ]),  # End chart block
            ]),  # End left column
            
            # RIGHT: Analysis panel (grey, table format, dynamic)
            html.Div(style={'flex': '1', 'minWidth': '300px'}, children=[
                html.Div(style={'backgroundColor': '#e8eaed', 'borderRadius': '2px', 'padding': '0'}, children=[
                    # Table header row
                    html.Div(style={'display': 'flex', 'padding': '10px 12px', 'borderBottom': '1px solid #d5d8dc',
                                   'fontSize': '11px', 'color': '#666', 'fontWeight': '600'}, children=[
                        html.Div("Metric", style={'flex': '2'}),
                        html.Div("Level", style={'flex': '1', 'textAlign': 'right'}),
                        html.Div("M/M", style={'flex': '1', 'textAlign': 'right'}),
                        html.Div("Y/Y", style={'flex': '1', 'textAlign': 'right'}),
                    ]),
                    # Dynamic data rows (updated by callback)
                    html.Div(id='analysis-rows'),
                    # Footer links
                    html.Div(style={'padding': '12px 15px', 'textAlign': 'center', 'borderTop': '1px solid #d5d8dc'}, children=[
                        html.A("LinkedIn Article", href="https://www.linkedin.com/pulse/asymmetric-cryptoization-update-expanded-exchange-data-giupponi", 
                               target="_blank", style={'color': WB['primary'], 'fontSize': '12px', 'textDecoration': 'none'}),
                        html.Span(" · ", style={'color': '#999', 'margin': '0 5px'}),
                        html.A("GitHub", href="https://github.com/emigiupponi/asymmetric-cryptoization", 
                               target="_blank", style={'color': WB['primary'], 'fontSize': '12px', 'textDecoration': 'none'}),
                    ]),
                    # Download Data button
                    html.Div(style={'padding': '12px 15px', 'textAlign': 'center', 'borderTop': '1px solid #d5d8dc'}, children=[
                        html.Button("Download Data", id='btn-open-download', n_clicks=0,
                                    style={'backgroundColor': WB['primary'], 'color': '#fff', 'border': 'none',
                                           'borderRadius': '2px', 'padding': '8px 24px', 'fontSize': '13px',
                                           'cursor': 'pointer', 'fontFamily': FONT, 'fontWeight': '600'}),
                    ]),
                ]),
            ]),  # End right column
            
        ]),  # End main content area
    ]),  # End wrapper
    
    # ===== DOWNLOAD MODAL =====
    html.Div(id='download-modal', style={'display': 'none', 'position': 'fixed', 'top': '0', 'left': '0',
                                          'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)',
                                          'zIndex': '9999', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        html.Div(style={'backgroundColor': '#fff', 'borderRadius': '4px', 'padding': '30px', 'width': '420px',
                        'maxWidth': '90%', 'margin': 'auto', 'marginTop': '15vh', 'boxShadow': '0 4px 20px rgba(0,0,0,0.15)'}, children=[
            html.H3("Download Data", style={'margin': '0 0 6px 0', 'color': WB['text_dark'], 'fontSize': '18px', 'fontFamily': FONT}),
            html.P("Please provide your institutional details for our records.", 
                   style={'color': WB['text_muted'], 'fontSize': '13px', 'margin': '0 0 20px 0', 'fontFamily': FONT}),
            # Name
            html.Label("Name", style={'fontSize': '12px', 'color': WB['text_muted'], 'textTransform': 'uppercase', 
                                      'fontWeight': '600', 'fontFamily': FONT}),
            dcc.Input(id='download-name', type='text', placeholder='Your name',
                     style={'width': '100%', 'padding': '8px 12px', 'border': f"1px solid {WB['border']}", 
                            'borderRadius': '2px', 'fontSize': '14px', 'marginBottom': '12px', 'boxSizing': 'border-box'}),
            # Institution
            html.Label("Institution", style={'fontSize': '12px', 'color': WB['text_muted'], 'textTransform': 'uppercase',
                                             'fontWeight': '600', 'fontFamily': FONT}),
            dcc.Input(id='download-institution', type='text', placeholder='e.g. Bank of England',
                     style={'width': '100%', 'padding': '8px 12px', 'border': f"1px solid {WB['border']}",
                            'borderRadius': '2px', 'fontSize': '14px', 'marginBottom': '12px', 'boxSizing': 'border-box'}),
            # Email
            html.Label("Email", style={'fontSize': '12px', 'color': WB['text_muted'], 'textTransform': 'uppercase',
                                       'fontWeight': '600', 'fontFamily': FONT}),
            dcc.Input(id='download-email', type='email', placeholder='your.email@institution.org',
                     style={'width': '100%', 'padding': '8px 12px', 'border': f"1px solid {WB['border']}",
                            'borderRadius': '2px', 'fontSize': '14px', 'marginBottom': '20px', 'boxSizing': 'border-box'}),
            # Buttons
            html.Div(style={'display': 'flex', 'gap': '10px', 'justifyContent': 'flex-end'}, children=[
                html.Button("Cancel", id='btn-cancel-download', n_clicks=0,
                            style={'backgroundColor': WB['button_bg'], 'color': WB['text'], 'border': f"1px solid {WB['border']}",
                                   'borderRadius': '2px', 'padding': '8px 20px', 'fontSize': '13px', 'cursor': 'pointer'}),
                html.Button("Download CSV", id='btn-confirm-download', n_clicks=0,
                            style={'backgroundColor': WB['primary'], 'color': '#fff', 'border': 'none',
                                   'borderRadius': '2px', 'padding': '8px 20px', 'fontSize': '13px', 'cursor': 'pointer',
                                   'fontWeight': '600'}),
            ]),
            # Validation message
            html.Div(id='download-validation', style={'marginTop': '10px', 'fontSize': '12px', 'color': '#e74c3c'}),
        ]),
    ]),
    
    # Download component
    dcc.Download(id='download-data'),
])

# ============ CALLBACKS ============

@app.callback(
    Output('indicator-title', 'children'),
    [Input('fiat-selector', 'value'),
     Input('crypto-selector', 'value'),
     Input('view-selector', 'value'),
     Input('frequency-selector', 'value'),
     Input('metric-selector', 'value')]
)
def update_indicator_title(fiats, cryptos, view, freq, metric):
    """Generate dynamic title based on selections."""
    # Build fiat description
    if not fiats:
        fiat_desc = "All Regions"
    elif 'SPECIAL:AE_VS_EMDE' in fiats:
        fiat_desc = "AEs vs EMDEs"
    elif 'SPECIAL:AE' in fiats:
        fiat_desc = "Advanced Economies"
    elif 'SPECIAL:EMDE' in fiats:
        fiat_desc = "Emerging Markets"
    else:
        clean_fiats = [f for f in fiats if not f.startswith('SPECIAL:') and not f.startswith('SEP') and not f.startswith('EXCL:')]
        fiat_desc = ", ".join(f.upper() for f in clean_fiats[:3])
        if len(clean_fiats) > 3:
            fiat_desc += f" +{len(clean_fiats)-3}"
    
    # Build crypto description
    if not cryptos:
        crypto_desc = "All Cryptos"
    elif 'SPECIAL:STABLE_VS_UNBACKED' in cryptos:
        crypto_desc = "Stablecoins vs Unbacked"
    elif 'SPECIAL:STABLECOINS' in cryptos:
        crypto_desc = "Stablecoins"
    elif 'SPECIAL:UNBACKED' in cryptos:
        crypto_desc = "Unbacked Crypto"
    else:
        clean_cryptos = [c for c in cryptos if not c.startswith('SPECIAL:') and not c.startswith('SEP') and not c.startswith('EXCL:')]
        crypto_desc = ", ".join(c.upper() for c in clean_cryptos[:3])
        if len(clean_cryptos) > 3:
            crypto_desc += f" +{len(clean_cryptos)-3}"
    
    # View and frequency
    view_map = {'evolution': 'Evolution', 'ranking': 'Ranking'}
    freq_map = {'M': 'Monthly', 'D': 'Daily'}
    metric_map = {'volume_usd': 'Volume (USD)', 'number_of_trades': 'Trades'}
    
    title = f"{crypto_desc} Trading {metric_map.get(metric, metric)} — {fiat_desc}"
    subtitle = f"{view_map.get(view, view)} view, {freq_map.get(freq, freq)} data"
    
    return html.Div([
        html.H1(title, style=TITLE_STYLE),
        html.P(subtitle, style=SUBTITLE_STYLE),
    ])


@app.callback(
    [Output('date-start-label', 'children'),
     Output('date-end-label', 'children')],
    [Input('date-slider', 'value')]
)
def update_date_labels(date_range):
    start = _index_to_date(date_range[0])
    end = _index_to_date(date_range[1])
    return start.strftime('%b %Y'), end.strftime('%b %Y')


@app.callback(
    Output('main-chart', 'figure'),
    [Input('exchange-selector', 'value'),
     Input('fiat-selector', 'value'),
     Input('crypto-selector', 'value'),
     Input('view-selector', 'value'),
     Input('frequency-selector', 'value'),
     Input('stacking-selector', 'value'),
     Input('metric-selector', 'value'),
     Input('chart-type-selector', 'value'),
     Input('date-slider', 'value')]
)
def update_chart(exchanges, fiats, cryptos, view, frequency, stacking, metric, chart_type, date_range):
    df = _data.copy()
    
    # Filter by date
    start_date = _index_to_date(date_range[0])
    end_date = _index_to_date(date_range[1])
    df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    
    # Parse exclusions from selections (EXCL: prefix)
    exclude_exchanges = [e.replace('EXCL:', '') for e in (exchanges or []) if e.startswith('EXCL:')]
    exclude_fiats = [f.replace('EXCL:', '') for f in (fiats or []) if f.startswith('EXCL:')]
    exclude_cryptos = [c.replace('EXCL:', '') for c in (cryptos or []) if c.startswith('EXCL:')]
    
    # Clean selections (remove EXCL: items and separators)
    exchanges = [e for e in (exchanges or []) if not e.startswith('EXCL:') and not e.startswith('SEP')]
    fiats = [f for f in (fiats or []) if not f.startswith('EXCL:') and not f.startswith('SEP')]
    cryptos = [c for c in (cryptos or []) if not c.startswith('EXCL:') and not c.startswith('SEP')]
    
    # Apply exclusions first (leave-one-out sensitivity analysis)
    if exclude_exchanges:
        df = df[~df['exchange'].isin(exclude_exchanges)]
    if exclude_fiats:
        df = df[~df['quote_asset'].isin(exclude_fiats)]
    if exclude_cryptos:
        df = df[~df['base_asset'].isin(exclude_cryptos)]
    
    # Filter by exchange (inclusion)
    if exchanges and 'all' not in exchanges:
        df = df[df['exchange'].isin(exchanges)]
    
    # Process fiat selection
    use_region_comparison = False
    if fiats:
        special_fiats = [f for f in fiats if f.startswith('SPECIAL:')]
        individual_fiats = [f for f in fiats if not f.startswith('SPECIAL:') and f != 'SEP']
        
        if 'SPECIAL:AE_VS_EMDE' in special_fiats:
            use_region_comparison = True
            df = df[df['region'].isin(['AEs', 'EMDEs'])]
        elif 'SPECIAL:AE' in special_fiats:
            df = df[df['region'] == 'AEs']
        elif 'SPECIAL:EMDE' in special_fiats:
            df = df[df['region'] == 'EMDEs']
        elif individual_fiats:
            df = df[df['quote_asset'].isin(individual_fiats)]
    
    # Process crypto selection
    use_crypto_comparison = False
    use_fsb_4cat = False
    if cryptos:
        special_cryptos = [c for c in cryptos if c.startswith('SPECIAL:')]
        individual_cryptos = [c for c in cryptos if not c.startswith('SPECIAL:') and c != 'SEP']
        
        if 'SPECIAL:FSB_4CAT' in special_cryptos:
            use_fsb_4cat = True
        elif 'SPECIAL:STABLE_VS_UNBACKED' in special_cryptos:
            use_crypto_comparison = True
        elif 'SPECIAL:STABLECOINS' in special_cryptos:
            df = df[df['crypto_type'] == 'Stablecoins']
        elif 'SPECIAL:UNBACKED' in special_cryptos:
            df = df[df['crypto_type'] == 'Unbacked']
        elif individual_cryptos:
            df = df[df['base_asset'].isin(individual_cryptos)]
    
    if len(df) == 0:
        return go.Figure().add_annotation(text="No data for selection", showarrow=False)
    
    # Check for multiple individual fiats (need subplots)
    individual_fiats = [f for f in (fiats or []) if not f.startswith('SPECIAL:') and f != 'SEP']
    use_fiat_subplots = len(individual_fiats) > 1
    
    # FSB 4-category colors
    FSB_COLORS = {
        'USDT': '#4A7C59',                      # Verde USDT 100%
        'Other Stables': 'rgba(74, 124, 89, 0.5)',  # Verde 50%
        'BTC': '#E59400',                       # Naranja BTC 100%
        'Other Unbacked': 'rgba(229, 148, 0, 0.5)', # Naranja 50%
    }
    
    # ============================================================
    # PRE-PROCESS: Transform base_asset to reflect crypto groupings
    # (Replicates local dashboard approach from _make_evolution_fig)
    # This way, the chart-building loop ALWAYS iterates by base_asset.
    # ============================================================
    df = df.copy()
    if use_fsb_4cat:
        def _fsb_group(row):
            if row['base_asset'] == 'usdt':
                return 'USDT'
            elif row['base_asset'] == 'btc':
                return 'BTC'
            elif row.get('crypto_type') == 'Stablecoins':
                return 'Other Stables'
            else:
                return 'Other Unbacked'
        df['base_asset'] = df.apply(_fsb_group, axis=1)
    elif use_crypto_comparison:
        df['base_asset'] = df['crypto_type']  # 'Stablecoins' or 'Unbacked'
    
    # Determine region column and subplot structure
    if use_region_comparison:
        region_col = 'region'
        regions = ['AEs', 'EMDEs']
        subplot_titles = regions
    elif use_fiat_subplots:
        region_col = 'quote_asset'
        regions = individual_fiats
        subplot_titles = [FIAT_TO_COUNTRY_NAME.get(f, f.upper()) for f in individual_fiats]
    else:
        region_col = None
        regions = None
        subplot_titles = None
    
    # Merge all colors into one lookup for simplicity
    ALL_COLORS = {**COLORS, **FSB_COLORS}
    
    # ============================================================
    # BUILD FIGURE (unified logic, replicating local _make_evolution_fig)
    # ============================================================
    if regions and len(regions) >= 1:
        # --- SUBPLOT MODE: one panel per region/fiat ---
        n_panels = len(regions)
        print(f"[DEBUG CHART] Subplot mode: {n_panels} panels, regions={regions}, base_assets={sorted(df['base_asset'].unique())}")
        fig = make_subplots(rows=1, cols=n_panels, subplot_titles=subplot_titles,
                           horizontal_spacing=0.08)
        
        # Group data ONCE (like local dashboard line 880-889)
        grouped = df.groupby(['month', region_col, 'base_asset'])[metric].sum().reset_index()
        
        for col_idx, region in enumerate(regions, 1):
            region_data = grouped[grouped[region_col] == region]
            
            if region_data.empty:
                print(f"[DEBUG CHART] No data for region={region}, skipping")
                continue
            
            # Compute totals for percent stacking
            if stacking == 'percent':
                totals = region_data.groupby('month')[metric].sum().reset_index()
                totals.columns = ['month', '_total']
            
            cryptos_in_region = sorted(region_data['base_asset'].unique())
            
            for crypto in cryptos_in_region:
                crypto_data = region_data[region_data['base_asset'] == crypto].sort_values('month')
                
                if crypto_data.empty:
                    continue
                
                # Compute y values
                if stacking == 'percent':
                    crypto_data = crypto_data.merge(totals, on='month')
                    y_vals = crypto_data[metric] / crypto_data['_total'] * 100
                else:
                    y_vals = crypto_data[metric] / 1e9 if metric == 'volume_usd' else crypto_data[metric]
                
                color = ALL_COLORS.get(crypto, ALL_COLORS.get(crypto.lower(), '#999'))
                name = crypto.upper() if crypto not in FSB_COLORS else crypto
                show_legend = (col_idx == 1)
                
                if chart_type == 'bar':
                    fig.add_trace(go.Bar(
                        x=crypto_data['month'], y=y_vals,
                        name=name, marker_color=color,
                        showlegend=show_legend, legendgroup=crypto
                    ), row=1, col=col_idx)
                else:
                    fig.add_trace(go.Scatter(
                        x=crypto_data['month'], y=y_vals,
                        name=name, line=dict(color=color), mode='lines',
                        showlegend=show_legend, legendgroup=crypto
                    ), row=1, col=col_idx)
        
        fig.update_layout(barmode='stack' if chart_type == 'bar' else None)
        y_title = 'Share (%)' if stacking == 'percent' else ('Vol. (USD B)' if metric == 'volume_usd' else 'Trades')
        fig.update_yaxes(title=y_title, row=1, col=1)
    
    else:
        # --- SINGLE CHART MODE (no subplots) ---
        fig = go.Figure()
        
        # Determine what to iterate over
        cryptos_available = sorted(df['base_asset'].unique())
        
        # Group data
        grouped = df.groupby(['month', 'base_asset'])[metric].sum().reset_index()
        
        # Compute totals for percent stacking
        if stacking == 'percent':
            totals = grouped.groupby('month')[metric].sum().reset_index()
            totals.columns = ['month', '_total']
        
        for crypto in cryptos_available:
            crypto_data = grouped[grouped['base_asset'] == crypto].sort_values('month')
            
            if crypto_data.empty:
                continue
            
            if stacking == 'percent':
                crypto_data = crypto_data.merge(totals, on='month')
                y_vals = crypto_data[metric] / crypto_data['_total'] * 100
            else:
                y_vals = crypto_data[metric] / 1e9 if metric == 'volume_usd' else crypto_data[metric]
            
            color = ALL_COLORS.get(crypto, ALL_COLORS.get(crypto.lower(), '#999'))
            name = crypto.upper() if crypto not in FSB_COLORS else crypto
            
            if chart_type == 'bar':
                fig.add_trace(go.Bar(x=crypto_data['month'], y=y_vals, name=name, marker_color=color))
            else:
                fig.add_trace(go.Scatter(x=crypto_data['month'], y=y_vals, name=name,
                                        line=dict(color=color), mode='lines'))
        
        y_title = 'Share (%)' if stacking == 'percent' else ('Volume (USD B)' if metric == 'volume_usd' else 'Trades')
        y_range = [0, 100] if stacking == 'percent' else None
        fig.update_layout(barmode='stack' if chart_type == 'bar' else None)
        fig.update_yaxes(title=y_title, range=y_range)
    
    # Common layout - World Bank style
    fig.update_layout(
        height=380,
        margin=dict(l=50, r=30, t=30, b=50),
        paper_bgcolor=WB['surface'],
        plot_bgcolor=WB['surface'],
        legend=dict(
            orientation='h', 
            yanchor='bottom', 
            y=-0.2, 
            xanchor='center', 
            x=0.5,
            font=dict(size=12, color=WB['text_muted']),
            bgcolor='rgba(0,0,0,0)',
        ),
        font=dict(family=FONT, size=12, color=WB['text']),
        hoverlabel=dict(
            bgcolor=WB['surface'],
            font_size=12,
            font_family=FONT,
            bordercolor=WB['border'],
        ),
    )
    # Clean axes - World Bank style
    fig.update_xaxes(
        tickformat='%Y', 
        dtick='M12', 
        showgrid=False,
        linecolor=WB['border'],
        tickfont=dict(size=11, color=WB['text_muted']),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(0,0,0,0.06)',
        gridwidth=1,
        linecolor=WB['border'],
        tickfont=dict(size=11, color=WB['text_muted']),
        title_font=dict(size=12, color=WB['text_muted']),
    )
    
    return fig


@app.callback(
    Output('analysis-rows', 'children'),
    [Input('main-chart', 'figure'),
     Input('fiat-selector', 'value'),
     Input('crypto-selector', 'value'),
     Input('metric-selector', 'value'),
     Input('date-slider', 'value')]
)
def update_analysis_panel(figure, fiats, cryptos, metric, date_range):
    """Generate dynamic analysis table based on current data."""
    df = _data.copy()
    
    # Filter by date
    start_date = _index_to_date(date_range[0])
    end_date = _index_to_date(date_range[1])
    df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    
    rows = []
    row_style = {'display': 'flex', 'padding': '10px 12px', 'borderBottom': '1px solid #d5d8dc',
                 'fontSize': '13px', 'alignItems': 'center'}
    
    def format_pct(val):
        if val is None or pd.isna(val):
            return "—"
        color = '#27ae60' if val >= 0 else '#e74c3c'
        return html.Span(f"{val:+.1f}%", style={'color': color})
    
    def format_level(val, metric):
        if val is None or pd.isna(val):
            return "—"
        if metric == 'volume_usd':
            if val >= 1e9:
                return f"{val/1e9:.1f}B"
            elif val >= 1e6:
                return f"{val/1e6:.1f}M"
            else:
                return f"{val/1e3:.0f}K"
        else:
            if val >= 1e6:
                return f"{val/1e6:.1f}M"
            elif val >= 1e3:
                return f"{val/1e3:.0f}K"
            return f"{val:.0f}"
    
    # Determine what to show based on selections
    show_crypto_comparison = cryptos and 'SPECIAL:STABLE_VS_UNBACKED' in cryptos
    show_region_comparison = fiats and 'SPECIAL:AE_VS_EMDE' in fiats
    
    metric_col = 'volume_usd' if metric == 'volume_usd' else 'number_of_trades'
    
    try:
        # Get latest month data
        latest_month = df['month'].max()
        prev_month = latest_month - pd.DateOffset(months=1)
        year_ago = latest_month - pd.DateOffset(months=12)
        
        if show_crypto_comparison:
            # Stablecoins vs Unbacked
            for crypto_type in ['Stablecoins', 'Unbacked']:
                if crypto_type == 'Stablecoins':
                    type_df = df[df['base_asset'].isin(STABLECOINS)]
                else:
                    type_df = df[~df['base_asset'].isin(STABLECOINS)]
                
                current = type_df[type_df['month'] == latest_month][metric_col].sum()
                prev = type_df[type_df['month'] == prev_month][metric_col].sum()
                year = type_df[type_df['month'] == year_ago][metric_col].sum()
                
                mom = ((current / prev) - 1) * 100 if prev > 0 else None
                yoy = ((current / year) - 1) * 100 if year > 0 else None
                
                rows.append(html.Div(style=row_style, children=[
                    html.Div(crypto_type, style={'flex': '2', 'fontWeight': '500', 'color': '#333'}),
                    html.Div(format_level(current, metric), style={'flex': '1', 'textAlign': 'right', 'color': '#666'}),
                    html.Div(format_pct(mom), style={'flex': '1', 'textAlign': 'right'}),
                    html.Div(format_pct(yoy), style={'flex': '1', 'textAlign': 'right'}),
                ]))
        
        if show_region_comparison:
            # AEs vs EMDEs
            for region in ['AEs', 'EMDEs']:
                region_df = df[df['region'] == region]
                
                current = region_df[region_df['month'] == latest_month][metric_col].sum()
                prev = region_df[region_df['month'] == prev_month][metric_col].sum()
                year = region_df[region_df['month'] == year_ago][metric_col].sum()
                
                mom = ((current / prev) - 1) * 100 if prev > 0 else None
                yoy = ((current / year) - 1) * 100 if year > 0 else None
                
                rows.append(html.Div(style=row_style, children=[
                    html.Div(region, style={'flex': '2', 'fontWeight': '500', 'color': '#333'}),
                    html.Div(format_level(current, metric), style={'flex': '1', 'textAlign': 'right', 'color': '#666'}),
                    html.Div(format_pct(mom), style={'flex': '1', 'textAlign': 'right'}),
                    html.Div(format_pct(yoy), style={'flex': '1', 'textAlign': 'right'}),
                ]))
        
        # Total row
        current_total = df[df['month'] == latest_month][metric_col].sum()
        prev_total = df[df['month'] == prev_month][metric_col].sum()
        year_total = df[df['month'] == year_ago][metric_col].sum()
        
        mom_total = ((current_total / prev_total) - 1) * 100 if prev_total > 0 else None
        yoy_total = ((current_total / year_total) - 1) * 100 if year_total > 0 else None
        
        rows.append(html.Div(style={**row_style, 'backgroundColor': '#dfe2e6'}, children=[
            html.Div("Total", style={'flex': '2', 'fontWeight': '600', 'color': '#333'}),
            html.Div(format_level(current_total, metric), style={'flex': '1', 'textAlign': 'right', 'color': '#333', 'fontWeight': '600'}),
            html.Div(format_pct(mom_total), style={'flex': '1', 'textAlign': 'right'}),
            html.Div(format_pct(yoy_total), style={'flex': '1', 'textAlign': 'right'}),
        ]))
        
    except Exception as e:
        rows.append(html.Div(f"Error: {str(e)}", style={'padding': '10px', 'color': '#999'}))
    
    return rows


def log_download_to_github(name, institution, email, timestamp):
    """Append a download record to downloads.log in the GitHub repo."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("[WARNING] GITHUB_TOKEN not set, skipping GitHub log")
        return
    
    repo = 'emigiupponi/asymmetric-cryptoization'
    path = 'downloads.log'
    api_url = f'https://api.github.com/repos/{repo}/contents/{path}'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    
    new_line = f"{timestamp} | {name} | {institution} | {email}\n"
    
    try:
        r = requests.get(api_url, headers=headers)
        if r.status_code == 200:
            file_data = r.json()
            existing = base64.b64decode(file_data['content']).decode('utf-8')
            sha = file_data['sha']
        else:
            existing = "timestamp | name | institution | email\n"
            sha = None
        
        updated = existing + new_line
        encoded = base64.b64encode(updated.encode('utf-8')).decode('utf-8')
        
        payload = {'message': f'[log] Download by {name} ({institution})', 'content': encoded}
        if sha:
            payload['sha'] = sha
        
        requests.put(api_url, headers=headers, json=payload)
        print(f"[GITHUB LOG] Saved to {path}")
    except Exception as e:
        print(f"[GITHUB LOG ERROR] {e}")


# ============ DOWNLOAD CALLBACKS ============

@app.callback(
    Output('download-modal', 'style'),
    [Input('btn-open-download', 'n_clicks'),
     Input('btn-cancel-download', 'n_clicks'),
     Input('btn-confirm-download', 'n_clicks')],
    [State('download-modal', 'style'),
     State('download-name', 'value'),
     State('download-institution', 'value'),
     State('download-email', 'value')],
    prevent_initial_call=True
)
def toggle_download_modal(open_clicks, cancel_clicks, confirm_clicks, current_style, name, institution, email):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_style
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == 'btn-open-download':
        return {**current_style, 'display': 'flex'}
    elif trigger == 'btn-cancel-download':
        return {**current_style, 'display': 'none'}
    elif trigger == 'btn-confirm-download':
        if name and institution and email:
            return {**current_style, 'display': 'none'}
    return current_style


@app.callback(
    [Output('download-data', 'data'),
     Output('download-validation', 'children')],
    Input('btn-confirm-download', 'n_clicks'),
    [State('download-name', 'value'),
     State('download-institution', 'value'),
     State('download-email', 'value'),
     State('exchange-selector', 'value'),
     State('fiat-selector', 'value'),
     State('crypto-selector', 'value'),
     State('date-slider', 'value')],
    prevent_initial_call=True
)
def process_download(n_clicks, name, institution, email, exchanges, fiats, cryptos, date_range):
    if not name or not institution or not email:
        return dash.no_update, "Please fill in all fields."
    
    # Log the download to Render logs and GitHub
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"[DOWNLOAD] {name} | {institution} | {email} | {timestamp}")
    log_download_to_github(name, institution, email, timestamp)
    
    # Prepare filtered data
    df = _data.copy()
    
    start_date = _index_to_date(date_range[0])
    end_date = _index_to_date(date_range[1])
    df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    
    # Apply filters
    clean_exchanges = [e for e in (exchanges or []) if not e.startswith('EXCL:') and not e.startswith('SEP')]
    if clean_exchanges and 'all' not in clean_exchanges:
        df = df[df['exchange'].isin(clean_exchanges)]
    
    clean_fiats = [f for f in (fiats or []) if not f.startswith('SPECIAL:') and not f.startswith('SEP') and not f.startswith('EXCL:')]
    special_fiats = [f for f in (fiats or []) if f.startswith('SPECIAL:')]
    if 'SPECIAL:AE' in special_fiats:
        df = df[df['region'] == 'AEs']
    elif 'SPECIAL:EMDE' in special_fiats:
        df = df[df['region'] == 'EMDEs']
    elif clean_fiats:
        df = df[df['quote_asset'].isin(clean_fiats)]
    
    clean_cryptos = [c for c in (cryptos or []) if not c.startswith('SPECIAL:') and not c.startswith('SEP') and not c.startswith('EXCL:')]
    special_cryptos = [c for c in (cryptos or []) if c.startswith('SPECIAL:')]
    if 'SPECIAL:STABLECOINS' in special_cryptos:
        df = df[df['crypto_type'] == 'Stablecoins']
    elif 'SPECIAL:UNBACKED' in special_cryptos:
        df = df[df['crypto_type'] == 'Unbacked']
    elif clean_cryptos:
        df = df[df['base_asset'].isin(clean_cryptos)]
    
    # Select columns for export
    export_cols = ['month', 'exchange', 'base_asset', 'quote_asset', 'region', 'crypto_type', 'volume_usd', 'number_of_trades']
    export_df = df[[c for c in export_cols if c in df.columns]]
    
    return dcc.send_data_frame(export_df.to_csv, "asymmetric_cryptoization_data.csv", index=False), ""


# ============ RUN ============

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8051)))
