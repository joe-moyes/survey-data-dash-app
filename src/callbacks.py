# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 11:20:08 2021

@author: Joseph.Moyes

File information:
    imported by index.py, which runs the below callback function definitions.
"""

import dash
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash.dash import no_update

import pandas as pd
import regex as re

from layout import *
import agg_functions

import json # this is after realising the economical benefit of storing the boolean mask (list object) - instead of the data (dataframe) - in dcc.Store


####################### Menu: section headers collapse open/close #######################

# each menu child is a dbc.Card (see make_section_block return)
# within each dbc.Card, we access the 2nd child's id (dbc.Collapse)
collapse_ids = [child.children[1].id for child in menu.children]

# dbc.Card > 1st child (dbc.CardHeader) > dbc.Button.id
# note that when 'children' is singular it is NOT a list
header_ids = [child.children[0].children.id for child in menu.children]


@app.callback(
    [Output(collapse_id, "is_open") for collapse_id in collapse_ids],
    [Input(header_id, "n_clicks") for header_id in header_ids],
    [State(collapse_id, "is_open") for collapse_id in collapse_ids]
)
def on_sidebar_header(*args):
    ctx = dash.callback_context
    
    if ctx.triggered:
        
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # corresponding collapse id 
        collapse_id = re.sub("header", "collapse", trigger_id)
        
        # inverse the is_open state of corresponding collapse_id
        ctx.states[collapse_id + ".is_open"] = not ctx.states[collapse_id + ".is_open"]
        
    # return states
    # note callbacks run on launch thus states need returned regardless of triggering
    return tuple(state for state in ctx.states.values())


####################### Menu items: selected question populates search bar #######################

# OUTER LOOP: iterates over each card (menu section)
# html.Div > dbc.Card
# INNER LOOP: accesses each ListGroupItem (stored in a list as the child of ListGroup)
# dbc.Card > 2nd child (dbc.Collapse) > dbc.CardBody > dbc.ListGroup > list of ListGroupItems
# RETURN VALUE: ListGroupItem > Button.id
question_ids = [item.children.id for child in menu.children
                for item in child.children[1].children.children.children
                ]

@app.callback(
    [Output('question search', "value")],
    [Input(question_id, "n_clicks") for question_id in question_ids],
    [State('question search', "value")]
)
def on_sidebar_question(*args):
    ctx = dash.callback_context
    
    if ctx.triggered:
        
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # we can reference any component in the layout by its id
        # the component is the button pressed and its child is...
        # ...the text of that button (the question)
        return [layout[trigger_id].children] # for some reason, value must be a list
     
    else:
        # keep searchbar clear if not triggered (i.e. on launch)
        return no_update


####################### Market filter: edit market dropdown options #######################

# NOTE: this caused me some anguish before realising...
# if you want to return each item in a container to a seperate output:
    # wrap the seperate outputs in a list
# if you want to return a whole container to a sinlge output:
    # do NOT wrap seperate outputs in a list

@app.callback(
    Output('market-A', "options"), # outputs are NOT wrapped in square brackets (see above)
    Output('market-A', "value"),
    Output('market-B', "options"),
    Output('market-B', "value"),
    [Input('toggle-markets-A', "value"), Input('toggle-markets-B', "value")]
)
def on_market_options(selected_A, selected_B):
    
    # Audience A:
    # selected_A is updated to None by on_age_range callback if user drags age range to custom range
    # in that event, returning no_update prevents KeyError
    options_A = [{'label': market, 'value' : market}
                   for market in data.market_regions[selected_A]] if selected_A else no_update
    values_A = [market for market in data.market_regions[selected_A]] if selected_A else no_update
    
    # Audience B:
    # selected_B is updated to None by on_age_range callback if user drags age range to custom range
    # in that event, returning no_update prevents KeyError
    options_B = [{'label': market, 'value' : market}
                   for market in data.market_regions[selected_B]] if selected_B else no_update
    values_B = [market for market in data.market_regions[selected_B]] if selected_B else no_update
    
    
    ctx = dash.callback_context

    # note: this callback is triggered on launch by on_market_list, which assigns
    # the value "All" to both audience sets. This means, on launch, ctx.triggered
    # is of length-2. 
    if len(ctx.triggered) == 2:
        return options_A, values_A, options_B, values_B
    
    else:        
        # else determine which audience version was changed:
        # note: only the audience version that changed is updated
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "toggle-markets-A":
            return options_A, values_A, no_update, no_update
        elif trigger_id == "toggle-markets-B":
            return no_update, no_update, options_B, values_B


####################### Gender filter: edit gender dropdown options #######################

@app.callback(
    Output('gender-A', "options"), # outputs are NOT wrapped in square brackets (see above)
    Output('gender-A', "value"),
    Output('gender-B', "options"),
    Output('gender-B', "value"),
    [Input('toggle-genders-A', "value"), Input('toggle-genders-B', "value")]
)
def on_gender_options(selected_A, selected_B):
    
    # Audience A:
    # selected_A is updated to None by on_age_range callback if user drags age range to custom range
    # in that event, returning no_update prevents KeyError
    options_A = [{'label': gender, 'value' : gender}
                   for gender in data.gender_groups[selected_A]] if selected_A else no_update
    values_A = [gender for gender in data.gender_groups[selected_A]] if selected_A else no_update
    
    # Audience B:
    # selected_B is updated to None by on_age_range callback if user drags age range to custom range
    # in that event, returning no_update prevents KeyError
    options_B = [{'label': gender, 'value' : gender}
                   for gender in data.gender_groups[selected_B]] if selected_B else no_update
    values_B = [gender for gender in data.gender_groups[selected_B]] if selected_B else no_update
    
    
    ctx = dash.callback_context
        
    # note: this callback is triggered on launch by on_gender_list, which assigns
    # the value "All" to both audience sets. This means, on launch, ctx.triggered
    # is of length-2. 
    if len(ctx.triggered) == 2:
        return options_A, values_A, options_B, values_B

    else:
        # else determine which audience version was changed:
        # note: only the audience version that changed is updated
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "toggle-genders-A":
            return options_A, values_A, no_update, no_update
        elif trigger_id == "toggle-genders-B":
            return no_update, no_update, options_B, values_B


####################### Age filter: edit selected age range #######################

@app.callback(
    Output('age-A', "value"),
    Output('age-B', "value"),
    Input('toggle-ages-A', "value"),
    Input('toggle-ages-B', "value")
)
def on_age_options(selected_A, selected_B):

    
    # Audience A:
    # selected_A is updated to None by on_age_range callback if user drags age range to custom range
    # in that event, returning no_update prevents KeyError
    value_A = data.age_groups[selected_A] if selected_A else no_update
    
    # Audience B:
    # selected_B is updated to None by on_age_range callback if user drags age range to custom range
    # in that event, returning no_update prevents KeyError
    value_B = data.age_groups[selected_B] if selected_B else no_update
    
    
    ctx = dash.callback_context
    
    # note: this callback is triggered on launch by on_age_range, which assigns
    # the value "All" to both audience sets. This means, on launch, ctx.triggered
    # is of length-2. 
    if len(ctx.triggered) == 2:
        return value_A, value_B

    else:
        # else determine which audience version was changed:
        # note: only the audience version that changed is updated
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "toggle-ages-A":
            return value_A, no_update
        elif trigger_id == "toggle-ages-B":
            return no_update, value_B


####################### Income filter: edit selected income range #######################

@app.callback(
    Output('income-A', "value"),
    Output('income-B', "value"),
    Input('toggle-incomes-A', "value"),
    Input('toggle-incomes-B', "value")
)
def on_income_options(selected_A, selected_B):
                
    # Audience A:
    # selected_A is updated to None by on_income_range callback if user drags income range to custom range
    # in that event, returning no_update prevents KeyError
    value_A = data.income_groups[selected_A] if selected_A else no_update
    
    # Audience B:
    # selected_B is updated to None by on_income_range callback if user drags income range to custom range
    # in that event, returning no_update prevents KeyError
    value_B = data.income_groups[selected_B] if selected_B else no_update
    
    
    ctx = dash.callback_context
    
    # note: this callback is triggered on launch by on_income_range, which assigns
    # the value "All" to both audience sets. This means, on launch, ctx.triggered
    # is of length-2. 
    if len(ctx.triggered) == 2:
        return value_A, value_B

    else: 
        # else determine which audience version was changed:
        # note: only the audience version that changed is updated
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "toggle-incomes-A":
            return value_A, no_update
        elif trigger_id == "toggle-incomes-B":
            return no_update, value_B


####################### Travel filter: edit selected travel range #######################

@app.callback(
    Output('travel-A', "value"),
    Output('travel-B', "value"),
    Input('toggle-travels-A', "value"),
    Input('toggle-travels-B', "value")
)
def on_travel_options(selected_A, selected_B):        
    
    # Audience A:
    # selected_A is updated to None by on_travel_range callback if user drags travel range to custom range
    # in that event, returning no_update prevents KeyError
    value_A = data.travel_groups[selected_A] if selected_A else no_update
    
    # Audience B:
    # selected_B is updated to None by on_travel_range callback if user drags travel range to custom range
    # in that event, returning no_update prevents KeyError
    value_B = data.travel_groups[selected_B] if selected_B else no_update
    
    
    ctx = dash.callback_context
    
    # note: this callback is triggered on launch by on_income_range, which assigns
    # the value "All" to both audience sets. This means, on launch, ctx.triggered
    # is of length-2. 
    if len(ctx.triggered) == 2:
        return value_A, value_B

    else:
        # else determine which audience version was changed:
        # note: only the audience version that changed is updated
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id == "toggle-travels-A":
            return value_A, no_update
        elif trigger_id == "toggle-travels-B":
            return no_update, value_B


####################### Market filter (2): adjust market option when market list is changed #######################

# note: there is a circular reference between on_market_option and on_market_list.
# This is because each fires the other. However, there is NO infinite loop.
# This is because on_market_list only updates market option if output is NOT equal to existing state.
# see below else code in try : except : else block. In actual fact, the else code is not strictly 
# needed because the output would result in an unchanged market option value (but it is written for
# the sake of logical clarity).

@app.callback(
    Output('toggle-markets-A', "value"),
    Output('toggle-markets-B', "value"),
    Input('market-A', "value"),
    Input('market-B', "value"),
    State('toggle-markets-A', "value"),
    State('toggle-markets-B', "value")
)
def on_market_list(list_A, list_B, selected_A, selected_B):
    # useful resource: https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
    
    ctx = dash.callback_context 
    
    # if initial launch:
    if not ctx.triggered:
    # for some reason, when testing, this was the print out of ctx.triggered before this line:
    # [{'prop_id': '.', 'value': None}]
    # bit confusing why this line thus runs on launch. but it does. possibly something to do with circular reference warning.
        return "All", "All"

    # else determine which audience version was changed:
    # note: only the audience version that changed is updated
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "market-A":
            # Audience A:
            try:
                # it is ESSENTIAL to ensure the list is ordered before comparing
                if list_A: list_A = sorted(list_A) 
                
                # if the changed list corresponds to an market option, select that market option
                select_A = list(data.market_regions.keys())[list(data.market_regions.values()).index(list_A)]
            except ValueError:
                # if the changed list does not correspond to an market option, no market option is selected
                select_A = None
            else:
                # if the changed list does correspond to an market option, only update if market option is not already selected
                select_A = no_update if select_A == selected_A else select_A
                
            return select_A, no_update
        
        elif trigger_id == "market-B":
            # Audience B:
            try:
                # it is ESSENTIAL to ensure the list is ordered before comparing
                if list_B: list_B = sorted(list_B) 
                
                # if the changed list corresponds to an market option, select that market option
                select_B = list(data.market_regions.keys())[list(data.market_regions.values()).index(list_B)]
            except ValueError:
                # if the changed list does not correspond to an market option, no market option is selected
                select_B = None
            else:
                # if the changed list does correspond to an market option, only update if market option is not already selected
                select_B = no_update if select_B == selected_B else select_B
                
            return no_update, select_B


####################### Gender filter (2): adjust gender option when gender list is changed #######################

# note: there is a circular reference between on_gender_option and on_gender_list.
# This is because each fires the other. However, there is NO infinite loop.
# This is because on_gender_list only updates gender option if output is NOT equal to existing state.
# see below else code in try : except : else block. In actual fact, the else code is not strictly 
# needed because the output would result in an unchanged gender option value (but it is written for
# the sake of logical clarity).

@app.callback(
    Output('toggle-genders-A', "value"),
    Output('toggle-genders-B', "value"),
    Input('gender-A', "value"),
    Input('gender-B', "value"),
    State('toggle-genders-A', "value"),
    State('toggle-genders-B', "value")
)
def on_gender_list(list_A, list_B, selected_A, selected_B):
    # useful resource: https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
    
    ctx = dash.callback_context
            
    # if initial launch:
    if not ctx.triggered:
    # for some reason, when testing, this was the print out of ctx.triggered before this line:
    # [{'prop_id': '.', 'value': None}]
    # bit confusing why this line thus runs on launch. but it does. possibly something to do with circular reference warning.
        return "All", "All"

    # else determine which audience version was changed:
    # note: only the audience version that changed is updated
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "gender-A":
            # Audience A:
            try:
                # it is ESSENTIAL to ensure the list is ordered before comparing
                # this also means "Prefer not to answer" goes last
                if list_A: 
                    list_A = sorted(list_A)
                    if "Prefer not to answer" in list_A: list_A.append(list_A.pop(list_A.index("Prefer not to answer")))
                
                # if the changed list corresponds to an gender option, select that gender option
                select_A = list(data.gender_groups.keys())[list(data.gender_groups.values()).index(list_A)]
            except ValueError:
                # if the changed list does not correspond to an gender option, no gender option is selected
                select_A = None
            else:
                # if the changed list does correspond to an gender option, only update if gender option is not already selected
                select_A = no_update if select_A == selected_A else select_A
                
            return select_A, no_update
        
        elif trigger_id == "gender-B":
            # Audience B:
            try:
                # it is ESSENTIAL to ensure the list is ordered before comparing
                # this also means "Prefer not to answer" goes last
                if list_B: 
                    list_B = sorted(list_B)
                    if "Prefer not to answer" in list_B: list_B.append(list_B.pop(list_B.index("Prefer not to answer")))
                
                # if the changed list corresponds to an gender option, select that gender option
                select_B = list(data.gender_groups.keys())[list(data.gender_groups.values()).index(list_B)]
            except ValueError:
                # if the changed list does not correspond to an gender option, no gender option is selected
                select_B = None
            else:
                # if the changed list does correspond to an gender option, only update if gender option is not already selected
                select_B = no_update if select_B == selected_B else select_B
                
            return no_update, select_B


####################### Age filter (2): adjust age option when age range is changed #######################

# note: there is a circular reference between on_age_option and on_age_range.
# This is because each fires the other. However, there is NO infinite loop.
# This is because on_age_range only updates age option if output is NOT equal to existing state.
# see below else code in try : except : else block. In actual fact, the else code is not strictly 
# needed because the output would result in an unchanged age option value (but it is written for
# the sake of logical clarity).

@app.callback(
    Output('toggle-ages-A', "value"),
    Output('toggle-ages-B', "value"),
    Input('age-A', "value"),
    Input('age-B', "value"),
    State('toggle-ages-A', "value"),
    State('toggle-ages-B', "value")
)
def on_age_range(range_A, range_B, selected_A, selected_B):
    # useful resource: https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
    
    ctx = dash.callback_context
           
    # if initial launch:
    if not ctx.triggered:
    # for some reason, when testing, this was the print out of ctx.triggered before this line:
    # [{'prop_id': '.', 'value': None}]
    # bit confusing why this line thus runs on launch. but it does. possibly something to do with circular reference warning.
        return "All", "All"

    # else determine which audience version was changed:
    # note: only the audience version that changed is updated
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "age-A":
            # Audience A:
            try:
                # if the changed range corresponds to an age option, select that age option
                select_A = list(data.age_groups.keys())[list(data.age_groups.values()).index(range_A)]
            except ValueError:
                # if the changed range does not correspond to an age option, no age option is selected
                select_A = None
            else:
                # if the changed range does correspond to an age option, only update if age option is not already selected
                select_A = no_update if select_A == selected_A else select_A
                
            return select_A, no_update
        
        elif trigger_id == "age-B":
            # Audience B:
            try:
                # if the changed range corresponds to an age option, select that age option
                select_B = list(data.age_groups.keys())[list(data.age_groups.values()).index(range_B)]
            except ValueError:
                # if the changed range does not correspond to an age option, no age option is selected
                select_B = None
            else:
                # if the changed range does correspond to an age option, only update if age option is not already selected
                select_B = no_update if select_B == selected_B else select_B
                
            return no_update, select_B


####################### Income filter (2): adjust income option when income range is changed #######################

# note: there is a circular reference between on_income_option and on_income_range.
# This is because each fires the other. However, there is NO infinite loop.
# This is because on_income_range only updates income option if output is NOT equal to existing state.
# see below else code in try : except : else block. In actual fact, the else code is not strictly 
# needed because the output would result in an unchanged income option value (but it is written for
# the sake of logical clarity).

@app.callback(
    Output('toggle-incomes-A', "value"),
    Output('toggle-incomes-B', "value"),
    Input('income-A', "value"),
    Input('income-B', "value"),
    State('toggle-incomes-A', "value"),
    State('toggle-incomes-B', "value")
)
def on_income_range(range_A, range_B, selected_A, selected_B):
    # useful resource: https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
    
    ctx = dash.callback_context
        
    # if initial launch:
    if not ctx.triggered:
    # for some reason, when testing, this was the print out of ctx.triggered before this line:
    # [{'prop_id': '.', 'value': None}]
    # bit confusing why this line thus runs on launch. but it does. possibly something to do with circular reference warning.
        return "All", "All"

    # else determine which audience version was changed:
    # note: only the audience version that changed is updated
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "income-A":
            # Audience A:
            try:
                # if the changed range corresponds to an income option, select that income option
                select_A = list(data.income_groups.keys())[list(data.income_groups.values()).index(range_A)]
            except ValueError:
                # if the changed range does not correspond to an income option, no income option is selected
                select_A = None
            else:
                # if the changed range does correspond to an income option, only update if income option is not already selected
                select_A = no_update if select_A == selected_A else select_A
                
            return select_A, no_update
        
        elif trigger_id == "income-B":
            # Audience B:
            try:
                # if the changed range corresponds to an income option, select that income option
                select_B = list(data.income_groups.keys())[list(data.income_groups.values()).index(range_B)]
            except ValueError:
                # if the changed range does not correspond to an income option, no income option is selected
                select_B = None
            else:
                # if the changed range does correspond to an income option, only update if income option is not already selected
                select_B = no_update if select_B == selected_B else select_B
                
            return no_update, select_B


####################### Travel filter (2): adjust travel option when travel range is changed #######################

# note: there is a circular reference between on_travel_option and on_travel_range.
# This is because each fires the other. However, there is NO infinite loop.
# This is because on_travel_range only updates travel option if output is NOT equal to existing state.
# see below else code in try : except : else block. In actual fact, the else code is not strictly 
# needed because the output would result in an unchanged travel option value (but it is written for
# the sake of logical clarity).

@app.callback(
    Output('toggle-travels-A', "value"),
    Output('toggle-travels-B', "value"),
    Input('travel-A', "value"),
    Input('travel-B', "value"),
    State('toggle-travels-A', "value"),
    State('toggle-travels-B', "value")
)
def on_travel_range(range_A, range_B, selected_A, selected_B):
    # useful resource: https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
    
    ctx = dash.callback_context
        
    # if initial launch:
    if not ctx.triggered:
    # for some reason, when testing, this was the print out of ctx.triggered before this line:
    # [{'prop_id': '.', 'value': None}]
    # bit confusing why this line thus runs on launch. but it does. possibly something to do with circular reference warning.
        return "All", "All"

    # else determine which audience version was changed:
    # note: only the audience version that changed is updated
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "travel-A":
            # Audience A:
            try:
                # if the changed range corresponds to an travel option, select that travel option
                select_A = list(data.travel_groups.keys())[list(data.travel_groups.values()).index(range_A)]
            except ValueError:
                # if the changed range does not correspond to an travel option, no travel option is selected
                select_A = None
            else:
                # if the changed range does correspond to an travel option, only update if travel option is not already selected
                select_A = no_update if select_A == selected_A else select_A
                
            return select_A, no_update
        
        elif trigger_id == "travel-B":
            # Audience B:
            try:
                # if the changed range corresponds to an travel option, select that travel option
                select_B = list(data.travel_groups.keys())[list(data.travel_groups.values()).index(range_B)]
            except ValueError:
                # if the changed range does not correspond to an travel option, no travel option is selected
                select_B = None
            else:
                # if the changed range does correspond to an travel option, only update if travel option is not already selected
                select_B = no_update if select_B == selected_B else select_B
                
            return no_update, select_B


####################### Travel filter (3): control traveller purpose/domain buttons #######################

travel_categories = ["All-type-", "purpose-type-", "domain-type-"]

@app.callback(
    [Output("{}A".format(category), "value") for category in travel_categories] +
    [Output("{}B".format(category), "value") for category in travel_categories],
    
    [Input("{}A".format(category), "value") for category in travel_categories] +
    [Input("{}B".format(category), "value") for category in travel_categories],
    
    [State("{}A".format(category), "value") for category in travel_categories] +
    [State("{}B".format(category), "value") for category in travel_categories],
)
def on_travel_type_options(*args):
    ctx = dash.callback_context
  
    if ctx.triggered:
 
        A_states = list(ctx.states.values())[:3]
        B_states = list(ctx.states.values())[3:]        
               
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # check if trigger is from A or B
        
        if trigger_id[-1] == "A":
            # if "All travellers" selected, deactivate others
            if trigger_id == "All-type-A":
                A_states = [A_states[0], None, None]
            # if purpose or domain selected, deactivate "All travellers"
            else:
                A_states = [None, A_states[1], A_states[2]]
                
            return A_states + [no_update]*3
                
        elif trigger_id[-1] == "B":
            # if "All travellers" selected, deactivate others
            if trigger_id == "All-type-B":
                B_states = [B_states[0], None, None]
            # if purpose or domain selected, deactivate "All travellers"
            else:
                B_states = [None, B_states[1], B_states[2]]
               
            return [no_update]*3 + B_states
    
    else:
        return [no_update]*6


####################### Filter by a behaviour: populate custom_selected_item options #######################

@app.callback(
    [Output("custom_selected_item-{}".format(version), "options") for version in ["A", "B"]] +
    [Output("custom_selected_item-{}".format(version), "value") for version in ["A", "B"]],
    
    [Input("custom_selected_question-{}".format(version), "value") for version in ["A", "B"]]
)
def on_custom_selected_question(*args):
    ctx = dash.callback_context
  
    if ctx.triggered:      
               
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        question = ctx.triggered[0]["value"]
        
        # check if trigger is from A or B
         
        if trigger_id[-1] == "A":
            # if a question is selected
            if question:
                options = [{'label' : question_item, 'value' : question_item}
                           for question_item in data.question_items_values_dict[question]]
                value = list(data.question_items_values_dict[question]) # this is helpful for the user: default is to return all values so they do not have to repetitively add multiple values 
            
            # if no question selected
            else:
                options = []
                value = None
            
            return options, no_update, value, no_update
                
        elif trigger_id[-1] == "B":
            # if a question is selected
            if question:
                options = [{'label' : question_item, 'value' : question_item}
                           for question_item in data.question_items_values_dict[question]]
                value = list(data.question_items_values_dict[question]) # this is helpful for the user: default is to return all values so they do not have to repetitively add multiple values 

            # if no question selected
            else:
                options = []
                value = None
            
            return no_update, options, no_update, value
    
    else:
        return tuple([no_update]*4)


####################### Filter by a behaviour: populate custom_selected_response options #######################

@app.callback(
    [Output("custom_selected_response-{}".format(version), "options") for version in ["A", "B"]] +
    [Output("custom_selected_response-{}".format(version), "value") for version in ["A", "B"]],   
    
    [Input("custom_selected_item-{}".format(version), "value") for version in ["A", "B"]],
    
    [State("custom_selected_question-{}".format(version), "value") for version in ["A", "B"]]
)
def on_custom_selected_item(*args):
    ctx = dash.callback_context
  
    if ctx.triggered:      
               
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        question_items = ctx.triggered[0]["value"]
        
        # check if trigger is from A or B
         
        if trigger_id[-1] == "A":
            # if a question_item(s) is selected
            # note: question_items is a list 
            if question_items:
                question = list(ctx.states.values())[0]

                # how this works:
                    # the middle portion generates a list of lists (each list contains the response values for a question item)
                    # we iterate over this list of lists and return each value from each list
                    # dict.fromkeys removes duplicates (different question items will usually have the same response values) \
                        # it is an alternative to set() and retains the order! https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
                response_values = list(dict.fromkeys([value for values_list in 
                                                      [data.question_items_values_dict[question][question_item] for question_item in question_items]
                                                      for value in values_list]))
                
                # if response_values are all integers, we want an overall order applied:
                if all([isinstance(x, int) for x in response_values]):
                    response_values = sorted(response_values)
                    
                options = [{'label' : response_value, 'value' : response_value}
                           for response_value in response_values]
                value = response_values # this is helpful for the user: default is to return all values so they do not have to repetitively add multiple values 
                
            # if no question selected
            else:
                options = []
                value = None
            
            return options, no_update, value, no_update
                
        elif trigger_id[-1] == "B":
            # if a question_item(s) is selected
            # note: question_items is a list
            if question_items:
                question = list(ctx.states.values())[1]
                
                # how this works:
                    # the middle portion generates a list of lists (each list contains the response values for a question)
                    # we iterate over this list of lists and return each value from each list
                    # set removes duplicates (different question items will usually have the same response values)
                response_values = list(dict.fromkeys([value for values_list in 
                                                      [data.question_items_values_dict[question][question_item] for question_item in question_items]
                                                      for value in values_list]))

                # if response values are all integers, we want an overall order applied:
                if all([isinstance(x, int) for x in response_values]):
                    response_values = sorted(response_values)

                options = [{'label' : response_value, 'value' : response_value}
                           for response_value in response_values]
                value = response_values # this is helpful for the user: default is to return all values so they do not have to repetitively add multiple values

            # if no question selected
            else:
                options = []
                value = None
            
            return no_update, options, no_update, value
    
    else:
        return tuple([no_update]*4)



####################### filter menus: expand/collapse menu A and B #######################

@app.callback(
    [Output("collapse-A", "is_open"), 
     Output("collapse-B", "is_open")],
    Input("check-B", "checked"), # collapse-B is closed whenever checkbox is unticked
    Input("menu-A", "n_clicks"),
    Input("menu-B", "n_clicks"), 
    State("collapse-A", "is_open"),
    State("collapse-B", "is_open"),
)
def on_filter_menu(*args):
    ctx = dash.callback_context
    
    if ctx.triggered:
        
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # ensure Audience B cardbody is closed when its checkbox is unchecked
        # I preferred this action to be contained within on_checkbox_change...
        #... but any given component value can only be changed by one callback.
        if trigger_id == "check-B":
            if ctx.triggered[0]["value"] == False:
                ctx.states["collapse-B.is_open"] = False
        
        else:
            # corresponding collapse id 
            collapse_id = re.sub("menu", "collapse", trigger_id)
            
            # inverse the is_open state of corresponding collapse_id
            ctx.states[collapse_id + ".is_open"] = not ctx.states[collapse_id + ".is_open"]
        
    # return states
    # note callbacks run on launch thus states need returned regardless of triggering
    return tuple(state for state in ctx.states.values())


####################### filter menu headers: expand/collapse menu headers A and B #######################

demos = ["markets", "genders", "ages", "incomes", "travels", "custom"]

@app.callback(
    [Output("collapse-{}-A".format(demo), "is_open") for demo in demos] +
    [Output("collapse-{}-B".format(demo), "is_open") for demo in demos],
    
    [Input("button-{}-A".format(demo), "n_clicks") for demo in demos] +
    [Input("button-{}-B".format(demo), "n_clicks") for demo in demos] +
    [Input("not-audience-A", "checked")],
    
    [State("collapse-{}-A".format(demo), "is_open") for demo in demos] +
    [State("collapse-{}-B".format(demo), "is_open") for demo in demos],
    [State("not-audience-A", "checked")]
)
def on_filter_menu_header(*args):
    ctx = dash.callback_context
    
    if ctx.triggered:
        
        # identify input component that triggered callback
        # reference: https://dash.plotly.com/advanced-callbacks
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # if the trigger is a menu header:
        if trigger_id != "not-audience-A":
            
            # corresponding collapse id 
            collapse_id = re.sub("button", "collapse", trigger_id)
            
            # inverse the is_open state of corresponding collapse_id
            ctx.states[collapse_id + ".is_open"] = not ctx.states[collapse_id + ".is_open"]
        
        else:
            # if "not-audience-A" is checked:
            if list(ctx.states.values())[-1]:
                # set the is_open state of all B menu headers to closed
                for state in ctx.states:
                    if "-B" in state: ctx.states[state] = False            
        
    # return states (but we ignore last state: "not-audience-A")
    # note callbacks run on launch thus states need returned regardless of triggering
    return tuple([state for state in ctx.states.values()][:-1])



# in addition to the B menu headers being set to "is_open" = closed
# in the above function, we use the below function to also ensure the
# B menu headers are set to "disabled" = True
@app.callback(
    [Output("button-{}-B".format(demo), "disabled") for demo in demos],
    Input("not-audience-A", "checked")
)
def on_not_audience_A_checked(checked):
    if checked:
        return tuple([True]*6)
    else:
        return tuple([False]*6)



####################### return boolean mask (to subsequently filter data with), sample, and summaries whenever inputs change for Audience A / B #######################

def behavioural_summary_values(values):
    # if response_values are all integers, we simply want min - max range:
    if all([isinstance(x, int) for x in values]):
        return "{} - {}".format(min(values), max(values))
    else:
        # there may be a combination of string and numbers (e.g. the airport experience satisfaction scale)
        return ", ".join([str(x) for x in values])


# on_input_changes is a bulky function so I have teased out the main code from the function...
# ... and wrapped it in the following function:
def filter_and_summaries(column_map):
    masks = []
    for col_name, value in column_map.items():
        
        if col_name in ["Market", "Gender"]:
            
            # establish value for summary:
            try:
                # if value corresponds to an option, return option
                summary = list(cols_options[col_name].keys())[list(cols_options[col_name].values()).index(value)]
            except ValueError:
                # if value does not correspond to an option, return value
                summary = " ".join(value)
            finally:
                if col_name == "Market":
                    market_summary = summary
                elif col_name == "Gender":
                    gender_summary = summary
            
            # only bother to filter if not "All" markets / genders are selected
            if summary != "All":
                # value is a list of [markets/genders]
                mask = data.get_data()[data.corresponding("Variable alias", col_name, "Column")[0]].isin(value)
                masks.append(mask)
                
    
        elif col_name in ["Age", "Income", "Travel"]:
            
            # establish value for summary:
            try:
                # if value corresponds to an option, return option
                summary = list(cols_options[col_name].keys())[list(cols_options[col_name].values()).index(value)]
    
            # if value does not correspond to an option, return value                
            except ValueError:
    
                if col_name == "Age":
                    # check that range slider is not selected on only one value
                    if value[0] != value[1]:
                        summary = "{} - {} years".format(value[0], value[1])
                    else:
                        summary = "{} years".format(value[0])
                
                elif col_name == "Income":
                    # check that range slider is not selected on only one value
                    if value[0] != value[1]:
                        summary = "${:,} - ${:,}".format(value[0], value[1])
                    else:
                        summary = "${:,}".format(value[0])
                
                elif col_name == "Travel":
                    # check that range slider is not selected on only one value
                    if value[0] != value[1]:
                        summary = "{} - {} trips".format(value[0], value[1])
                    else:
                        summary = "{} trips".format(value[0])
            
            finally:
                if col_name == "Age":
                    age_summary = summary
                elif col_name == "Income":
                    income_summary = summary
                elif col_name == "Travel":
                    travel_summary = summary                
            
            # only bother to filter if "All" is not selected
            # this also prevents non-numeric data always beings excluded (e.g. missing data / outliers)
            if summary != "All":
            
                # value is a list of [min, max]
                for index, v in enumerate(value):
                    # min value
                    if index == 0:
                        mask = data.get_data()[data.corresponding("Variable alias", col_name, "Column")[0]] >= v
                        masks.append(mask)
                    # max value
                    elif index == 1:
                        mask = data.get_data()[data.corresponding("Variable alias", col_name, "Column")[0]] <= v
                        masks.append(mask)
            
                    
        elif col_name in ["Travel purpose", "Travel domain"]:
            
            # establish value for summary:
            try:
                # if value corresponds to an option, return option
                summary = list(cols_options[col_name].keys())[list(cols_options[col_name].values()).index(value)]
            except ValueError:
                # if value does not correspond to an option, it means no option is selected
                summary = ""
            finally:
                if col_name == "Travel purpose":
                    purpose_summary = summary
                elif col_name == "Travel domain":
                    domain_summary = summary
                    
                    # because Travel domain is always last in the loop, we can stitch together the "type_summary" variable:
                    # if both have values, drop "travellers"
                    if domain_summary and purpose_summary:
                        combined = [re.sub("travelers", "", summary)
                                    for summary in [domain_summary, purpose_summary]]
                        type_summary = " ".join(combined) + "travelers"
                    # if neither have values, return "All"
                    elif not domain_summary and not purpose_summary:
                        type_summary = "All"
                    # else return whichever is selected + empty string
                    else:
                        type_summary = domain_summary + purpose_summary
                    
            # only bother to filter if an option is selected (not None)
            if value:
                mask = data.get_data()[data.corresponding("Variable alias", col_name, "Column")[0]] == value
                masks.append(mask)
    
    
    # check if Behavioural filters are in use:
    if all([column_map["question"], column_map["items"], column_map["responses"]]):
        
        # iterate over each question item, fetch the data column, and generate mask based on selected response values
        for item in column_map["items"]:
            
            # we need a different way to create the mask for Q15 (open-ended question)
            if column_map["question"][:3] == "Q15":
                
                # are any of the response values in the observation?
                mask = data.get_data()[data.corresponding("Component", item, "Column",
                                                          initial_filter_col = "Question", initial_filter_value = column_map["question"])[0]].str.contains("|".join(column_map["responses"]), regex=True)                 
            else:
                # is the observation in the response values?
                mask = data.get_data()[data.corresponding("Component", item, "Column",
                                                          initial_filter_col = "Question", initial_filter_value = column_map["question"])[0]].isin(column_map["responses"])    
            masks.append(mask)
            
            
        behavioural_summary = data.question_ids[column_map["question"]] + " | " + \
                              ", ".join(column_map["items"]) + " | " + \
                              behavioural_summary_values(column_map["responses"])    
        
    else:
        behavioural_summary = "-"
    
    
    # unpack items in 'masks' list (each item is a boolean mask series)
    # reduce to a single array by evaluating where all masks equal True
    # reference: see above
    final_mask = list(map(all, zip(*masks)))

    # if every component is set to "All", final_mask will be an empty list!    
    mask_len = sum(1 for i in final_mask if i) if final_mask else data.TOTAL_SAMPLE
    
    sample_update = "{:,} ({:.0%})".format(mask_len,
                                            mask_len / data.TOTAL_SAMPLE)
    
    summaries = [market_summary, gender_summary, age_summary, income_summary, travel_summary, type_summary, behavioural_summary]
    summary_colors = ["" if summary == "All" or summary == "-" else "text-info" for summary in summaries]
    
    return final_mask, sample_update, summaries, summary_colors
    


# this function is used to return the inverse of Audience A for Audience B when "Not Audience A" is in use.
def if_not_audience_A(component, final_mask_len = None, final_mask = None, summaries = None):
    
    # must pass Audience A final_mask_len
    if component == "sample_update":
        # note: if Audience A is equal to entire sample then Audience A final_mask will be an empty list
        # that means final_mask_len would equal 0
        mask_len = data.TOTAL_SAMPLE - final_mask_len if final_mask_len else 0
        return "{:,} ({:.0%})".format(mask_len,
                                      mask_len / data.TOTAL_SAMPLE)
    
    # must pass Audience A final_mask
    elif component == "final_mask":
        # note: if Audience A is equal to entire sample then Audience A final_mask will be an empty list
        # that means we would have nothing to inverse
        return [not x for x in final_mask] if final_mask else [False]*data.TOTAL_SAMPLE
    
    # must pass Audience A summaries and final_mask_len
    elif component == "summaries":
        # note: if Audience A is equal to entire sample then Audience A final_mask_len will equal 0
        # that means we would show "All" when we should shown nothing
        return ["NOT " + summary if summary != "All" and summary != "-" else summary for summary in summaries] if final_mask_len else \
               ["" for summary in summaries]
    


# note that the ""All-type-" input from travel_categories is omitted. This is because we do not
# need to know if it has changed: if it has changed, one of "purpose-type-" or "domain-type-" 
# will have changed. It is also excluded because there is no data column associated with it.
# new: Behavioural filter components now added to input_components
input_components = ["market-", "gender-", "age-", "income-", "travel-"] + travel_categories[1:] + ["custom_selected_question-", "custom_selected_item-", "custom_selected_response-"]

# associated data column:
# new: Behavioural filter components now added
data_cols = ["Market", "Gender", "Age", "Income", "Travel"] + ["Travel purpose", "Travel domain"] + ["question", "items", "responses"]

# associated options dictionary:
options_dicts = [data.market_regions, data.gender_groups, data.age_groups, data.income_groups, data.travel_groups, data.traveller_purposes, data.traveller_domains]

# column : options_dict dictionary
# used to check if selected value of a component is equal to a radioitem option
# have to ignore the last 3, newly added Behavioural filter, items from data_cols
cols_options = {data_col : options_dict for data_col, options_dict in zip(data_cols[:-3], options_dicts)}


# output summaries
output_summaries = ["market-summary-", "gender-summary-", "age-summary-", "income-summary-", "travel-summary-", "traveler-type-summary-", "behavioural-summary-"]


@app.callback(
    # 1 list of 2 + 2 + 2 + 2 + 7 + 7 + 7 + 7 = 36 return items
    [Output("sample-A", "style"), Output("sample-B", "style")] +
    [Output("update-audience-A", "style"), Output("update-audience-B", "style")] +
    [Output("sample-A", "children"), Output("sample-B", "children")] +
    [Output("filtered-df-A", "data"), Output("filtered-df-B", "data")] +
    [Output("{}A".format(component), "children") for component in output_summaries] +
    [Output("{}B".format(component), "children") for component in output_summaries] +
    [Output("{}A".format(component), "className") for component in output_summaries] +
    [Output("{}B".format(component), "className") for component in output_summaries],

    # this function is run whenever Audience B checkbox is changed OR 
    # not-audience-A checkbox is changed OR
    # update button is pressed OR 
    # inputs change
    # if Audience B checkbox is changed: nothing is updated except sample (B) and update button (B) opacity is toggled
    # if inputs change: nothing is updated except update button is made visible
    # if button is pressed: everything is updated and update button is made invisible
    Input("check-B", "checked"),
    Input("not-audience-A", "checked"),    
    [Input("update-audience-A", "n_clicks"), Input("update-audience-B", "n_clicks")] +
    [Input("{}A".format(component), "value") for component in input_components] +
    [Input("{}B".format(component), "value") for component in input_components],
    
    # current state of style dictionary of sample-B label and update-audience-B button
    # current state of style dictionary of sample-A label and update-audience-A button
    [State("sample-B", "style"), State("update-audience-B", "style")] +
    [State("sample-A", "style"), State("update-audience-A", "style")] +
    # current values of data input components / used for df filtering
    [State("{}A".format(component), "value") for component in input_components] +
    [State("{}B".format(component), "value") for component in input_components] +
    # whether or not user has selected "Not Audience A" / if both these last states == True then filtered-df-B is updated at same time as filtered-df-A
    [State("check-B", "checked")] + [State("not-audience-A", "checked")]
)
def on_input_change_or_button_press(checkbox, *args, data_cols = data_cols, cols_options = cols_options):
    # final_mask reference: https://stackoverflow.com/questions/62113972/logical-and-operation-across-multiple-lists
    
    ctx = dash.callback_context
     
    # identify input component that triggered callback
    # reference: https://dash.plotly.com/advanced-callbacks
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # this callback is triggered twice on initial launch:
    # 1st run: 
        # Dash checks all callback functions 
        # the traveller-type inputs are set to None in layout
        # the remaining inputs are set to None as they are yet to be assigned their values by their respective callbacks
        # note that the first 4 and the last 2 states are excluded from the 1st run check (i.e. non input components)
    # 2nd run: 
        # remaining inputs are assigned their values - and thus all fire
        # it is the only time when Audience A AND B inputs simultaneously fire
    
    # Note: the first 4 states are excluded from the below 1st run check:
    # (sample-A/B.style and update-audience-A/B.style)
    
    # 1st run:
    if all(v is None for v in list(ctx.states.values())[4:-2]):
        return [no_update]*2 + \
               [no_update]*2 + \
               [no_update]*2 + \
               [no_update]*2 + \
               [no_update]*7 + \
               [no_update]*7 + \
               [no_update]*7 + \
               [no_update]*7

    # 2nd run:
    elif all(x in [dic['prop_id'] for dic in ctx.triggered]
             for x in ['market-A.value', 'market-B.value']):
        return [no_update]*2 + \
               [no_update]*2 + \
               [no_update]*2 + \
               [no_update]*2 + \
               [no_update]*7 + \
               [no_update]*7 + \
               [no_update]*7 + \
               [no_update]*7
    
    
    # Determine what user has changed:
        
    else:
        
        # if user toggled Audience B checkbox:
        if trigger_id == "check-B":
            # if checkbox is checked (True):
            if checkbox:
                sample_B_style = list(ctx.states.values())[0]
                sample_B_style['opacity'] = 1
                
                update_B_style = list(ctx.states.values())[1]
                update_B_style['opacity'] = 1
                
                return [no_update, sample_B_style] + \
                       [no_update, update_B_style] + \
                       [no_update]*2 + \
                       [no_update]*2 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7 
            else:
                sample_B_style = list(ctx.states.values())[0]
                sample_B_style['opacity'] = 0    
                
                update_B_style = list(ctx.states.values())[1]
                update_B_style['opacity'] = 0
              
                return [no_update, sample_B_style] + \
                       [no_update, update_B_style] + \
                       [no_update]*2 + \
                       [no_update]*2 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7   
            
        
        # if user has not pressed "update" then they have changed filter inputs (inc. the "Not Audience A" checkbutton):
        # if this is the case then show the Audience A/B update button
        elif "update-audience" not in trigger_id:
            # if Audience A filters have changed:
            if trigger_id[-1] == "A" and not trigger_id == "not-audience-A": 
                sample_A_style = list(ctx.states.values())[2]
                sample_A_style['display'] = 'none'
                
                update_A_style = list(ctx.states.values())[3]
                update_A_style['display'] = 'inline'
                
                return [sample_A_style, no_update] + \
                       [update_A_style, no_update] + \
                       [no_update]*2 + \
                       [no_update]*2 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7    
            # if Audience B filters or "Not Audience A" checkbutton have changed:
            elif trigger_id[-1] == "B" or trigger_id == "not-audience-A": 
                sample_B_style = list(ctx.states.values())[0]
                sample_B_style['display'] = 'none'
                
                update_B_style = list(ctx.states.values())[1]
                update_B_style['display'] = 'inline'
                
                return [no_update, sample_B_style] + \
                       [no_update, update_B_style] + \
                       [no_update]*2 + \
                       [no_update]*2 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7 + \
                       [no_update]*7 
            
        
        # else, by process of elimination, the user must have pressed an update button:
        else:
            if trigger_id[-1] == "A":
                inputs = list(ctx.states.values())[4:14] # (exclude sample x2 and update button x2) 1st 10 values in ctx.states.values
                
                column_map = {col_name : value for col_name, value in zip(data_cols, inputs)}
                final_mask, sample_update, summaries, summary_colors = filter_and_summaries(column_map)
                
                sample_A_style = list(ctx.states.values())[2]
                sample_A_style['display'] = 'inline'
                
                update_A_style = list(ctx.states.values())[3]
                update_A_style['display'] = 'none'
                
                # if "Not Audience A" is selected: confirm Audience A final_mask_len now to avoid repeating
                if all(list(ctx.states.values())[-2:]): final_mask_len = sum(1 for i in final_mask if i)
                
                return [sample_A_style, no_update if not all(list(ctx.states.values())[-2:]) else sample_A_style] + \
                       [update_A_style, no_update if not all(list(ctx.states.values())[-2:]) else update_A_style] + \
                       [sample_update, no_update if not all(list(ctx.states.values())[-2:]) else if_not_audience_A("sample_update", final_mask_len = final_mask_len)] + \
                       [json.dumps(final_mask), no_update if not all(list(ctx.states.values())[-2:]) else json.dumps(if_not_audience_A("final_mask", final_mask = final_mask))] + \
                       summaries + \
                       ([no_update]*7 if not all(list(ctx.states.values())[-2:]) else if_not_audience_A("summaries", summaries = summaries, final_mask_len = final_mask_len)) + \
                       summary_colors + \
                       ([no_update]*7 if not all(list(ctx.states.values())[-2:]) else summary_colors)
                
            elif trigger_id[-1] == "B":
                # is the user using Audience B filters? (not-audience-A is last state)
                if not list(ctx.states.values())[-1]:
                    inputs = list(ctx.states.values())[14:24] # 2nd 10 values in ctx.states.values
                    
                    column_map = {col_name : value for col_name, value in zip(data_cols, inputs)}
                    final_mask, sample_update, summaries, summary_colors = filter_and_summaries(column_map)
                
                # else, the user wants the inverse of Audience A
                else:
                    inputs = list(ctx.states.values())[4:14] # 1st 10 values in ctx.states.values (Audience A values)
                    
                    column_map = {col_name : value for col_name, value in zip(data_cols, inputs)}
                    final_mask, sample_update, summaries, summary_colors = filter_and_summaries(column_map)                  
                    
                    # inverse:
                    final_mask_len = sum(1 for i in final_mask if i)
                    
                    sample_update = if_not_audience_A("sample_update", final_mask_len = final_mask_len)
                    final_mask = if_not_audience_A("final_mask", final_mask = final_mask)
                    summaries = if_not_audience_A("summaries", summaries = summaries, final_mask_len = final_mask_len)
                    
                sample_B_style = list(ctx.states.values())[0]
                sample_B_style['display'] = 'inline'
                
                update_B_style = list(ctx.states.values())[1]
                update_B_style['display'] = 'none'
                
                return [no_update, sample_B_style] + \
                       [no_update, update_B_style] + \
                       [no_update, sample_update] + \
                       [no_update, json.dumps(final_mask)] + \
                       [no_update]*7 + \
                       summaries + \
                       [no_update]*7 + \
                       summary_colors
       

####################### disable/enable Audience B on checkbox click #######################

# Ideally, the following components would be controlled within this callback:
    # collapse-B.is_open (controlled by on_filter_menu)
    # sample-B.style (controlled by on_input_change_or_button_press)
    # update-audience-B.style (on_input_change_or_button_press)
    
# This was not possible because any given component property can only be changed by ONE
# callback function...

# output summaries
text_headers = ["market-text-header-B", "gender-text-header-B", "age-text-header-B", "income-text-header-B", "travel-text-header-B", "traveler-type-text-header-B", "behavioural-text-header-B"]

@app.callback(
    Output("menu-B", "disabled"),
    [Output(component, "style") for component in text_headers],
    [Output("{}B".format(component), "style") for component in output_summaries],
    Input("check-B", "checked"),
    State("menu-B", "disabled")
)
def on_checkbox_change(checkbox, menu_button):
    
    ctx = dash.callback_context
    
    if ctx.triggered:
        
        # toggle menu_button active/disabled
        menu_button = not menu_button
        
        # make summaries in cardfooter opaque if checked else invisible
        if checkbox:
            cardfooter_headers = tuple([{"height" : "1rem", "opacity" : 1}]*7)
            cardfooter_summaries = tuple([{"height" : "1rem", "opacity" : 1}]*7)
        else:
            cardfooter_headers = tuple([{"height" : "1rem", "opacity" : 0.5}]*7)
            cardfooter_summaries = tuple([{"height" : "1rem", "opacity" : 0}]*7)

        # note: tuples are unpacked by return - whereas a list is returned as one item
        return tuple([menu_button, *cardfooter_headers, *cardfooter_summaries])
    
    else:
        return tuple([no_update]*15)


####################### recieve boolean mask (final_mask) to filter data, and convert into graphic depending on selected question #######################

# I don't have to worry about when Audience A / B inputs change. This is because any changes to the inputs will result in
# the final_mask for Audience A / B changing (stored in dcc.Store components).

# IMPORTANT: 
# This dictionary determines what function runs when a question is selected and specifies the 
# required additional information for that function to run.
q_functions = {
    "Q1" : {"function" : agg_functions.travel_breakdown,
            "kwargs" : {"question" : "Q1",
                        "outlier column" : "Q1 travel outlier",
                        "total column" : "Travel",
                        "totals columns" : "Q1 totals"
                        }
            },
    "Q2" : {"function" : agg_functions.travel_breakdown,
            "kwargs" : {"question" : "Q2",
                        "outlier column" : "Q2 travel outlier",
                        "total column" : "Q2 travel",
                        "totals columns" : "Q2 totals"
                        }
            },
    
    "Q3" : {"function" : agg_functions.ffp_and_breakdown,
            "kwargs" : {"follow-up question" : "Q3B"}
            },
    
    "Q4" : {"function" : agg_functions.one_col_h_bar_plot,
            "kwargs" : {"cut-off" : 15,
                        "Others" : False,
                        "q_id" : "Q4"}
            },
    "Q5" : {"function" : agg_functions.two_col_h_bar_plot,
            "kwargs" : {"q_id" : "Q5"}
            },
    "Q6" : {"function" : agg_functions.two_col_h_bar_plot,
            "kwargs" : {"q_id" : "Q6"}
            },
     "Q7" : {"function" : agg_functions.airport_sentiment,
             "kwargs" : {}
            },
     "Q8" : {"function" : agg_functions.airport_voucher_spend,
             "kwargs" : {}
             },
     "Q9" : {"function" : agg_functions.horizontal_total_order_plot,
             "kwargs" : {"q_id" : "Q9"}
             },
     "Q10" : {"function" : agg_functions.airport_satisfaction,
              "kwargs" : {}
              },
     "Q11" : {"function" : agg_functions.airport_services,
              "kwargs" : {}
              },
     "Q12" : {"function" : agg_functions.horizontal_stacked_plot,
              "kwargs" : {"q_id" : "Q12"}
              },
     "Q13" : {"function" : agg_functions.horizontal_grouped_plot,
              "kwargs" : {"q_id" : "Q13"}
              },
     "Q14" : {"function" : agg_functions.horizontal_grouped_plot,
              "kwargs" : {"q_id" : "Q14"}
              },
     "Q15" : {"function" : agg_functions.horizontal_grouped_plot,
              "kwargs" : {"q_id" : "Q15",
                          "text clusters" : "Q15 clusters"}
              },
     "Q16" : {"function" : agg_functions.horizontal_grouped_plot,
              "kwargs" : {"q_id" : "Q16"}
              },
     "Q17" : {"function" : agg_functions.horizontal_stacked_plot,
              "kwargs" : {"q_id" : "Q17"}   
              },
     "Q18" : {"function" : agg_functions.horizontal_stacked_plot,
              "kwargs" : {"q_id" : "Q18"}   
              },
     "Q19" : {"function" : agg_functions.horizontal_total_order_plot,
              "kwargs" : {"q_id" : "Q19"}
              },
     "Q20" : {"function" : agg_functions.horizontal_stacked_plot,
              "kwargs" : {"q_id" : "Q20"}
              },
     "Q21" : {"function" : agg_functions.pie_chart_and_breakdown,
              "kwargs" : {'q_id' : "Q21"}
              },
     "Q22" : {"function" : agg_functions.pie_chart_and_breakdown,
              "kwargs" : {'q_id' : "Q22"}
              },
     "Q23" : {"function" : agg_functions.generic_pie_chart,
              "kwargs" : {'q_id' : "Q23"}
              },     
     "Q24" : {"function" : agg_functions.generic_pie_chart,
              "kwargs" : {'q_id' : "Q24"}
              },  
     "Q25" : {"function" : agg_functions.f_and_b_services,
              "kwargs" : {}
              }, 
     "Market" : {"function" : agg_functions.generic_pie_chart,
              "kwargs" : {'q_id' : "Market"}
              }, 
     "Gender" : {"function" : agg_functions.generic_pie_chart,
              "kwargs" : {'q_id' : "Gender"}
              }, 
      "Age" : {"function" : agg_functions.distribution_plot,
               "kwargs" : {'q_id' : "Age"}
               }, 
      "Income" : {"function" : agg_functions.distribution_plot,
               "kwargs" : {'q_id' : "Income"}
               }
    }

# this is a wrapper function that does all the necessary work before calling the function
# associated with the selected question that computes the analysis and visual.
def run_question_function(df, columns, A_or_B, q_id, q_functions = q_functions):
    # This function is passed the filtered df and then does the preparation work
    # before running the function associated with the selected question    
    
    # filter columns down to those associated with the quesiton
    # note: columns is always a list thus df is always a DataFrame (never a Series)
    df = df[columns]
    
    # replace column coded names with descriptive names (using inplace threw a warning)
    df = df.rename(columns = {old : new for old, new in zip(
        df.columns, data.corresponding("Variable alias", q_id, "Component"))})
        
    # run function associated with question
    function = q_functions[q_id]["function"]
    kwargs = q_functions[q_id]["kwargs"]
    
    # returns content that will be shown in "graph-area"
    return function(df, A_or_B, **kwargs)

inputs = ["df_A", "df_B", "question", "check-B"]

# FOR TESTING EACH AGG FUNCTION:
# values_dict = {"df_A" : data.df,
#                 "question" : "Q22 How do you feel about walking through retail stores after airport security checks in order to get to the departure hall?",
#                 }
# kwargs  = {"q_id" : ""}
# A_or_B = "A"
# q_id = "Q22"
# columns = data.corresponding("Variable alias", q_id, "Column")
# df = data.get_data()

@app.callback(
    Output("output-A", "children"),
    Output("output-A-width", "width"),
    Output("output-B", "children"),
    Output("output-B-width", "width"),
    Output("overview-container", "style"), # overview div container
    Input("overview", "n_clicks"), # research overview open button
    Input("close-overview", "n_clicks"), # research overview close button
    Input("filtered-df-A", "data"),
    Input("filtered-df-B", "data"),
    Input("question search", "value"), 
    Input("check-B", "checked"),
    State("filtered-df-A", "data"),
    State("filtered-df-B", "data"),
    State("question search", "value"), 
    State("check-B", "checked"),
    State("overview-container", "style") # overview div container
)
def produce_graphic(*args):
    # resource for read_json: https://dash.plotly.com/sharing-data-between-callbacks
    
    ctx = dash.callback_context
    
    # if this is initial launch
    if not ctx.triggered:
        return tuple([no_update]*5)
        
    # this callback is triggered on launch and, of course, by subsequent user input.
    # output is only generated when a question is selected in the dropdown menu.
    # the "research overview" (see OVERVIEW in layout) is displayed on launch and whenever the "Research overview" button is pressed.
    
    # identify input component that triggered callback
    # reference: https://dash.plotly.com/advanced-callbacks
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]        
    
    
    # current style of research overview container (inline or none)
    overview_style = list(ctx.states.values())[-1]
    
    # if the "Research overview" button was triggered, make research overview appear:
    if trigger_id == "overview":
        overview_style["display"] = "inline"
        return None, 12, None, None, overview_style

    # else if the Research overview "close button" was triggered, make research overview disappear:
    elif trigger_id == "close-overview":
        overview_style["display"] = "none"
        return None, 12, None, None, overview_style

    else:
        
        # ensure research overview is hidden for all other permutations
        overview_style["display"] = "none"
        
        # make dictionary of output values
        # excludes last state (overview-container.style)
        values_dict = {input_ : value for input_, value in zip(inputs, list(ctx.states.values())[:-1])}        
        
        # ensure a question is selected:
        # otherwise there is nothing to do
        if values_dict["question"]:
            
            # fetch question id using question
            q_id = data.question_ids[values_dict["question"]]
            
            # retrieve columns associated with the question id
            # note: this returns a list regardless of the number of column names returned
            columns = data.corresponding("Variable alias", q_id, "Column")
            
            # this will be populated with generated content
            output =  {"A" : "", "B" : ""}
            
            # DETERMINE TRIGGER:
            
            # if a question is selected: update both Audience A and B content (if checked) OR
            # if both filtered-df-A AND filtered-df-B have been simultaneously updated (user updates Audience A with "Not Audience A" checkbutton selected)
            # it is important that this is the first condition to be checked
            if trigger_id == "question search" or len(ctx.triggered) == 2:
            
                for A_or_B in ["A", "B"]:
                    
                    # if this is the "B" loop and check-B is not checked, skip loop
                    if A_or_B == "B" and not values_dict["check-B"]:
                        continue
                
                    # use boolean mask - a list; stored as json - to produce filtered df
                    # note: the list is empty if no filtering has been applied thus assign entire data in this case
                    df = data.get_data().loc[json.loads(values_dict["df_{}".format(A_or_B)])] \
                        if json.loads(values_dict["df_{}".format(A_or_B)]) \
                        else data.get_data()
                    
                    # catch when user has set Audience A/B sample size to < 10
                    # this is to minimise probability of errors in the agg functions due to data being inadequate in size / variation of values
                    if len(df) < 10: 
                        output[A_or_B] = [dcc.Markdown("Please ensure sample comprises 10+ individuals.",
                                                       className = "text-danger" if A_or_B == "A" else "text-secondary")]
                    else:    
                        # fetch the content generated by function associated with question
                        output[A_or_B] = run_question_function(df, columns, A_or_B, q_id)
                
                # RETURN VALUES:
                output_A_width = 6 if output["B"] else 12
                output_B_width = 6 if output["B"] else None
                return output["A"], output_A_width, output["B"], output_B_width, overview_style
            
            
            # if Audience A or B inputs changed: update Audience A or B content
            elif trigger_id == "filtered-df-A" or trigger_id == "filtered-df-B":
                
                A_or_B = trigger_id[-1]

                # convert filtered Audience A/B df back from json
                df = data.get_data().loc[json.loads(values_dict["df_{}".format(A_or_B)])] \
                    if json.loads(values_dict["df_{}".format(A_or_B)]) \
                    else data.get_data()
                
                # catch when user has set Audience A/B sample size to > 10
                # this is to minimise probability of errors in the agg functions due to data being inadequate in size / variation of values
                if len(df) < 10: 
                    output[A_or_B] = [dcc.Markdown("Please ensure sample comprises 10+ individuals.",
                                                   className = "text-danger" if A_or_B == "A" else "text-secondary")]
                else:    
                    # fetch the content generated by function associated with question
                    output[A_or_B] = run_question_function(df, columns, A_or_B, q_id)
          
                # RETURN VALUES:
                if A_or_B == "A": output["B"] = no_update
                if A_or_B == "B": output["A"] = no_update
                return output["A"], no_update, output["B"], no_update, overview_style
                
            
            # if checked-B changed: update Audience B content accordingly
            elif trigger_id == "check-B":
                
                # if checked: generate Audience B content
                if values_dict["check-B"]:
                
                    # convert filtered Audience B df back from json
                    df = data.get_data().loc[json.loads(values_dict["df_B"])] \
                        if json.loads(values_dict["df_B"]) \
                        else data.get_data()
               
                    # catch when user is reactivating Audience B but sample size was previously < 10
                    # this is to minimise probability of errors in the agg functions due to data being inadequate in size / variation of values
                    if len(df) < 10: 
                        output["B"] = [dcc.Markdown("Please ensure sample comprises 10+ individuals.",
                                                    className = "text-secondary")]
                    else:
                        # fetch the content generated by function associated with question
                        output["B"] = run_question_function(df, columns, "B", q_id)
                
                    # RETURN VALUES:
                    return no_update, 6, output["B"], 6, overview_style
                
                # if unchecked: remove Audience B content
                else:
    
                    # RETURN VALUES:
                    return no_update, 12, None, None, overview_style
                
    
    
        # if no question is selected:
        return None, no_update, None, no_update, overview_style
        
    