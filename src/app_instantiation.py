# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 11:20:08 2021

@author: Joseph.Moyes

File information: 
    imported by index.py, which then modifies the instantiation of the Dash app.
"""

import dash
import dash_bootstrap_components as dbc

# dbc.themes.BOOTSTRAP: url to the css file provided by dash-bootstrap-components
# The BOOTSTRAP theme of dbc is similar to the default 'bootstrap' theme used by Dash, but it
# is tweaked.
# Theme explorer: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])