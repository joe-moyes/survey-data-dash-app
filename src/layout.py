# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 11:20:08 2021

@author: Joseph.Moyes

File information:
    imported by index.py, which makes the below layout definition available for declaration.
"""
    
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# import app object
from app_instantiation import app

# import data
import data


# variable used to quickly highlight a Row or Col to assess size during layout production
IDENTIFY = {'background' : '#28FF00'}

####################### Div: "Research overview" content #######################

# Note: having the Spinner wrap this html.Div was a stroke of genius:
# the problem was, when wrapping the "output-A" html.Div, the spinner would appear in the center
# of the div, which often meant it was too low down the screen to actually see. This is not the case
# with OVERVIEW, which is always above "output-A" - and invisible/display = none. Moreover, OVERVIEW
# is a part of the produce_graphic callback, meaning it is checked whenever "output-A" is checked -
# and therefore reloads whenever output-A reloads.
    
OVERVIEW = dbc.Spinner(html.Div([dbc.Button("X",
                                id = "close-overview",
                                outline = True,
                                size = "sm",
                                n_clicks = 0,
                                color = "danger",
                                className = "float-right",
                                style = {"marginRight" : "50px",
                                         "marginTop" : "0px"}),
                     dcc.Markdown("""
#### Aim:
    
This research provides the latest insights on travelers' habits, attitudes, and needs as concerns the airport journey following the Covid pandemic. 
The findings, which extend data collected annually through _The Collinson Airport Experience Survey_ (2014-2019), inform what challenges and opportunities airports should expect as travel moves into a new era.

#### Method:
    
A survey was developed with 25 questions designed to investigate the following areas:
    
* Profiling regular airport passengers around the world
* Their views on improving the airport journey
* Their relationship with airports
* Their preferences on shopping and retail space
* Their preferences on F&B consumption at the airport

Regular airport passengers were defined as *taking at least 2 return trips* in a typical year before the Covid pandemic. Fieldwork was conducted independently by [Dynata](https://www.dynata.com/) and a sample of 6,024 regular airport passengers was collected between 17 August - 7 September 2021.

For any enquiries about this application, please contact joseph.moyes@collinsongroup.com.
""", style = {'margin': 50, 'padding' : '10px', "color" : "#003865", "backgroundColor" : "#DCEDF4"})
], id = "overview-container", style = {"display" : "inline"})
                                  , color = "danger",
                                    show_initially = False)


####################### Div: make section headers and questions in sidebar #######################

# generate a card where card header is a research section and...
# the body is a collapsable list of the section questions
def make_section_block(section_name, section_dict, question_ids = data.question_ids):
    """
    section_name: 
        - str: name of section
        - a key from the dictionary data.sections
    section_dict: 
        - dict: see additional notes
        - a value from the dictionary data.sections
        - Additional notes: 
            section represents {questions : [section questions],
                                id : index}
            questions: represents list of questions of the section
            id: represents corresponding component id -friendly value
    qustion_ids:
        - dictionary: {question : id}
        - where id represents corresponding component id -friendly value
    """   
    # section will be a basic header
    header = dbc.Button(section_name,
                        # refer to sections variable in data.py
                        id = "header-{}".format(section_dict['id']),
                        color = 'link',
                        size = 'lg',
                        n_clicks = 0
                        )
    
    # list out questions as list group items
    list_items = [dbc.ListGroupItem(dbc.Button(q,
                                               # refer to question_ids variable in data.py
                                               id = question_ids[q],
                                               color = "link",
                                               block = True,
                                               ),
                                    color = "#FFFFFF",
                                    active = True
                                    )
                  for q in section_dict['questions']]
    
    # return card
    return dbc.Card([
        dbc.CardHeader(header),
        dbc.Collapse(
            dbc.CardBody(dbc.ListGroup(list_items,
                                       flush = True)),
            # refer to sections variable in data.py
            id = "collapse-{}".format(section_dict['id']),
            is_open = False,
        ),
    ])

# stitch together a card per section header
menu = html.Div([make_section_block(section_name, section_dict) 
                for section_name, section_dict in data.sections.items()
                ], className = "accordion")


####################### Div: content bar #######################

# fix sidebar in place with zero margin space top, bottom and left
sidebar_style = {
    "height" : "100%",
    "left" : 0,
    "width" : "25%",
    "position": "fixed",
    "overflow-y": "scroll"
}

sidebar = dbc.Card([
    dbc.CardBody([
        html.H2('Menu',
                className = "text-primary"),
        html.Hr(),
        dbc.Button("Research overview",
                   id = "overview",
                   color = 'link',
                   outline = False,
                   className = "text-primary",
                   size = 'lg',
                   n_clicks = 0,
                   style = {"marginLeft" : "0rem",
                            "marginBottom" : "1rem",
                            "padding" : "0px"}),
        menu
    ])
], color = "light", style = sidebar_style)


####################### Form: user inputs #######################

def make_inputs(version):
    
    market = dbc.FormGroup([
        dbc.Button("Market:",
            id = "button-markets-{}".format(version),
            color = 'link',
            className = "text-danger" if version == "A" else "text-secondary",
            size = 'md',
            n_clicks = 0
        ),
        
        dbc.Collapse([
            dbc.RadioItems(
                id = "toggle-markets-{}".format(version),
                options = [{'label': group, 'value' : group}
                           for group in data.market_regions],
                # value is assigned "All" by on_market_list on launch
                # this then triggers on_market_options...
                inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
            ),
            
            dcc.Dropdown(
                id = "market-{}".format(version),
                multi = True,
                # value is assigned by on_market_options on launch
                className = "dash-bootstrap",
                style = {"font-size" : "small",
                         "color" : "#003865"}
            )
        ], id = "collapse-markets-{}".format(version), is_open = False)
    ])
    
    
    gender = dbc.FormGroup([
        dbc.Button("Gender:",
            id = "button-genders-{}".format(version),
            color = 'link',
            className = "text-danger" if version == "A" else "text-secondary",
            size = 'md',
            n_clicks = 0
        ), 
        
        dbc.Collapse([
            dbc.RadioItems(
                id = "toggle-genders-{}".format(version),
                options = [{'label': group, 'value' : group}
                           for group in data.gender_groups],
                # value is assigned "All" by on_gender_list on launch
                # this then triggers on_gender_options...
                inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
            ),
            
            dcc.Dropdown(
                id = "gender-{}".format(version),
                multi = True,
                # value is assigned by on_gender_options on launch
                className = "dash-bootstrap",
                style = {"font-size" : "small",
                         "color" : "#003865"}    
            )
        ], id = "collapse-genders-{}".format(version), is_open = False)
    ])
    
    
    age = dbc.FormGroup([
        dbc.Button("Age:",
            id = "button-ages-{}".format(version),
            color = 'link',
            className = "text-danger" if version == "A" else "text-secondary",
            size = 'md',
            n_clicks = 0
        ), 
        
        dbc.Collapse([
            dbc.RadioItems(
                id = "toggle-ages-{}".format(version),
                options = [{'label': group, 'value' : group}
                           for group in data.age_groups],
                # value is assigned "All" by on_age_range on launch
                # this then triggers on_age_options...
                inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
            ),
            
            dcc.RangeSlider(
                id = "age-{}".format(version),
                min = data.ages['min'],
                max = data.ages['max'],
                step = 1,
                # value is assigned by on_age_options on launch
                allowCross = False,
                marks={i: '{}yrs'.format(i) for i in [data.ages['min'], data.ages['max']]},
                tooltip = {'always_visible' : False, 'placement' : 'bottom'},
                updatemode = 'mouseup',
                className = "dash-bootstrap",
                #Style = {"font-size" : "small"}
                
            )
        ], id = "collapse-ages-{}".format(version), is_open = False)
    ])
    
     
    income = dbc.FormGroup([
        dbc.Button("Household income (equivalised U.S. purchase power):",
            id = "button-incomes-{}".format(version),
            color = 'link',
            className = "text-danger" if version == "A" else "text-secondary",
            size = 'md',
            n_clicks = 0
        ), 
        
        dbc.Collapse([
            dbc.RadioItems(
                id = "toggle-incomes-{}".format(version),
                options = [{'label': group, 'value' : group}
                           for group in data.income_groups],
                # value is assigned "All" by on_income_range on launch
                # this then triggers on_income_options...
                inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
            ),
            
            dcc.RangeSlider(
                id = "income-{}".format(version),
                min = data.incomes['min'],
                max = data.incomes['max'],
                step = 1000,
                # value is assigned by on_income_options on launch
                allowCross = False,
                marks={i: '${:,}'.format(i) for i in [data.incomes['min'], data.incomes['max']]},
                tooltip = {'always_visible' : False, 'placement' : 'bottom'},
                updatemode = 'mouseup',
                className = "dash-bootstrap",
                #style = {"font-size" : "small"}
            )
        ], id = "collapse-incomes-{}".format(version), is_open = False)
    ])
    
    
    travel = dbc.FormGroup([
        dbc.Button("Travel (annual return trips before Covid-19):",
            id = "button-travels-{}".format(version),
            color = 'link',
            className = "text-danger" if version == "A" else "text-secondary",
            size = 'md',
            n_clicks = 0
        ), 
        
        dbc.Collapse([
            dbc.RadioItems(
                id = "toggle-travels-{}".format(version),
                options = [{'label': group, 'value' : group}
                            for group in data.travel_groups],
                # value is assigned "All" by on_travel_range on launch
                # this then triggers on_travel_options...
                inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
            ),
            
            dcc.RangeSlider(
                id = "travel-{}".format(version),
                min = data.travels['min'],
                max = data.travels['max'],
                step = 1,
                # value is assigned by on_travel_options on launch
                allowCross = False,
                marks={i: '{}trips'.format(i) for i in [data.travels['min'], data.travels['max']]},
                tooltip = {'always_visible' : False, 'placement' : 'bottom'},
                updatemode = 'mouseup',
                className = "dash-bootstrap",
                #style = {"font-size" : "small"}
            ),
            
            dbc.FormGroup([
                dbc.Col(dbc.RadioItems(
                    id = "All-type-{}".format(version),
                    options = [{'label': "All travelers", 'value' : "All"}],
                    value = "All",
                    inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
                ), width = 4),
                
                dbc.Col(dbc.RadioItems(
                    id = "purpose-type-{}".format(version),
                    options = [{'label': group, 'value' : data.traveller_purposes[group]}
                                for group in data.traveller_purposes],
                    value = None,
                    inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
                ), width = 4),
                
                dbc.Col(dbc.RadioItems(
                    id = "domain-type-{}".format(version),
                    options = [{'label': group, 'value' : data.traveller_domains[group]}
                                for group in data.traveller_domains],
                    value = None,
                    inline = True,
                labelStyle = {"font-size" : "small",
                              "color" : "#003865"}
                ), width = 4)
            ], row = True)
        ], id = "collapse-travels-{}".format(version), is_open = False)
    ])
    
    custom = dbc.FormGroup([
        dbc.Button("Behavioural:",
            id = "button-custom-{}".format(version),
            color = 'link',
            className = "text-danger" if version == "A" else "text-secondary",
            size = 'md',
            n_clicks = 0
        ), 
        
        dbc.Collapse([
            dbc.FormGroup([
                
                dbc.FormGroup([
                    dbc.Label("Question:", html_for = 'custom_selected_question-{}'.format(version), 
                              size = "sm", className = "text-primary", style = {"marginBottom" : "1px"}),
                    dcc.Dropdown(
                        id = 'custom_selected_question-{}'.format(version),
                        placeholder = 'select question...',
                        options = [{'label' : q, 'value' : q} for q in data.question_items_values_dict],
                        multi = False,
                        className = "dash-bootstrap",
                        style = {"font-size" : "small",
                                 "color" : "#003865",
                                 "whiteSpace" : "nowrap"} # stops wrapping / prevents longs Qs causing wrapping issues
                        )
                    ]),
                
                dbc.FormGroup([
                    dbc.Label("Question item:", html_for = 'custom_selected_item-{}'.format(version), 
                              size = "sm", className = "text-primary", style = {"marginBottom" : "1px"}),
                    dcc.Dropdown(
                        id = 'custom_selected_item-{}'.format(version),
                        placeholder = 'select question item(s)...',
                        options = [], # options is set on-the-fly depending on what question is selected in "custom_selected_question"
                        multi = True,
                        className = "dash-bootstrap",
                        style = {"font-size" : "small",
                                 "color" : "#003865"} 
                        )
                    ]),

                dbc.FormGroup([
                    dbc.Label("Response:", html_for = 'custom_selected_response-{}'.format(version),
                              size = "sm", className = "text-primary", style = {"marginBottom" : "1px"}),
                    dcc.Dropdown(
                        id = 'custom_selected_response-{}'.format(version),
                        placeholder = 'Select response(s)...',
                        options = [], # options is set on-the-fly depending on what question item(s) is selected in "custom_selected_item"
                        multi = True,
                        className = "dash-bootstrap",
                        style = {"font-size" : "small",
                                 "color" : "#003865"} 
                        )
                    ])
                
            ]),
                
        ], id = "collapse-custom-{}".format(version), is_open = False)
    ])
    
    if version == "B":
        # create a "NOT Audience A" filtering option
        not_audience_A = dbc.FormGroup([
            dbc.Col(dbc.Label("Not Audience A ",
                        size = "md",
                        className = "text-secondary",
                        style = {'paddingLeft' : '12px'} 
                        ), width = "auto"
                    ),
            dbc.Col(dbc.Checkbox(
                        id = "not-audience-A",
                        checked = False, # unchecked on launch
                        className = "bg-secondary",
                        # manually position checkbox to align with "Audience B"
                        # relative = default position: 1px down from top of default position and 15px in from the right
                        style = {"position" : "relative",
                                 "top" : "1px",
                                 "right" : "15px"}
                        ), width = "auto"
                    )
            ], row = True)
    else:
        not_audience_A = None
                                    


    return [market, gender, age, income, travel, custom, not_audience_A]
    
audience_A = dbc.Form(make_inputs(version = "A"))
audience_B = dbc.Form(make_inputs(version = "B"))

####################### Div: content #######################

content_style = {
    'padding-top' : '1rem'
}

content = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([dcc.Markdown("## Tomorrow\'s Traveler.", className = "text-primary"),
                      dcc.Markdown("## Tomorrow\'s Airport Experience.", className = "text-primary"),
                      dcc.Markdown("###### Collinson Research 2021", className = "text-danger"),
                    ], style = {'textAlign' : 'left',
                                'marginLeft' : '1rem'})
            ], width = 'auto'),
        
        dbc.Col(html.Div([html.A(html.Img(src = app.get_asset_url('Collinson logo.jpg'),
                                          style = {"max-width" : "35vh"}), # control width: ensure width does not exceed 35% of viewport (% values based on trial & error) 
                                 href = r"https://www.collinsongroup.com/", target='_blank'),
                          html.A(html.Img(src = app.get_asset_url('AD logo.jpg'),
                                          style = {"max-width" : "35vh"}), # control width: ensure width does not exceed 35% of viewport (% values based on trial & error)
                                 href = r"https://www.airportdimensions.com/", target='_blank')
                          ], style = {"display" : "inline-block"}),
                width = "auto")
    ], justify = "between", no_gutters = True),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id = 'question search',
                placeholder = 'search question list...',
                options = [{'label' : q, 'value' : q} for q in data.questions_order],
                multi = False,
                className = "text-primary",
                # add some margin space above and below question searchbar
                style = {"marginTop" : "8px",
                         "marginBottom" : "3px"}
                
            )
        ], width = 12)
    ], no_gutters = True, style = {"margin-bottom" : "1rem"}),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(dbc.Button("Audience A",
                                    id = "menu-A",
                                    color = 'link',
                                    outline = False,
                                    className = "text-danger",
                                    size = 'lg',
                                    n_clicks = 0
                                    ),
                                width = 6),
                                                                       
                        dbc.Col([dbc.Label("{:,} ({:.0%})".format(data.TOTAL_SAMPLE,
                                               data.TOTAL_SAMPLE / data.TOTAL_SAMPLE),
                                    id = "sample-A",
                                    size = "lg",    
                                    className = "text-danger",
                                    style = {'display' : 'inline',
                                             "position" : "relative",
                                             "top" : "8px"}
                                    ),
                                 dbc.Button("UPDATE FILTERS",
                                    id = "update-audience-A",
                                    color = 'link',
                                    outline = True,
                                    className = "text-danger",
                                    size = 'lg',
                                    n_clicks = 0,
                                    style = {'display' : 'none',
                                             "padding" : "0px",
                                             "position" : "relative",
                                             "top" : "8px"},
                                    )],
                                # align column content to right and pad right 2 characters
                                width = 6, style = {"textAlign" : "right",
                                                    "paddingRight" : "2rem"})
                    
                    # make row fill entire height of cardheader
                    ], className = "h-100"),  
                    
                    # customise cardheader height and leave no internal padding
                    style = {"height" : "3rem", "padding" : '0rem'}
                ),
                
                dbc.Collapse(dbc.CardBody(audience_A),
                             id = "collapse-A",
                             is_open = False),
                
                # &nbsp; represents whitespace in markdown
                dbc.CardFooter([dcc.Markdown("""
                                            **&nbsp;Market:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""All""",
                                              id = "market-summary-A", style = {"height" : "1rem"}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Gender:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""All""",
                                              id = "gender-summary-A", style = {"height" : "1rem"}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Age:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""All""",
                                              id = "age-summary-A", style = {"height" : "1rem"}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Income:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""All""",
                                              id = "income-summary-A", style = {"height" : "1rem"}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Travel:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""All""",
                                              id = "travel-summary-A", style = {"height" : "1rem"}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Traveler type:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""All""",
                                              id = "traveler-type-summary-A", style = {"height" : "1rem"}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Behavioural filters:&nbsp;**""", className = "text-danger", style = {"height" : "1rem"}),
                                dcc.Markdown("""-""",
                                              id = "behavioural-summary-A", style = {"height" : "1rem"})                                
                                ],
                                 
                               # flex worked as a solution for keeping markdown components inline
                               # flexWrap ensures components wrap onto a new line to prevent overflow!
                               style = {"display" : "flex",
                                        "flexWrap" : "wrap",
                                        "overflow-y" : "scroll", # this is required. Overflow is possible when a summary (usually Behavioural filters) wrap onto new lines.
                                        "fontSize" : "small",
                                        "padding" : "2px",
                                        "height" : "100%"} # container height must be specified to manually set height of elements
                               )
                
            ])
        ], width = 6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col([dbc.Button("Audience B",
                                        id = "menu-B",
                                        color = 'link',
                                        className = "text-secondary",
                                        size = 'lg',
                                        n_clicks = 0,
                                        disabled = True # disabled on launch
                                        ),
                                
                                dbc.Checkbox(
                                        id = "check-B",
                                        checked = False, # unchecked on launch
                                        className = "bg-secondary",
                                        # manually position checkbox to align with "Audience B"
                                        # relative = default position: 4px down from top of default position
                                        style = {"position" : "relative",
                                                 "top" : "4px"}
                                        )
                                ], width = 6),
                                                
                        dbc.Col([dbc.Label("{:,} ({:.0%})".format(data.TOTAL_SAMPLE,
                                               data.TOTAL_SAMPLE / data.TOTAL_SAMPLE),
                                    id = "sample-B",
                                    size = "lg",
                                    className = "text-secondary",
                                    style = {'opacity' : 0, # hidden on launch
                                             'display' : 'inline',
                                             "position" : "relative",
                                             "top" : "8px"} 
                                    ),
                                dbc.Button("UPDATE FILTERS",
                                    id = "update-audience-B",
                                    color = 'link',
                                    outline = True,
                                    className = "text-secondary",
                                    size = 'lg',
                                    n_clicks = 0,
                                    style = {'opacity' : 0,
                                             'display' : 'none',
                                             "padding" : "0px",
                                             "position" : "relative",
                                             "top" : "8px"},
                                    )],
                                # align column content to right and pad right 2 characters
                                width = 6, style = {"textAlign" : "right",
                                                    "paddingRight" : "2rem"})
                                                
                    # make row fill entire height of cardheader
                    ], className = "h-100"),  
                    
                    # customise cardheader height and leave no internal padding
                    style = {"height" : "3rem", "padding" : '0rem'}
                ),
                
                dbc.Collapse(dbc.CardBody(audience_B),
                             id = "collapse-B",
                             is_open = False),
                
                # &nbsp; represents whitespace in markdown
                # B Audience text headers need ids - they are greyed out when Audience B is unchecked
                dbc.CardFooter([dcc.Markdown("""
                                            **&nbsp;Market:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "market-text-header-B"),
                                dcc.Markdown("""All""",
                                              id = "market-summary-B", style = {"height" : "1rem", "opacity" : 0}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Gender:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "gender-text-header-B"),
                                dcc.Markdown("""All""",
                                              id = "gender-summary-B", style = {"height" : "1rem", "opacity" : 0}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Age:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "age-text-header-B"),
                                dcc.Markdown("""All""",
                                              id = "age-summary-B", style = {"height" : "1rem", "opacity" : 0}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Income:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "income-text-header-B"),
                                dcc.Markdown("""All""",
                                              id = "income-summary-B", style = {"height" : "1rem", "opacity" : 0}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Travel:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "travel-text-header-B"),
                                dcc.Markdown("""All""",
                                              id = "travel-summary-B", style = {"height" : "1rem", "opacity" : 0}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Traveler type:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "traveler-type-text-header-B"),
                                dcc.Markdown("""All""",
                                              id = "traveler-type-summary-B", style = {"height" : "1rem", "opacity" : 0}),
                                
                                dcc.Markdown("""
                                            **&nbsp;Behavioural filters:&nbsp;**""", className = "text-secondary", style = {"height" : "1rem", "opacity" : 0.5}, id = "behavioural-text-header-B"),
                                dcc.Markdown("""-""",
                                              id = "behavioural-summary-B", style = {"height" : "1rem", "opacity" : 0})                                
                                ],
                                 
                               # flex worked as a solution for keeping markdown components inline
                               # flexWrap ensures components wrap onto a new line to prevent overflow!
                               id = "cardfooter-B",
                               style = {"display" : "flex",
                                        "flexWrap" : "wrap",
                                        "overflow-y" : "scroll", # this is required. Overflow is possible when a summary (usually Behavioural filters) wrap onto new lines.                                        
                                        "fontSize" : "small",
                                        "padding" : "2px",
                                        "height" : "100%"} # container height must be specified to manually set height of elements
                               )
                
            ])
        ], width = 6),
    ], no_gutters = False),

    # OVERVIEW is usually invisible, including on launch. 
    # This means this row is not usually part of the layout.
    # However, it needs to be specified in the layout in order to link it to a callback...
    # ...to make it appear when the "Research overview" button is pressed.                                             
    dbc.Row(dbc.Col(OVERVIEW, width = 12)), 
             
    dbc.Row([dbc.Col(html.Div(id = "output-A"), 
                     style = {"paddingTop" : "15px"},
                     id = "output-A-width", 
                     width = 6),
             dbc.Col(html.Div(id = "output-B"), 
                     style = {"paddingTop" : "15px"},
                     id = "output-B-width", 
                     width = 6)],
            id = "graph-area")
    
], style = content_style)
    


# layout
layout = dbc.Container([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(sidebar, width = 3), 
        dbc.Col(content, width = 9)
    ], no_gutters = True),
    # source: https://dash.plotly.com/sharing-data-between-callbacks
    # this now stores the boolean mask instead of the filtered data - memory usage/spike is now kept below 500MB at all times!
    dcc.Store(data = "[]",
              id='filtered-df-A'),
    dcc.Store(data = "[]",
              id='filtered-df-B')
    ], fluid = True
)
    