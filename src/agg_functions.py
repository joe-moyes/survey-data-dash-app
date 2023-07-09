# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 09:23:00 2021

@author: Joseph.Moyes

File information:
    - contains the aggregation functions that are used by the callback function, produce_graphic.
    - each question id - as per in the Labels worksheet / dfL - is assigned a function, which is 
      looked up by produce_graphic.
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import regex as re

# need access to 'corresponding' function and 'dfL'
# note: when the app runs, the data file is imported when "from layout import layout" runs in index.py
# therefore, the below does not result in the data file being re-imported when the app runs
# (see index.py for explanation)
import data


# Important note on use of **kwargs:
# kwargs allows certain functions to be provided with the additional information they may require.
# E.g. the function 'travel_breakdown' requires that the outlier column alias is provided.
# it is important that ALL functions have kwargs in their definition, even if unused. This is because
# the functions are called on-the-fly by the 'produce_graphic' callback and so consistency is needed.


######################################## Helper functions

# When using a smaller, work laptop screen, lengthy y-axis text in horizontally-orientated plots
# were cut-off, even with "automargin" set to True. It seems a length of 40 chars is maximum.
# Thus - if a question item exceeds 40 chars in length, it needs wrapping.
# Note: Q4 has it's own unique wrapping: at specifically the space after "Airport"
def wrap_func(text, q_id = "unspecified"):
    
    if q_id == "unspecified":
    
        if len(text) > 80:
            thirds = round(text.count(" ") / 3)
            return " ".join(text.split()[:thirds]) + \
                   "<br>" + \
                   " ".join(text.split()[thirds:thirds*2]) + \
                   "<br>" + \
                   " ".join(text.split()[thirds*2:])    
    
        elif len(text) > 40:
            halfway_ish = round(text.count(" ") / 2) + 1 # makes first half of wrapped text longer
            return " ".join(text.split()[:halfway_ish]) + \
                   "<br>" + \
                   " ".join(text.split()[halfway_ish:])

        else:
            return text
        
        
    elif q_id == "Q4":
            
        if len(text) > 40:
            return re.sub("(Airport)\s", r"\1" + "<br>", text)
        else:
            return text
        

# for coloring text on the y-axis in a horizontally-orientated plot
# E.g. to distinguish between "positive-sentiment" versus "negative-sentiment" response options
# Source: https://stackoverflow.com/questions/58183962/how-to-color-ticktext-in-plotly
def color(color, text):
    
    colored_text = "<span style='color:" + str(color) + "'>" + str(text) + "</span>"
    return colored_text

    
# used to format the bins after binning the age / income data
# prepend is basically just used to differentiate between income / age by whether to prepend bracket with dollar sign
def format_bins(bin_string, prepend = "$"):
    # remove brackets
    step_1 = re.sub("[\[\)]", "", bin_string)
    # split the 2 numbers and format (if it's the 2nd number then subtract by 1)
    step_2 = ["{}{:,.0f}".format(prepend, float(num)) if ind == 0 else "{}{:,.0f}".format(prepend, float(num) - 1)
              for ind, num in enumerate(step_1.split(", "))]
    # join the 2 formatted numbers seperated by a dash
    return " - ".join(step_2)

# this is used after the above function is run, specifcally for the first bin
# for the first bin, I have opted to undo the substraction by 1 so that the first bin reads e.g.:
# "Under $25,000" instead of something like "$24,999 or less".
def remove_punc_and_add_one(match_group):
    # remove punctuation
    step_1 = re.sub("[\D]", "", match_group)
    # add one, and (re)format
    return "{:,}".format(int(step_1) + 1)


######################################## Q1 / Q2

def travel_breakdown(df, A_or_B, **kwargs):
    """
    # returns:
        - markdown confirming median number of return trips
        - table confirming breakdown by trip domain (columns) and purpose (rows)
        - bar plot confirming % that have taken >= n trips
        - group bar plot confirming % that have taken >= n trip type (purposes and domains)
        - markdown confirming how many outliers were removed
        
    # notes:
        - outliers are removed for all computations except median
        - reliance on data.py to lookup alias data columns
        
    # kwargs:
        this function relies on the following dictionary:
            {"question" : question id (either "Q1" or "Q2")
             "outlier column" : alias associated with outlier column (e.g. "Q1 travel outlier"),
             "total column" : alias associated with total trips column (e.g. "Travel"),
             "totals columns" alias associated with breakdown total columns (e.g. "Q1 totals")}
        
        each value is given as a string. The string is looked up using data.corresponding() in
        the "Labels" worksheet of "Prepared data.xlsx" (stored as "data.dfL") under the "Variable
        alias" column, and the correspoding value(s) in the "Column" column are fetched. These are
        then used to retrieve the necessary data columns in data.get_data() to perform necessary actions.
    """
    
    ################## identify if this is question 1 or 2 ##################
    
    if kwargs["question"] == "Q1": timeframe = "per year before 2020"
    if kwargs["question"] == "Q2": timeframe = "between August 2020 - 2021"

    
    ################## filter out outliers ##################
    
    # fetch travel outlier column
    outlier_col = data.corresponding("Variable alias", kwargs["outlier column"], "Column")[0]
    
    # use index of filtered df to look up corresponding outlier values
    mask = data.get_data().loc[df.index, outlier_col]
    
    # capture sample size before outliers are removed...
    with_outliers = len(df)
    
    # filter out outliers from filtered df (TRUE = outlier)
    df = df[~mask]
    del mask
    
    # number of outerlier removed:
    # to be reported as a footnote at end
    outliers_removed = with_outliers - len(df)
    
    
    # 1 ################## Create markdown ##################
    
    # fetch total column
    total_col = data.corresponding("Variable alias", kwargs["total column"], "Column")[0]
    
    # use index of filtered df to look up corresponding outlier values
    # ... and fetch median
    total_col = data.get_data().loc[df.index, total_col]
    return_trips = total_col.median() 
    
    # compile markdown:
    markdown = html.Div([
        dcc.Markdown("### {} return trip{}".format(int(return_trips), "s" if return_trips != 1 else ""), 
                     className = "text-danger" if A_or_B == "A" else "text-secondary"),
        dcc.Markdown("### &nbsp;{}".format(timeframe), 
                     className = "text-primary")]
        , style = {"display" : "flex",
                   "flexWrap" : "wrap",
                   "marginBottom" : "2rem"}
    )
    
    
    # 2 ################## Create breakdown table ##################
    
    # 2a ################## compute mean values for table ##################
    
    # for each column, compute the mean
    df_means = df.apply(np.mean)
    
    # compute the total by summing all cells
    total_trips = df_means.sum()
    
    # compute sums
    domains = ["[Dd]omestic", "[Ii]nternational"]
    purposes = ["[Ll]eisure", "[Bb]usiness", "[Oo]ther"]
    
    sum_for = domains + purposes
    for factor in sum_for:
        df_means.loc[factor + " sum"] = df_means[df_means.index.str.contains(factor)].sum()
    
    # for each value, divide by total trips and format as % rounded to 0 dp
    df_means = df_means.apply(lambda x: "{:.0%}".format(x / total_trips))
    
    
    # 2b ################## create table ##################
        
    table_header = [
    html.Thead(html.Tr([html.Th("Breakdown of all trips taken collectively {} by Audience {}".format(timeframe, A_or_B),
                                style = {"font-style" : "normal",
                                         "font-weight" : "normal",
                                         "text-align" : "left"}), 
                        html.Th("Domestic"), 
                        html.Th("International"), 
                        html.Th(" ")]
                       )
               )
    ]
    
    # iterate over purpose and domain to generate non-sum cells of table
    rows = [html.Tr([html.Td(df_means.loc[df_means.index.str.fullmatch(".*" + domain + ".*" + purpose + ".*")][0]
                             , className = "text-danger" if A_or_B == "A" else "text-secondary"
                             ) 
                     for domain in domains])
            for purpose in purposes]
    
    # preprend row headers:
    rows[0].children.insert(0, html.Td("For leisure", style = {"font-weight" : "bold",
                                                               "text-align" : "right"}))
    rows[1].children.insert(0, html.Td("For business", style = {"font-weight" : "bold",
                                                               "text-align" : "right"}))
    rows[2].children.insert(0, html.Td("Other (e.g. commuting, visiting friends/relatives)", style = {"font-weight" : "bold",
                                                                                                      "text-align" : "right"}))
    
    # append row sums:
    for row, purpose in zip(rows, purposes):
        row.children.append(html.Td(df_means.loc[df_means.index.str.contains(purpose + " sum",
                                                                             regex = False)][0]
                                    , className = "text-danger" if A_or_B == "A" else "text-secondary"
                                    , style = {"font-weight" : "bold"}
                                    )
                            )
       
   
    # add bottom row / column sums
    # ps - I could've used Tfoot here (similar to Thead). But doesn't really make much difference.
    table_footer = html.Tr([html.Td(" ")] +
                       [html.Td(df_means.loc[df_means.index.str.contains(domain + " sum",
                                                          regex = False)][0]) 
                        for domain in domains] +
                       [html.Td("100%")]
                       , className = "text-danger" if A_or_B == "A" else "text-secondary"
                       , style = {"font-weight" : "bold"}
                   )
    rows.append(table_footer)
    
    rows.append(html.Tr([html.Td(" ")]*4)) # empty row but produces a bottom line for the table
    
    # wrap rows in Tbody class
    table_body = [html.Tbody(rows)]
    
    table = dbc.Table(table_header + table_body, bordered = False,
                      style = {"text-align" : "center"},
                      className = "text-primary") # text color of table is primary unless specified otherwise
    
    
    # 3 ################## Create reverse cumulative bar charts ##################
    
    # 3a ################## make df of totals columns ##################
    
    # fetch totals columns
    total_cols = data.corresponding("Variable alias", kwargs["totals columns"], "Column")
    
    # use index of filtered df to look up corresponding totals columns
    totals = data.get_data().loc[df.index, total_cols]
    
    # rename columns with descriptions
    totals = totals.rename(columns = {old : new for old, new in zip(
                totals.columns, data.corresponding("Variable alias", kwargs["totals columns"], "Component"))})
    
    
    # 3b ################## append kwargs["total column"] ##################

    # Note: we also want the reverse cumulative breakdown of the "total column"
    # we already have the series of values represented by 'total_col' (see part 1)
    
    # rename to descriptive name
    total_col = total_col.rename(
        data.corresponding("Variable alias", kwargs["total column"], "Component")[0])

    # vlookup total_col and append it to totals
    totals[total_col.name] = totals.index.map(total_col.to_dict())
    del total_col
    
    # 3c ################## compute reverse cumulative table ##################
       
    totals_distribs = pd.DataFrame(data = 
        # how this works:
        # outer loop: create a list - one item per totals column
        # inner loop: each list item is a dictionary of "number of trips" : "% of audience"
        # 0 trips has a different computation to 1-10 trips
        # resulting list of dictionaries is used to make a df
        [{number : len(totals[totals[col] >= number])/len(totals) if number else len(totals[totals[col] == number])/len(totals)
          for number in range(11)}
         for col in totals.columns],
        index = totals.columns)
    
    # rename columns to clarify 
    totals_distribs = totals_distribs.rename(columns = {col : str(col)+"+" for col in totals_distribs.columns[1:]})
    
    graph_data = totals_distribs.T
    all_trips = graph_data.iloc[:, -1] # All return trips
    breakdown_trips = graph_data.iloc[:, :-1] # Leisure, Business, Domestic, International
    
    
    # 3d ################## create bar chart of "All return trips" ##################

    # see appendix for construction details
    fig = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': '%{y:.0%} took %{x} return trips<extra></extra>',
              'legendgroup': '',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': all_trips.values,
              'textposition': 'outside',
              'texttemplate': '%{text:.0%}',
              'type': 'bar',
              'x': all_trips.index.values,
              'xaxis': 'x',
              'y': all_trips.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'relative',
                'legend': {'tracegroupgap': 0},
                'title': {'font': {'color': '#003865'}, 
                          'text': 'Return trips {}<br>All trips'.format(timeframe)},
                'xaxis': {'anchor': 'y',
                          'domain': [0.0, 1.0],
                          'title': {'text': 'Number of trips taken {}'.format(timeframe)}},
                'yaxis': {'anchor': 'x',
                          'domain': [0.0, 1.0],
                          'range': [0, 1.1],
                          'tickformat': '.0%',
                          'title': {'text': '% of Audience {}'.format(A_or_B)}
                          },
                'template': 'simple_white'
                }
        }
    

    # 3e ################## create bar chart of purpose/domain breakdowns ##################
    
    # see appendix for construction details
    fig_2 = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': '%{y:.0%} took %{x} leisure return trips<extra></extra>',
              'legendgroup': 'Leisure return trips',
              'marker': {'color': '#007DBA', 'pattern': {'shape': ''}},
              'name': 'Leisure return trips',
              'offsetgroup': 'Leisure return trips',
              'orientation': 'v',
              'showlegend': True,
              'textposition': 'auto',
              'type': 'bar',
              'x': breakdown_trips.index.values,
              'xaxis': 'x',
              'y': breakdown_trips.iloc[:,0].values,
              'yaxis': 'y'},
              {'alignmentgroup': 'True',
              'hovertemplate': '%{y:.0%} took %{x} business return trips<extra></extra>',
              'legendgroup': 'Business return trips',
              'marker': {'color': '#96172E', 'pattern': {'shape': ''}},
              'name': 'Business return trips',
              'offsetgroup': 'Business return trips',
              'orientation': 'v',
              'showlegend': True,
              'textposition': 'auto',
              'type': 'bar',
              'x': breakdown_trips.index.values,
              'xaxis': 'x',
              'y': breakdown_trips.iloc[:,1].values,
              'yaxis': 'y'},
              {'alignmentgroup': 'True',
              'hovertemplate': '%{y:.0%} took %{x} domestic return trips<extra></extra>',
              'legendgroup': 'Domestic return trips',
              'marker': {'color': '#218D7F', 'pattern': {'shape': ''}},
              'name': 'Domestic return trips',
              'offsetgroup': 'Domestic return trips',
              'orientation': 'v',
              'showlegend': True,
              'textposition': 'auto',
              'type': 'bar',
              'x': breakdown_trips.index.values,
              'xaxis': 'x',
              'y': breakdown_trips.iloc[:,2].values,
              'yaxis': 'y'},
              {'alignmentgroup': 'True',
              'hovertemplate': '%{y:.0%} took %{x} international return trips<extra></extra>',
              'legendgroup': 'International return trips',
              'marker': {'color': '#D64D6E', 'pattern': {'shape': ''}},
              'name': 'International return trips',
              'offsetgroup': 'International return trips',
              'orientation': 'v',
              'showlegend': True,
              'textposition': 'auto',
              'type': 'bar',
              'x': breakdown_trips.index.values,
              'xaxis': 'x',
              'y': breakdown_trips.iloc[:,3].values,
              'yaxis': 'y'
              }],
    'layout': {'barmode': 'group',
                'legend': {'bgcolor': 'rgba(0,0,0,0)',
                          'title': {'text': 'Trip type'},
                          'tracegroupgap': 0,
                          "yanchor" : "top",
                          "y" : 1,
                          "xanchor" : "right",
                          "x" : 1},
                'title': {'font': {'color': '#003865'}, 'text': 'Return trips {}<br>By trip type'.format(timeframe)},
                'xaxis': {'anchor': 'y',
                          'domain': [0.0, 1.0],
                          'showgrid': True,
                          'ticklen': 10,
                          'ticks': 'outside',
                          'tickson': 'boundaries',
                          'title': {'text': 'Number of trips taken {}'.format(timeframe)}},
                'yaxis': {'anchor': 'x',
                          'domain': [0.0, 1.0],
                          'range': [0, 1.1],
                          'tickformat': '.0%',
                          'title': {'text': '% of Audience {} members'.format(A_or_B)}
                          },
                'template': 'simple_white',
                }
    }
    

    # 4 ################## confirm how many outliers were removed ##################    
    
    footnote = dcc.Markdown("Note: {:,} outliers removed.".format(outliers_removed),
                            className = "text-primary",
                            style = {"paddingTop" : "25px"})
    

    return [markdown,
            table,
            dcc.Graph(figure = fig),
            dcc.Graph(figure = fig_2),
            footnote]



######################################## Q3

def ffp_and_breakdown(df, A_or_B, **kwargs):
    """
    # returns:
        - Pie chart confirming proportional breakdown of values listed in the given column of data
        
    # Notes:
        The "given column of data" contains binary data (Yes or No) indicating ffp member status.
        ffp stands for "frequent flyer programme"
    # kwargs:
        this function relies on the following dictionary:
            {"follow-up question" : "Q3B"}
            
        Q3B - breakdown of ffp membership tier - is shown as part of Q3.
    """
    
    ################## 1a compute Q3 values ##################
    
    # note: px.pie expects numeric data to group by a "names" column.
    # go.pie can be used to feed in labels and values instead.
    
    # get value counts of the one-column df
    Q3_values = df.iloc[:,0].value_counts()
    
    # ensure "Yes" is always listed first
    index = ["Yes",
             "No"]
    Q3_values = Q3_values.reindex(index)
    
    
    ################## 1b create Yes-No pie chart ##################
        
    # see appendix for construction details
    fig = {
    'data': [{'type': 'pie',
              'values': list(Q3_values),
              'marker': {'colors': ["#CE0058" if A_or_B == "A" else "#4B4F54",
                                    "white"], 
                         'line': {'color': '#000000', 
                                  'width': 2}
                         },
              "sort" : False, # ensures "Yes" is always first segment
              "direction" : "clockwise",
              'labels': Q3_values.index.values,
              'texttemplate': '%{label} (%{percent:.0%})',
              'hovertemplate': '%{percent:.0%} said %{label}<extra></extra>',
              'pull': 0.03,
              'showlegend': False,
              'textposition': 'inside'}],
    'layout': {'template': 'simple_white'}
    }

    
    ################## 1c fetch and compute Q3B column values ##################
    
    # fetch Q3B column
    Q3B_col = data.corresponding("Variable alias", kwargs["follow-up question"], "Column")[0]
    
    # use index of filtered df to look up corresponding Q3B values
    Q3B_values = data.get_data().loc[df.index, Q3B_col].value_counts().to_frame()

    # manipulate the Q3B_values dataframe for bar graph:
    
    # replace double quotation marks with single quotation marks    
    # replace " (e.g." with "<br>(e.g."
    Q3B_values.index = Q3B_values.index.str.replace("\"", "'", regex = True)
    Q3B_values.index = Q3B_values.index.str.replace(" (e.g.", "<br>(e.g.", regex = False)
    
    # we want the following fixed order:
    index = ["Base Tier",
             "I am in Base Tier having dropped from a higher tier since COVID",
             "One above Base Tier<br>(e.g. 'Silver')",
             "Two above Base Tier<br>(e.g. 'Gold')",
             "Three above Base Tier<br>(e.g. 'Platinum') or higher"]
    Q3B_values = Q3B_values.reindex(index)
    
    # create a 2nd column / data series that only contains the value for ...
    # "I am in base tier having dropped..." on the same row as "Base Tier" in 1st column
    Q3B_values[index[1]] = Q3B_values.index.map(lambda x: 
        Q3B_values.loc[Q3B_values.index == index[1], Q3B_values.columns[0]][0] if x == index[0] else np.nan)
    
    # we can now remove the "I am in base tier having dropped..." row
    Q3B_values = Q3B_values.loc[Q3B_values.index != index[1]]
        
    # create Totals column
    Q3B_values["Total"] = Q3B_values.sum(axis = 1)
    
    # convert all cells to %s (as a % of entire sample)
    Q3B_values = Q3B_values.applymap(lambda x: x / len(df))
    
    # add new column that is a formatted version of index (accessed via customdata)
    Q3B_values["index_formatted"] = Q3B_values.index.str.replace("Tier.*", "Tier",
                                                                 regex = True)
    Q3B_values["index_formatted"] = Q3B_values["index_formatted"].str.lower()
    

    ################## 1d create stacked bar chart of Q3B values ##################
    
    # Interesting note about customdata:
        # I originally passed the Q3B_values df and used customdata[3] to reference the 4th column
        # this works in Plotly with plot(fig_2)... but results in "Error loading layout..." in Dash
        # to overcome this, I instead passed the 4th column as a list.
        # it seems customdata is more fragile in Dash than in Plotly.
    
    # see appendix for construction details
    fig_2 = {
    'data': [{'alignmentgroup': 'True',
              'customdata': list(Q3B_values.iloc[:, -1]), # used for hovertemplate ("index_formatted")
              'hovertemplate': '%{x} are in %{customdata}<extra></extra>',
              'legendgroup': 'Q3B',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': 'Q3B',
              'offsetgroup': 'Q3B',
              'orientation': 'h',
              'showlegend': False,
              'text': ["{:.0%}".format(Q3B_values.iloc[0, 0])], # only want data label for first bar
              'textposition': 'inside',
              'type': 'bar',
              'x': Q3B_values.iloc[:, 0].values,
              'xaxis': 'x',
              'y': Q3B_values.index.values,
              'yaxis': 'y'},
             {'alignmentgroup': 'True',
              'hovertemplate': '%{x} have dropped into base tier following the COVID pandemic<extra></extra>',
              'legendgroup': 'I am in Base Tier having droppedfrom a higher tier since COVID',
              'marker': {'color': '#007DBA', 
                         'pattern': {'shape': ''}},
              'name': 'Dropped into Base Tier since the COVID pandemic', # rephrase legend entry for succinctness
              'offsetgroup': 'I am in Base Tier having dropped from a higher tier since COVID',
              'orientation': 'h',
              'showlegend': True,
              'text': ["{:.0%}".format(Q3B_values.iloc[0, 1])], # only want data label for first bar
              'textposition': 'inside', # if graph is downsized, prevents this label from overlapping with annotation
              'type': 'bar',
              'x': Q3B_values.iloc[:, 1].values,
              'xaxis': 'x',
              'y': Q3B_values.index.values,
              'yaxis': 'y'}],
    'layout': {'annotations': [{'showarrow': False, 
                                'text': "{:.0%}".format(total), 
                                'x': total + 0.02,
                                "xanchor" : "left", # if graph is downsized, annotation is kept to the right of bar
                                'y': label}
                               for total, label in zip(Q3B_values.iloc[:, 2], Q3B_values.index.values)],
               'barmode': 'relative',
               'legend': {'title': {'text': ''}, 
                          'tracegroupgap': 0,
                          "yanchor" : "top",
                          "y" : -0.25,
                          "xanchor" : "left",
                          "x" : -0.15},
               'title': {'font': {'color': '#003865'},
                         'text': "Highest tier of membership:<br>Breakdown of the {:.0%} that said yes".format(Q3_values[0]/len(df))},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range': [0, 1],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }

    return [dcc.Graph(figure = fig),
            dcc.Graph(figure = fig_2)]



######################################## Q4

def one_col_h_bar_plot(df, A_or_B, **kwargs):
    """
    # returns:
        - horizontal-orientated bar plot sorted by frequency in descending order.
        
    # Notes:
        This function is designed to be as generalisable as possible.
        Only one column of data is expected.
        The values will be ordered in descending order in the bar plot.
        A footnote is included if column length (after dropna) is less than passed df.
    # kwargs:
        {"cut-off" : int, # top n items to include only, by frequency
         "Others" : bool, # whether to remove 'Others'
         "q_id" : str} # makes known the question id 
    """
    
    ################## 1a confirm if column sample is less than length of filtered df ##################
    
    # confirm length of column
    # be sure to capture empty strings!
    col_length = len(df.iloc[:, 0].replace("^\s+$", np.nan, regex = True).dropna())
    
    # check if a footnote is needed:
    if col_length < len(df):
        footnote = [dcc.Markdown("Note: actual sample is {:,} ({:.0%}).".format(col_length, col_length/data.TOTAL_SAMPLE),
                    className = "text-primary",
                    # only include top padding for 1st footnote
                    style = {"paddingTop" : "25px"})
                    ]
    else:
        footnote = []

    
    ################## 1a compute value counts ##################
    
    # get value counts of the one-column df
    value_counts = df.iloc[:,0].value_counts()
    
    # process kwargs:
        
    try:
        # if user has specified exclusion of "Others":
        if not kwargs["Others"]:
            value_counts = value_counts.loc[value_counts.index != "Others"]    
    # if unspecified ignore
    except KeyError:
        pass
    
    try:
        # if user has specified a cut-off:
        if kwargs["cut-off"]:
            value_counts = value_counts.iloc[:kwargs["cut-off"]] 
    # if unspecified ignore
    except KeyError:
        pass
    
    # if a response option exceeds 40 chars in length, it needs wrapping:
    value_counts.index = [wrap_func(item, kwargs["q_id"]) for item in value_counts.index]    

    # identify question id
    # this should always be provided in kwargs for any question using this function
    q_id = kwargs["q_id"]
    
    # if this is Q4: 
    if q_id == "Q4":
        # exclude everything after airport name
        # note: it is either a whitespace char OR "<br>" - which may have been inserted by wrap_func
        customdata = list(value_counts.index.str.replace("(\s|<br>)\|.*", "", regex = True)) 
        
        # prepare customdata
        # note: customdata as a df object does not work in Dash - hence conversion to numpy array
        customdata = pd.DataFrame({"position" : [index+1 for index, label in enumerate(customdata)],
                                   "label" : [label for index, label in enumerate(customdata)]}).to_numpy()       
        
        # hovertemplate text:
        hovertemplate = '#%{customdata[0]}: %{customdata[1]} %{x:.1%}<extra></extra>'
       
        # include a title and word it based on how many airports are listed
        title = "Top {} departure airports".format(len(value_counts)) \
            if len(value_counts) > 1 else "Top departure airport"
    
    elif q_id == "Qxx":
        pass # no other question uses this function yet.
        
        
    # lastly, convert values into %s
    value_counts = value_counts.apply(lambda x: x / len(df))
    

    ################## 1b create bar chart ##################
            
    # there was no preliminary construction for this figure: 
    # it is based on the Q3 fig_2 figure
    fig = {
    'data': [{'alignmentgroup': 'True',
              'customdata': customdata, # used for hovertemplate
              'hovertemplate': hovertemplate,
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'h',
              'showlegend': False,
              'text': value_counts.values,
              "texttemplate" : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': value_counts.values,
              'xaxis': 'x',
              'y': value_counts.index.values,
              'yaxis': 'y'}],
    'layout': {'height' : 800, # default is 450. increase if labels are poorly spaced. Reference: https://stackoverflow.com/questions/46287189/how-can-i-change-the-size-of-my-dash-graph           
               'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': title},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1], 
                         'range': [0, 1.1], # just in case a 100% value is presented, data label is still visble
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {"autorange" : "reversed", # show labels in reversed order
                         'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'ticklen' : 10,
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }

    return [dcc.Graph(figure = fig)] + footnote



######################################## Q5 / Q6

def two_col_h_bar_plot(df, A_or_B, **kwargs):
    """
    # returns:
        - horizontal-orientated grouped bar plot with 2 data series/traces.
        
    # Notes:
        This function is designed to be as generalisable as possible.
        Exactly two columns of data are expected.
        Labels/values are ordered according to a fixed order, based on question id.
        A footnote is included per column if column length - after .dropna() - is less than passed df.
    # kwargs:
        {"q_id" : str} # question id, used to determine order of Labels/values.
    """
    
    ################## 1a confirm if either column sample is less than length of filtered df ##################
    
    # confirm length of both columns
    # be sure to capture empty strings!
    lengths = [len(df.iloc[:, 0].replace("^\s+$", np.nan, regex = True).dropna()),
               len(df.iloc[:, 1].replace("^\s+$", np.nan, regex = True).dropna())]
    
    # check if footnotes are needed:
    footnotes =  []
    # check if sample for column is smaller than length of df
    for ind, col_length in enumerate(lengths):
        if col_length < len(df):
            footnote = dcc.Markdown("**{}:** subsample of {:,}.".format(df.columns[ind],
                                                                        col_length),
                className = "text-primary",
                # only include top padding for 1st footnote
                style = {"paddingTop" : "25px"} if not footnotes else {})
            footnotes.append(footnote)


    ################## 1b compute value counts for both columns ##################

    # get value counts:   
    value_counts = df.apply(pd.Series.value_counts, axis = 0)

    # identify question id
    # this should always be provided in kwargs for any question using this function
    q_id = kwargs["q_id"]
    
    # if this is Q5: 
    if q_id == "Q5":
        # establish fixed order of labels:
        index = ["First class",
                "Business class",
                "Premium economy",
                "Economy",
                "Low-cost/Budget airline"]
        value_counts = value_counts.reindex(index)
        
        # create hovertemplate
        col1_or_col2 = ["when they pay", "when their business pays"]
        hovertemplate = "%{x:.0%} travel %{y} "
        
        # no markdown is created for Q5
        markdown = []
        
    # if this is Q6: 
    if q_id == "Q6":
        # establish fixed order of labels:
        index = ["Less than 30 minutes",
                 "30 minutes - 1 hour",
                 "1 - 2 hours",
                 "2 - 3 hours",
                 "3 - 4 hours",
                 "More than 4 hours"]
        value_counts = value_counts.reindex(index)
        
        # create hovertemplate
        col1_or_col2 = ["domestically", "internationally"]
        hovertemplate = "%{x:.0%} arrive with %{y} before travelling "
                
        # markdown: we also want to compute averages using sumproduct
        midvalues = [30*0.8,
                     (30+60)/2,
                     (60+120)/2,
                     (120+180)/2,
                     (180+240)/2,
                     240*1.2]
        #NOTE: np.nansum() treats nans as zeros (nans may be present in small samples). sum() returns nan and thus is not used.
        col_aves = [np.nansum([x * y for x, y in zip(midvalues, value_counts[col])]) / np.nansum(value_counts[col])
                    for col in value_counts.columns]
        
        color_decider = lambda: "text-danger" if A_or_B == "A" else "text-secondary"
        markdown = [dcc.Markdown("##### Dwell time averages:", className = "text-primary")] + \
                   [dcc.Markdown("##### **{}:** {:.0f} minutes".format(col, ave),
                                 # this syntax is a bit unwieldy:
                                 # if first column, decide if text-danger or text-secondary is used, else text-info
                                 className = color_decider() if col == value_counts.columns[0] else "text-info")
                    for col, ave in zip(value_counts.columns, col_aves)]

            
    # lastly, convert values into %s
    # this is worked out per column, based on the count of non-nans in that column
    value_counts.iloc[:,0] = value_counts.iloc[:,0].apply(lambda x: x / lengths[0])
    value_counts.iloc[:,1] = value_counts.iloc[:,1].apply(lambda x: x / lengths[1])
    
    # marker color decider function
    def color(ind):
        # if this is the first data series/trace
        if ind == 0:
            # confirm if it should be Audience A color or Audience B color
            return "#CE0058" if A_or_B == "A" else "#4B4F54"
        else:
            # return Collinson light blue
            return "#007DBA"
        
    ################## 1c create grouped bar chart ##################
            
    # there was no preliminary construction for this figure: 
    # it is based on the Q3 fig_2 figure
    fig = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': hovertemplate + "{}<extra></extra>".format(col1_or_col2[ind]),
              'marker': {'color': color(ind), # use above function to decide color
                         "opacity" : 0.5 if ind == 1 else 1, # make 2nd series less prominent
                         'pattern': {'shape': ''}},
              'name': col,
              'offsetgroup': col,
              'orientation': 'h',
              'showlegend': True,
              'text': value_counts[col].values, # data labels
              "texttemplate" : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': value_counts[col].values, # values
              'xaxis': 'x',
              'y': value_counts.index.values, # labels
              'yaxis': 'y'}
             for ind, col in enumerate(value_counts.columns)],
    'layout': {'barmode': 'group',
               'legend': {'orientation' : 'h',
                          'xanchor' : 'center',
                          'x' : 0.5,
                          'yanchor' : 'bottom',
                          'y' : 1.1},
               'title': {'font': {'color': '#003865'}},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1], 
                         'range': [0, 1.1], # just in case a 100% value is presented, data label is still visble
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {"autorange" : "reversed", # show labels in reversed order
                         'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }
    
        
    return markdown + [dcc.Graph(figure = fig)] + footnotes



######################################## Q7

def airport_sentiment(df, A_or_B, **kwargs):
    """
    # returns:
        - vertical-orientated bar plot with fixed order.
        
    # Notes:
        This function is designed for the "Airport experience sentiment" question.
        Only one column of data is expected.
        The values will be ordered in a fixed order in the bar plot.
    # kwargs:
        {} # none needed
    """
    
    ################## 1a confirm if column sample is less than length of filtered df ##################
    
    # confirm length of column
    # be sure to capture empty strings!
    col_length = len(df.iloc[:, 0].replace("^\s+$", np.nan, regex = True).dropna())
    
    # check if a footnote is needed:
    if col_length < len(df):
        footnote = [dcc.Markdown("Note: actual sample is {:,} ({:.0%}).".format(col_length, col_length/data.TOTAL_SAMPLE),
                    className = "text-primary",
                    # only include top padding for 1st footnote
                    style = {"paddingTop" : "25px"})
                    ]
    else:
        footnote = []

    
    ################## 1b compute value counts ##################
    
    # get value counts of the one-column df
    value_counts = df.iloc[:,0].value_counts()
    
    # establish fixed order of labels:
    value_counts.index = value_counts.index.map(str)
    index = ["1 - The airport is something I have to tolerate to get to my destination",
             "2",
             "3",
             "4",
             "5 - The airport is an enjoyable part of the journey"]
    value_counts = value_counts.reindex(index)
    
    # text is too long for x-axis labels so remove.
    # graph footnote is included explaining what a score equal to 1 and 5 represent
    value_counts.index = value_counts.index.str.replace("\D", "", regex = True)
    
    # markdown: we also want to compute average score using sumproduct
    scores = [1,
              2,
              3,
              4,
              5]
    ave_score = np.nansum([x * y for x, y in zip(scores, value_counts.values)]) / np.nansum(value_counts.values)        
    net_positive = np.nansum(value_counts.iloc[-2:].values) / col_length
    markdown = [html.Div([dcc.Markdown("##### Average score (out of 5): ", 
                                       className = "text-primary"),
                          dcc.Markdown("##### &nbsp;{:.2f}".format(ave_score), 
                                       className = "text-danger" if A_or_B == "A" else "text-secondary")],
                         style = {"display" : "flex",
                                  "flexWrap" : "wrap"}),
                
                html.Div([dcc.Markdown("##### Positive score (4-5 out of 5): ", 
                                       className = "text-primary"),
                          dcc.Markdown("##### &nbsp;{:.0%}".format(net_positive), 
                                       className = "text-danger" if A_or_B == "A" else "text-secondary")],
                         style = {"display" : "flex",
                                  "flexWrap" : "wrap"})
                ]
                
    # prepare customdata
    customdata = scores
    
    # lastly, convert values into %s
    value_counts = value_counts.apply(lambda x: x / col_length)
    

    ################## 1c create bar chart ##################
            
    # there was no preliminary construction for this figure: 
    # it is based on the Q3 fig_2 figure
    fig = {
    'data': [{'alignmentgroup': 'True',
              'customdata': customdata, # used for hovertemplate
              'hovertemplate': '%{y} score their departure airport experience %{customdata} out of 5<extra></extra>',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': value_counts.values,
              "texttemplate" : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': value_counts.index.values,
              'xaxis': 'x',
              'y': value_counts.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': ''},
               'xaxis': {'anchor': 'y',
                        'domain': [0.0, 1.0],
                        'autotypenumbers' : 'strict', # stops numerical string values being interpreted as numbers
                         'title': {'text': ''},
                         "automargin" : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'range': [0.0, 1.1], # just in case a 100% value is presented, data label is still visble
                         'tickformat': '.0%',
                         'title': {'text' : '% of Audience {}'.format(A_or_B)},
                         "automargin" : True,
                         },
               'template': 'simple_white'
               }
    }
    
    graph_footnote = [dcc.Markdown("1 = 'The airport is something I have to tolerate to get to my destination'"),
                      dcc.Markdown("5 = 'The airport is an enjoyable part of the journey'")]
    
    return markdown + [dcc.Graph(figure = fig)] + graph_footnote + footnote



######################################## Q8

def airport_voucher_spend(df, A_or_B, **kwargs):
    """
    # returns:
        - 3 vertical-orientated bar plots.
        - order is based on descending order of plot 1 y-axis values.
        
    # Notes:
        This function is designed for the "Airport voucher spend" question.
    # kwargs:
        {} # none needed
    """
    
    ################## prelim: wrap x-axis labels ##################
    
    # The below was commented out because it caused more problems than it tried to solve.
    
    # def wrap_text(text):
    #     # find a space and a letter - replace with html newline syntax
    #     # we obviously don't want to replace the letter - so keep that!
    #     return re.sub("\s([a-zA-Z])", "<br>" + r"\1", text)
        
    # df.columns = [wrap_text(col) for col in df.columns]
    
    
    ################## 1a compute % that opted to spend on each service ##################
    
    # compute % that gave a spend (any value above zero)
    spend_perc = df.apply(lambda x: len(x[x > 0]), axis = 0)
    
    # sort in descending order and use the resulting index for plots 2 and 3
    spend_perc = spend_perc.sort_values(ascending = False)

    # customdata: make available the positional order of each service post-sorting
    # must convert to numpy array for Dash
    customdata = pd.DataFrame({"position" : [pos+1 for pos, label in enumerate(spend_perc.index)],
                               "label" : [label for pos, label in enumerate(spend_perc.index)]}).to_numpy()       
   
    # I want to use plot 1 x-axis order for plots 2 and 3 for data readability
    plot1_index = spend_perc.index
        
    # lastly, convert values into %s
    spend_perc = spend_perc.apply(lambda x: x / len(df))


    ################## 1b create "% interested" bar chart ##################
            
    # there was no preliminary construction for this figure: 
    # it is based on the Q3 fig_2 figure
    fig = {
    'data': [{'alignmentgroup': 'True',
              'customdata' : customdata,
              'hovertemplate': '<b>#%{customdata[0]}: %{y:.0%}</b> would spend something on <b>%{x}</b><extra></extra>',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': spend_perc.values,
              "texttemplate" : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': spend_perc.index.values,
              'xaxis': 'x',
              'y': spend_perc.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': '% of Audience {} passengers<br>that would spend something'.format(A_or_B)},
               'xaxis': {'anchor': 'y',
                        'domain': [0.0, 1.0],
                        'autotypenumbers' : 'strict', # stops numerical string values being interpreted as numbers
                         'title': {'text': ''},
                         "automargin" : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'range': [0.0, 1.1], # just in case a 100% value is presented, data label is still visble
                         'tickformat': '.0%',
                         'title': {'text' : ''},
                         "automargin" : True,
                         },
               'template': 'simple_white'
               }
    }
    
    
    ################## 2a compute median spend on each service ##################
    
    # compute median spend (of non-zero values only)
    spend_med = df.apply(lambda x: x[x > 0].median(), axis = 0)
    
    # sort in descending order (used for customdata)
    spend_med = spend_med.sort_values(ascending = False)

    # customdata: make available the positional order of each service post-sorting
    # must convert to numpy array for Dash
    customdata = pd.DataFrame(data = {"position" : [pos+1 for pos, label in enumerate(spend_med.index)]},
                              index = [label for pos, label in enumerate(spend_med.index)])    
   
    # I want to use plot 1 x-axis order for plots 2 and 3 for data readability
    spend_med = spend_med.reindex(plot1_index)
    customdata = customdata.reindex(plot1_index)
    
    # also make available the y-axis value of plot 1
    customdata["plot 1 y-axis value"] = customdata.index.map(spend_perc.to_dict())
    customdata = customdata.to_numpy()
       
    
    ################## 2b create "median spend" bar chart ##################

    fig_2 = {
    'data': [{'alignmentgroup': 'True',
              'customdata' : customdata,
              'hovertemplate': """<b>#%{customdata[0]}:</b> the <b>%{customdata[1]:.0%}</b> that would spend something on <b>%{x}</b><br>
would typically spend <b>$%{y:.0f}</b><extra></extra>""",
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': spend_med.values,
              "texttemplate" : "$%{text:.0f}",
              'textposition': 'outside',
              'type': 'bar',
              'x': spend_med.index.values,
              'xaxis': 'x',
              'y': spend_med.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': 'Median spend by Audience {} passengers'.format(A_or_B)},
               'xaxis': {'anchor': 'y',
                        'domain': [0.0, 1.0],
                        'autotypenumbers' : 'strict', # stops numerical string values being interpreted as numbers
                         'title': {'text': ''},
                         "automargin" : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'range': [0.0, 220], # US dollar value of voucher in question
                         'tickprefix' : '$', # tick prefix
                         'tickformat': '.0f',
                         'title': {'text' : ''},
                         "automargin" : True,
                         },
               'template': 'simple_white'
               }
    }
    
    
    ################## 3a compute spend per passenger on each service ##################
    
    # compute median spend (of non-zero values only)
    spend_ave = df.apply(lambda x: x.mean(), axis = 0)
    
    # sort in descending order (used for customdata)
    spend_ave = spend_ave.sort_values(ascending = False)

    # customdata: make available the positional order of each service post-sorting
    # must convert to numpy array for Dash
    customdata = pd.DataFrame(data = {"position" : [pos+1 for pos, label in enumerate(spend_ave.index)]},
                              index = [label for pos, label in enumerate(spend_ave.index)])    
   
    # I want to use plot 1 x-axis order for plots 2 and 3 for data readability
    spend_ave = spend_ave.reindex(plot1_index)
    customdata = customdata.reindex(plot1_index)
    
    # also make available the proportional share of revenue
    customdata["share of spend"] = customdata.index.map(lambda x: spend_ave.loc[x] / spend_ave.sum())
    customdata_fig_4 = customdata # used for pie chart
    customdata = customdata.to_numpy()
    
    
    ################## 3b create "spend per passenger" bar chart ##################
    
    fig_3 = {
    'data': [{'alignmentgroup': 'True',
              'customdata' : customdata,
              'hovertemplate': """<b>#%{customdata[0]}:</b> <b>$%{y:.0f}</b> per $220 voucher was spent on <b>%{x}</b><br>
This represents <b>%{customdata[1]:.0%}</b> of revenue generated across these 10 services<extra></extra>""",
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': spend_ave.values,
              "texttemplate" : "$%{text:.0f}",
              'textposition': 'outside',
              'type': 'bar',
              'x': spend_ave.index.values,
              'xaxis': 'x',
              'y': spend_ave.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': 'Expected spend per Audience {} passenger'.format(A_or_B)},
               'xaxis': {'anchor': 'y',
                        'domain': [0.0, 1.0],
                        'autotypenumbers' : 'strict', # stops numerical string values being interpreted as numbers
                         'title': {'text': ''},
                         "automargin" : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'range': [0.0, 220], # US dollar value of voucher in question
                         'tickprefix' : '$', # tick prefix
                         'tickformat': '.0f',
                         'title': {'text' : ''},
                         "automargin" : True,
                         },
               'template': 'simple_white'
               }
    }
    
    
    ################## 4a make "revenue breakdown" pie chart ##################
        
    # this pie chart is based on Q3
    fig_4 = {
    'data': [{'type': 'pie',
              'values': customdata_fig_4["share of spend"].values,
              'marker': {'colors': ["#CE0058"]*10 if A_or_B == "A" else ["#4B4F54"]*10, # must be a list of colors for each segment
                         'line': {'color': '#000000', 
                                  'width': 2}
                         },
              "sort" : True, # ensures "Yes" is always first segment
              "direction" : "clockwise",
              'labels': customdata_fig_4.index.values,
              'texttemplate': '%{label}<br>%{percent:.0%}',
              'hovertemplate': '%{label}<br>%{percent:.0%} share of the revenue generated across these services<extra></extra>',
              'pull': 0.03,
              'showlegend': False,
              'textposition': 'inside'}],
    'layout': {'title' : {'font': {'color': '#003865'},
                          'text' : 'Share of generated revenue'},
               'template': 'simple_white'}
    }

    
    return [dcc.Graph(figure = fig),
            dcc.Graph(figure = fig_2),
            dcc.Graph(figure = fig_3),
            dcc.Graph(figure = fig_4)]



######################################## Q9 / Q19

def horizontal_total_order_plot(df, A_or_B, **kwargs):
    """
    # returns:
        - 1 horizontally-orientated bar plot with different groups plotted in total ascending order.
        - bars are patterned & colored according to different categories/groups
        - This is used e.g. for the retail spend incentives question. Distinct groups/categories of
        response options are plotted but they are ordered as a collective in the plot.
        
    # Notes:
        This function is designed to be as generalisable as possible.
        Markdown is created to show category averages.
    # kwargs:
        {'q_id' : string} # this function is multi-question, thus need to know question id
    """

    ################## 1a question-dependent processing ##################
        
    if kwargs["q_id"] == "Q9":
        
        Q9_values = df.apply(pd.Series.value_counts, axis = 0)
        Q9_values.index = Q9_values.index.astype(str) # important to convert all values to string
        Q9_values.loc["Positive score"] = Q9_values.apply(lambda x: x[x.index.str.contains("4|5")].sum(),
                                                          axis = 0)
        
        # take only "Positive score" column, transpose and sort
        # values should NOT be sorted / the plot sorts them
        Q9_values = Q9_values.iloc[-1, :].T
        
        # present as percentages
        values = Q9_values.apply(lambda x: x / len(df))
        
        # create mapping of category : item / pattern / color / hovertemplate / customdata
        # note: first is plotted at bottom of stack
        cat_details = {}
        hovertemplate = '<b>%{x}</b> say <b>%{y}</b> is an important consideration<extra></extra>'
        
        cat_details["Logistics"] = [range(6),
                                    "/",
                                    "#CE0058" if A_or_B == "A" else "#4B4F54",
                                    hovertemplate,
                                    []] # customdata: none needed for this question
        cat_details["Experience"] = [range(6,11),
                                     "x",
                                     "#FF4997" if A_or_B == "A" else "#90959C",
                                     hovertemplate,
                                     []] # customdata: none needed for this question
        cat_details["Incentives"] = [range(11,17),
                                     "\\",
                                     "#FFC2DC" if A_or_B == "A" else "#DADCDE",
                                     hovertemplate,
                                     []] # customdata: none needed for this question
        # plot height for Q9
        plot_height = 600
    
    if kwargs["q_id"] == "Q19":
        
        Q19_values = df.apply(pd.Series.value_counts, axis = 0)
        
        # rename "None of the above" as "None of these options would encourage me"
        Q19_values = Q19_values.rename(columns = {"None of the above" : "None of these options would encourage me"})
        
        # isolate "Selected":
        # ensure "Selected" is always last so below index always works
        index = ["Not selected",
                 "Selected"]
        Q19_values = Q19_values.reindex(index)
        Q19_values = Q19_values.loc[Q19_values.index[-1]].T
        
        # present as percentages
        values = Q19_values.apply(lambda x: x / len(df))
        
        
        # create mapping of category : item / pattern / color / hovertemplate / customdata
        # note: first is plotted at bottom of stack
        cat_details = {}
        hovertemplate = '<b>%{x}</b> would spend more <b>"%{y}"</b><extra></extra>'
        
        # order items alphabetically, and then they can be indexed in a fixed manner
        values = values.sort_index()
        # for x,y in enumerate(items):
            # print(x,y)
        
        cat_details["Rewards"] = [[0,1],
                                    "/",
                                    "#67002C" if A_or_B == "A" else "#26272A",
                                    '<b>%{x}</b> would spend more with the <b>"%{y}"</b><extra></extra>']
        cat_details["Price comparisons"] = [[4,5,6],
                                     "x",
                                     "#CE0058" if A_or_B == "A" else "#4B4F54",
                                     hovertemplate]
        cat_details["Offers"] = [[12,13],
                                     "\\",
                                     "#FF4997" if A_or_B == "A" else "#90959C",
                                     '<b>%{x}</b> would spend more with <b>"%{y}"</b><extra></extra>'] 
        cat_details["Deliver/collect services"] = [[7,8,10],
                                    ".",
                                    "#FFC2DC" if A_or_B == "A" else "#DADCDE",
                                    hovertemplate]
        cat_details["Planning assistance"] = [[3,9],
                                     "+",
                                     "#FFD1E5" if A_or_B == "A" else "#E5E6E7",
                                     hovertemplate]
        cat_details["Uncorrelated - personal assistant"] = [[2],
                                     "",
                                     "white" if A_or_B == "A" else "white",
                                     '<b>%{x}</b> would spend more with <b>"%{y}"</b><br>(Uncorrelated response option)<extra></extra>']
        cat_details["Uncorrelated"] = [[11],
                                     "",
                                     "white" if A_or_B == "A" else "white",
                                     '<b>%{x}</b> are uninterested in spending more<br>(Exclusive response option)</b><extra></extra>']
       
        # plot height for Q19
        plot_height = 850
    
    ################## 1b create markdown: category averages ##################
    
    #compute category averages, and order by average
    # excluded "Uncorrelated" category for Q19!
    cat_aves = {k : values.iloc[v[0]].mean() for k, v in cat_details.items() if "Uncorrelated" not in k}
    cat_aves = {k : v for k, v in sorted(cat_aves.items(), key = lambda x: x[1], reverse = True)} # note: order is not viewable in Spyder's variable explorer
    
    # create markdown
    markdown = [html.Div([dcc.Markdown("##### {}".format(cat), 
                                   className = "text-danger" if A_or_B == "A" else "text-secondary"),
                      dcc.Markdown("&nbsp;{:.0%}".format(cat_aves[cat]), 
                                   className = "text-danger" if A_or_B == "A" else "text-secondary")],
                     style = {"display" : "flex",
                              "flexWrap" : "wrap"})
                for cat in cat_aves]
    
    
    ################## 1c question-independent checks and preparation ##################
               
    # remove " (e.g. ...)" from question items (if any)
    values.index = values.index.str.replace("\s\(e.g..*\)", "", regex = True)
    
    # if a question item exceeds 40 chars in length, it needs wrapping:
    # use pre-wrapped index as customdata
    customdata = pd.Series(values.index)
    # use post-wrapped index as index / y-axis values
    values.index = [wrap_func(item) for item in values.index]
    
    # color "None of these options would encourage me" with red
    if kwargs["q_id"] == "Q19":
        values = values.rename(index = {"None of these options would encourage me" : \
                                        color("red", 'None of these options would encourage me')})
                               
    
    ################## 1d create stacked bar chart of Q3B values ##################
    
    # figure is based on Q3 figure
    fig = {
    'data': [{'customdata' : customdata.iloc[cat_details[cat][0]].values,
              'alignmentgroup': 'True',
              'hovertemplate': cat_details[cat][3],
              'legendgroup': cat,
              'marker': {'color': cat_details[cat][2], 
                           'pattern': {'shape': cat_details[cat][1],
                                       'fgopacity' : 1},
                           'line' : {'color' : "black",
                                     'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'h',
              'showlegend': True if "Uncorrelated" not in cat else False,
              'text': values.iloc[cat_details[cat][0]].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': values.iloc[cat_details[cat][0]].values,
              'xaxis': 'x',
              'y': values.iloc[cat_details[cat][0]].index.values,
              'yaxis': 'y'}
             for cat in cat_details],
    'layout': {'barmode': 'overlay', # means items of each group is positioned in line with x-axis value
               'height' : plot_height, # default is 450. increase if labels are poorly spaced. Reference: https://stackoverflow.com/questions/46287189/how-can-i-change-the-size-of-my-dash-graph           
               'bargap' : 0.5,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "left",
                          "x" : 0.0},
               'title': {'font': {'color': '#003865'},
                         'text': ""},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range': [0, 1.19],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {'categoryorder' : 'total ascending', # sort bars indepdently of cateogry / trace
                         'ticks' : 'outside',
                         'ticklen' : 10,
                         'tickmode' : 'linear', # ensure all labels are shown                         
                         'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }

    return markdown + [dcc.Graph(figure = fig)]



######################################## Q10

def airport_satisfaction(df, A_or_B, **kwargs):
    """
    # returns:
        - 1 horizontally-orientated bar plot.
        - bars are patterned according to 4 categories:
            1. Arrival - security checks
            2. Departure waiting area
            3. Facilities
            4. Pre-boarding
        
    # Notes:
        This function is designed for the "Departure airport satisfaction" question.
    # kwargs:
        {} # none needed
    """

    ################## prelim: abbreviate long items ##################
    
    df = df.rename(columns = {"Availability of retail shopping delivery service (e.g. to home or destination)" : "Availability of retail shopping delivery service",
                              "Ability to pre-order shopping (e.g. access to 24-hour click & collect)" : "Ability to pre-order shopping"})
    
    Q10_values = df.apply(pd.Series.value_counts, axis = 0)
    Q10_values.index = Q10_values.index.astype(str) # important to convert all values to string
    
    
    ################## 1a compute Q10 positive score % (4-5 out of 5) ##################
   
    Q10_values.loc["Positive score"] = Q10_values.apply(lambda x: x[x.index.str.contains("4|5")].sum(),
                                                      axis = 0)
    
    # take only "Positive score" column, transpose and sort
    sat_Q10_values = Q10_values.iloc[-1, :].T.sort_values(ascending = False)
    
    # present as percentages
    sat_Q10_values = sat_Q10_values.apply(lambda x: x / len(df))
    
    # create mapping of category : item 
    cat_items = {}
    items = list(df.columns)
    cat_items["Arrival - security checks"] = items[:5]
    cat_items["Departure waiting area"] = items[5:11]
    cat_items["Facilities"] = items[11:19]
    cat_items["Pre-boarding"] = items[19:] 
    
    # create mapping of category : bar pattern
    cat_pattern = {}
    cat_pattern["Arrival - security checks"] = ["\\", "#67002C" if A_or_B == "A" else "#26272A"]
    cat_pattern["Departure waiting area"] = ["x", "#CE0058" if A_or_B == "A" else "#4B4F54"]
    cat_pattern["Facilities"] = [".", "#FF4997" if A_or_B == "A" else "#90959C"]
    cat_pattern["Pre-boarding"] = ["/", "#FFC2DC" if A_or_B == "A" else "#DADCDE"]
        
    
    ################## 1b create markdown: category averages ##################
    
    #compute category averages (note: unlike Q9, we don't want to keep same order)
    cat_aves = {k : sat_Q10_values.loc[v].mean() for k, v in cat_items.items()}
    
    # create markdown
    sat_markdown = [html.Div([dcc.Markdown("##### {}".format(cat), 
                                   className = "text-danger" if A_or_B == "A" else "text-secondary"),
                      dcc.Markdown("&nbsp; average: {:.0%}".format(cat_aves[cat]), 
                                   className = "text-danger" if A_or_B == "A" else "text-secondary")],
                     style = {"display" : "flex",
                              "flexWrap" : "wrap"})
                for cat in cat_aves]
         
    # create and prepend title markdown      
    title_markdown = html.Div([dcc.Markdown("### Passenger satisfaction (4-5 out of 5):")],
                                            className = "text-primary",
                                            style = {"text-align" : "center"})
    sat_markdown.insert(0, title_markdown)
               
    
    ################## 1c create figure with 4 legend entries ##################
    
    # figure is based on Q3 figure
    fig = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': '<b>%{x}</b> are satisfied with <b>%{y}</b><extra></extra>',
              'legendgroup': cat,
              'marker': {'color': cat_pattern[cat][1], 
                           'pattern': {'shape': cat_pattern[cat][0],
                                       'fgopacity' : 1},
                           'line' : {'color' : cat_pattern[cat][1],
                                     'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'h',
              'showlegend': True,
              'text': sat_Q10_values.loc[cat_items[cat]].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': sat_Q10_values.loc[cat_items[cat]].values,
              'xaxis': 'x',
              'y': sat_Q10_values.loc[cat_items[cat]].index.values,
              'yaxis': 'y'}
             for cat in cat_items],
    'layout': {'barmode': 'overlay', # means items of each group is positioned in line with x-axis value
               'height' : 750, # default is 450. increase if labels are poorly spaced. Reference: https://stackoverflow.com/questions/46287189/how-can-i-change-the-size-of-my-dash-graph           
               'bargap' : 0.5,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "left",
                          "x" : 0.0},
               'title': {'font': {'color': '#003865'},
                         'text': ""},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range': [0, 1.19],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {'categoryorder' : 'total ascending', # sort bars indepdently of cateogry / trace
                         'ticks' : 'outside',
                         'ticklen' : 10,
                         'tickmode' : 'linear', # ensure all labels are shown
                         'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }


    ################## 2a REPEAT for Q10 negative score % (1-2 out of 5) ##################
        
    Q10_values.loc["Negative score"] = Q10_values.apply(lambda x: x[x.index.str.contains("1|2")].sum(),
                                                        axis = 0)
    
    # take only "Negative score" column, transpose and sort
    dis_Q10_values = Q10_values.iloc[-1, :].T.sort_values(ascending = False)
    
    # present as percentages
    dis_Q10_values = dis_Q10_values.apply(lambda x: x / len(df))
    
    # create mapping of category : item 
    cat_items = {}
    items = list(df.columns)
    cat_items["Arrival - security checks"] = items[:5]
    cat_items["Departure waiting area"] = items[5:11]
    cat_items["Facilities"] = items[11:19]
    cat_items["Pre-boarding"] = items[19:] 
    
    # create mapping of category : bar pattern
    cat_pattern = {}
    cat_pattern["Arrival - security checks"] = ["\\", "#67002C" if A_or_B == "A" else "#26272A"]
    cat_pattern["Departure waiting area"] = ["x", "#CE0058" if A_or_B == "A" else "#4B4F54"]
    cat_pattern["Facilities"] = [".", "#FF4997" if A_or_B == "A" else "#90959C"]
    cat_pattern["Pre-boarding"] = ["/", "#FFC2DC" if A_or_B == "A" else "#DADCDE"]
        
    
    ################## 2b create markdown: category averages ##################
    
    #compute category averages (note: unlike Q9, we don't want to keep same order)
    cat_aves = {k : dis_Q10_values.loc[v].mean() for k, v in cat_items.items()}
    
    # create markdown
    dis_markdown = [html.Div([dcc.Markdown("##### {}".format(cat), 
                                   className = "text-danger" if A_or_B == "A" else "text-secondary"),
                      dcc.Markdown("&nbsp; average: {:.0%}".format(cat_aves[cat]), 
                                   className = "text-danger" if A_or_B == "A" else "text-secondary")],
                     style = {"display" : "flex",
                              "flexWrap" : "wrap"})
                for cat in cat_aves]
         
    # create and prepend title markdown      
    title_markdown = html.Div([dcc.Markdown("### Passenger dissatisfaction (1-2 out of 5):")],
                                            className = "text-primary",
                                            style = {"text-align" : "center"})
    dis_markdown.insert(0, title_markdown)
               
    
    ################## 2c create figure with 4 legend entries ##################
    
    # figure is based on Q3 figure
    fig_2 = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': '<b>%{x}</b> are dissatisfied with <b>%{y}</b><extra></extra>',
              'legendgroup': cat,
              'marker': {'color': cat_pattern[cat][1], 
                           'pattern': {'shape': cat_pattern[cat][0],
                                       'fgopacity' : 1},
                           'line' : {'color' : cat_pattern[cat][1],
                                     'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'h',
              'showlegend': True,
              'text': dis_Q10_values.loc[cat_items[cat]].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': dis_Q10_values.loc[cat_items[cat]].values,
              'xaxis': 'x',
              'y': dis_Q10_values.loc[cat_items[cat]].index.values,
              'yaxis': 'y'}
             for cat in cat_items],
    'layout': {'barmode': 'overlay', # means items of each group is positioned in line with x-axis value
               'height' : 750, # default is 450. increase if labels are poorly spaced. Reference: https://stackoverflow.com/questions/46287189/how-can-i-change-the-size-of-my-dash-graph
               'bargap' : 0.5,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "left",
                          "x" : 0.0},
               'title': {'font': {'color': '#003865'},
                         'text': ""},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range': [0, 1.19],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {'categoryorder' : 'total descending', # sort bars indepdently of cateogry / trace
                         'ticks' : 'outside',
                         'ticklen' : 10,
                         'tickmode' : 'linear', # ensure all labels are shown
                         'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }


    return sat_markdown + [dcc.Graph(figure = fig)] + dis_markdown + [dcc.Graph(figure = fig_2)]



######################################## Q11

def airport_services(df, A_or_B, **kwargs):
    """
    # returns:
        - 3 vertical-orientated bar plots.
        - order is based on descending order of plot 1 y-axis values.
        
    # Notes:
        This function is designed for the "Airport voucher spend" question.
    # kwargs:
        {} # none needed
    """   
    
    ################## prelim: compute value counts ##################    
    
    # compute value_counts
    value_counts = df.apply(pd.Series.value_counts, axis = 0)

    
    ################## 1a compute % that are "possibly" + "likely" to use each service ##################
    
    value_counts.loc["interested"] = value_counts.apply(lambda x: x[x.index.str.contains("3|4|5|6")].sum(),
                                                        axis = 0)
    
    # take only "Interest counts" column, transpose and sort
    interested_perc = value_counts.iloc[-1, :].T.sort_values(ascending = False)
    
    # sort in descending order and use the resulting index for plots 2 and 3
    interested_perc = interested_perc.sort_values(ascending = False)

    # customdata: make available the positional order of each service post-sorting
    # must convert to numpy array for Dash
    customdata = pd.DataFrame({"position" : [pos+1 for pos, label in enumerate(interested_perc.index)],
                               "label" : [label for pos, label in enumerate(interested_perc.index)]}).to_numpy()       
   
    # I want to use plot 1 x-axis order for plots 2 and 3 for data readability
    plot1_index = interested_perc.index
        
    # lastly, convert values into %s
    interested_perc = interested_perc.apply(lambda x: x / len(df))


    ################## 1b create "% interested" bar chart ##################
            
    # this figure is based on Q8 "fig"
    fig = {
    'data': [{'alignmentgroup': 'True',
              'customdata' : customdata,
              'hovertemplate': '<b>#%{customdata[0]}: %{y:.0%}</b> are interested in <b>%{x}</b><extra></extra>',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': interested_perc.values,
              "texttemplate" : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': interested_perc.index.values,
              'xaxis': 'x',
              'y': interested_perc.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': 'Audience {} passengers that<br>"would possibly" or "be likely to"<br>use this service'.format(A_or_B)},
               'xaxis': {'anchor': 'y',
                        'domain': [0.0, 1.0],
                        'autotypenumbers' : 'strict', # stops numerical string values being interpreted as numbers
                         'title': {'text': ''},
                         "automargin" : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'range': [0.0, 1.1], # just in case a 100% value is presented, data label is still visble
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)},
                         "automargin" : True,
                         },
               'template': 'simple_white'
               }
    }

    
    ################## 2a compute breakdown of 'likielihood' response counts ##################
    
    # compute counts for: possibly and interested (not at all interested and unlikely counts are already done)
    value_counts.loc["Possibly"] = value_counts.apply(lambda x: x[x.index.str.contains("3|4")].sum(),
                                                      axis = 0)
    
    value_counts.loc["Likely"] = value_counts.apply(lambda x: x[x.index.str.contains("5|6")].sum(),
                                                    axis = 0)
    
    # isolate the 4 'likelihood' groups and transpose
    likelihood_groups = value_counts.loc[value_counts.index[[0,1,-2,-1]]].T
    
    # remove numbers from response option text
    likelihood_groups = likelihood_groups.rename(columns = {"1 - Not at all interested" : "Not at all interested",
                                                            "2 - Unlikely" : "Unlikely"})
    
       
    # use plot 1 x-axis order for plots 2 and 3
    likelihood_groups = likelihood_groups.reindex(plot1_index)

    # create mapping of likelihood group : bar color / hovertemplate
    cat_details = {}
    cat_details["Not at all interested"] = ["#67002C" if A_or_B == "A" else "#26272A",
                                            '<b>%{y:.0%}</b> are <b>not at all interested</b> in using <b>%{x}</b><extra></extra>']
    cat_details["Unlikely"] = ["#CE0058" if A_or_B == "A" else "#4B4F54",
                               '<b>%{y:.0%}</b> are <b>unlikely</b> to use <b>%{x}</b><extra></extra>']
    cat_details["Possibly"] = ["#FF4997" if A_or_B == "A" else "#90959C",
                               '<b>%{y:.0%}</b> <b>would possibly</b> use <b>%{x}</b><extra></extra>']
    cat_details["Likely"] = ["#FFC2DC" if A_or_B == "A" else "#DADCDE",
                             '<b>%{y:.0%}</b> are <b>likely</b> to use <b>%{x}</b><extra></extra>']
 
    # express values as %s
    likelihood_groups = likelihood_groups.applymap(lambda x: x / len(df))
    
    
    ################## 2b create "likelihood breakdown" bar chart ##################

    # figure is loosely based on Q10 "fig"
    fig_2 = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': cat_details[cat][1],
              'legendgroup': cat,
              'marker': {'color': cat_details[cat][0],
                         'line' : {'color' : "#000000",
                                   'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'v',
              'showlegend': True,
              'text': likelihood_groups[cat].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'inside',
              'type': 'bar',
              'x': likelihood_groups[cat].index.values,
              'xaxis': 'x',
              'y': likelihood_groups[cat].values,
              'yaxis': 'y'}
             for cat in cat_details],
    'layout': {'barmode': 'relative',
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0},
               'title': {'font': {'color': '#003865'},
                         'text': "Breakdown of likelihood"},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'automargin' : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)},
                         'automargin' : True
                         }, 
               'template': 'simple_white'
               }
    }

    
    ################## 3a compute breakdown of 'booking preference' response counts ##################
    
    # compute counts for: "on the day" and "in advance"
    value_counts.loc["On the day"] = value_counts.apply(lambda x: x[x.index.str.contains("3|5")].sum(),
                                                        axis = 0)
    
    value_counts.loc["In advance"] = value_counts.apply(lambda x: x[x.index.str.contains("4|6")].sum(),
                                                    axis = 0)
    
    # isolate the 2 'booking preference' groups and transpose
    booking_groups = value_counts.loc[value_counts.index[-2:]].T
           
    # use plot 1 x-axis order for plots 2 and 3
    booking_groups = booking_groups.reindex(plot1_index)

    # create mapping of likelihood group : bar color / hovertemplate
    cat_details = {}
    cat_details["On the day"] = "#67002C" if A_or_B == "A" else "#26272A"
    cat_details["In advance"] = "#FFC2DC" if A_or_B == "A" else "#DADCDE"
    
    # express values as a ratio of one another:
    booking_groups["Sum"] = booking_groups.sum(axis = 1)
    for col in booking_groups.columns[:2]:
        booking_groups[col] = booking_groups[col] / booking_groups["Sum"]
    
    # drop sum column
    booking_groups = booking_groups.drop("Sum", axis = 1)
    
    
    ################## 3b create "likelihood breakdown" bar chart ##################

    # figure is loosely based on Q10 "fig"
    fig_3 = {
    'data': [{'alignmentgroup': 'True',
              'hovertemplate': '<b>%{y:.0%}</b> would prefer to book <b>%{x}</b>' + ' {}<extra></extra>'.format(cat.lower()),
              'legendgroup': cat,
              'marker': {'color': cat_details[cat],
                         'line' : {'color' : "#000000",
                                   'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'v',
              'showlegend': True,
              'text': booking_groups[cat].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'inside',
              'type': 'bar',
              'x': booking_groups[cat].index.values,
              'xaxis': 'x',
              'y': booking_groups[cat].values,
              'yaxis': 'y'}
             for cat in cat_details],
    'layout': {'barmode': 'relative',
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0},
               'title': {'font': {'color': '#003865'},
                         'text': "Booking preference ratio"},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'automargin' : True # stops x-axis labels being cut-off
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)},
                         'automargin' : True
                         },
               'template': 'simple_white'
               }
    }

    
    return [dcc.Graph(figure = fig),
            dcc.Graph(figure = fig_2),
            dcc.Graph(figure = fig_3)]



######################################## Q12 / Q17 / Q18 / Q20

def horizontal_stacked_plot(df, A_or_B, **kwargs):
    """
    # returns:
        - horizontally-orientated bar plot.
        - multiple bar trace(s) (i.e. data columns) are expected.
        - 'barmode' : 'relative'.
        
    # Notes:
        This function is designed to be as generalisable as possible.
    # kwargs:
        {'q_id' : string} # this function is multi-question, thus need to know question id
    """   
    
    ################## prelim: compute value counts ##################    
    
    # compute value_counts
    value_counts = df.apply(pd.Series.value_counts, axis = 0)
    
    # check if a footnote is needed:
    # we can use any one column to confirm length
    length = len(df.iloc[:, 0].replace("^\s+$", np.nan, regex = True).dropna())

    footnote =  []
    if length < len(df):
        note = dcc.Markdown("Note: actual sample is {:,} ({:.0%}).".format(length, length/data.TOTAL_SAMPLE),
                            className = "text-primary",
                            style = {"paddingTop" : "25px"})
        footnote.append(note)    
    

    ################## 1a prepare response_groups depending on question ##################
    
    # this section is question-dependent:
    
    if kwargs["q_id"] == "Q12":
        
        # compute counts for: worsen and improve
        value_counts.loc["Worsen"] = value_counts.apply(lambda x: x[x.index.str.contains("1|2")].sum(),
                                                          axis = 0)
        
        value_counts.loc["Improve"] = value_counts.apply(lambda x: x[x.index.str.contains("4|5")].sum(),
                                                        axis = 0)
        
        # isolate the 3 response groups/categories and transpose:
        # worsen, unsure, improve
        response_groups = value_counts.loc[value_counts.index[[-2,2,-1]]].T
        
        # order by improve (ascending will be flipped into descending when plotted)        
        response_groups = response_groups.sort_values("Improve", ascending = True)

        
        # create mapping of group/category : bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["Improve"] = ["#67002C" if A_or_B == "A" else "#26272A",
                                  '<b>%{x:.0%}</b> said <b>"%{y}"</b> would <b>improve</b> their experience<extra></extra>',
                                  []] # customdata: none needed for this question
        cat_details["Not sure"] = ["#FFFFFF",
                                   '<b>%{x:.0%}</b> are unsure about <b>"%{y}"</b><extra></extra>',
                                   []] # customdata: none needed for this question
        cat_details["Worsen"] = ["#FFC2DC" if A_or_B == "A" else "#DADCDE",
                                 '<b>%{x:.0%}</b> said <b>"%{y}"</b> would <b>worsen</b> their experience<extra></extra>',
                                 []] # customdata: none needed for this question
        
        # no need for text coloring / customdata for Q12
        color_text = False
        customdata = []
    
    
    if kwargs["q_id"] == "Q17":
        
        # remove empty value from index (represents respondents that did not answer this question)
        value_counts = value_counts.loc[value_counts.index.str.contains("[a-zA-Z]+", regex = True)]
        
        # compute counts for: worsen and improve
        value_counts.loc["Disagree"] = value_counts.apply(lambda x: x[x.index.str.contains("1|2")].sum(),
                                                          axis = 0)
        
        value_counts.loc["Agree"] = value_counts.apply(lambda x: x[x.index.str.contains("4|5")].sum(),
                                                        axis = 0)
        
        # isolate the 3 response groups/categories and transpose:
        # Disagree, Neutral, Agree
        response_groups = value_counts.loc[value_counts.index[[-2,2,-1]]].T
        
        # order by Agree (ascending will be flipped into descending when plotted)        
        response_groups = response_groups.sort_values("Agree", ascending = True)
        
        
        # create mapping of group/category : bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["Agree"] = ["#67002C" if A_or_B == "A" else "#26272A",
                                '<b>%{x:.0%}</b> agreed that <b>"%{customdata}"</b><extra></extra>']
                                # customdata is created below
        # note: this is how Neutral looks after regex is applied below
        cat_details["Neutral"] = ["#FFFFFF",
                                  '<b>%{x:.0%}</b> are undecided whether <b>"%{customdata}"</b><extra></extra>']
                                  # customdata is created below
        cat_details["Disagree"] = ["#FFC2DC" if A_or_B == "A" else "#DADCDE",
                                   '<b>%{x:.0%}</b> disagreed that <b>"%{customdata}"</b><extra></extra>']
                                   # customdata is created below
        
        # text coloring / customdata required for Q17
        # note: this is how these texts look after wrap_func is applied below
        color_text = True
        neg_responses = ["Communications from the airport(s) are not<br>of any value to me",
                         "The airport(s) are sent too<br>late to be of benefit/interest",
                         "Communications are sent at times when I<br>am not planning to travel",
                         "The airport(s) offer me discounts but<br>I have to spend too much<br>in order to take advantage of them"]


    if kwargs["q_id"] == "Q18":
        
        # isolate the 3 response groups/categories and transpose:
        # worsen, unsure, improve
        response_groups = value_counts.T
        
        # order by improve (ascending will be flipped into descending when plotted)        
        response_groups = response_groups.sort_values("More", ascending = True)

        
        # create mapping of group/category : bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["More"] = ["#67002C" if A_or_B == "A" else "#26272A",
                                  '<b>%{x:.0%}</b> need <b>more</b> information on <b>"%{y}"</b><extra></extra>',
                                  []] # customdata: none needed for this question
        cat_details["Unchanged"] = ["#FFFFFF",
                                   '<b>%{x:.0%}</b> do not need any change to information on <b>"%{y}"</b><extra></extra>',
                                   []] # customdata: none needed for this question
        cat_details["Less"] = ["#FFC2DC" if A_or_B == "A" else "#DADCDE",
                                 '<b>%{x:.0%}</b> want <b>less</b> information on <b>"%{y}"</b><extra></extra>',
                                 []] # customdata: none needed for this question
        
        # no need for text coloring / customdata for Q18
        color_text = False
        customdata = []
    
    
    if kwargs["q_id"] == "Q20":
        
        # remove empty value from index (represents respondents that did not answer this question)
        value_counts = value_counts.loc[value_counts.index.str.contains("[a-zA-Z]+", regex = True)]
        
        # compute counts for: worsen and improve
        value_counts.loc["Disagree"] = value_counts.apply(lambda x: x[x.index.str.contains("1|2")].sum(),
                                                          axis = 0)
        
        value_counts.loc["Agree"] = value_counts.apply(lambda x: x[x.index.str.contains("4|5")].sum(),
                                                        axis = 0)
        
        # isolate the 3 response groups/categories and transpose:
        # Disagree, Neutral, Agree
        response_groups = value_counts.loc[value_counts.index[[-2,2,-1]]].T
        
        # order by Agree (ascending will be flipped into descending when plotted)        
        response_groups = response_groups.sort_values("Agree", ascending = True)
        
        
        # create mapping of group/category : bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["Agree"] = ["#67002C" if A_or_B == "A" else "#26272A",
                                '<b>%{x:.0%}</b> agreed <b>"%{y}"</b><extra></extra>']
                                # customdata is created below
        # note: this is how Neutral looks after regex is applied below
        cat_details["Neutral"] = ["#FFFFFF",
                                  '<b>%{x:.0%}</b> are undecided whether <b>"%{y}"</b><extra></extra>']
                                  # customdata is created below
        cat_details["Disagree"] = ["#FFC2DC" if A_or_B == "A" else "#DADCDE",
                                   '<b>%{x:.0%}</b> disagreed <b>"%{y}"</b><extra></extra>']
                                   # customdata is created below

        # no need for text coloring / customdata for Q12
        color_text = False
        customdata = []    


    ################## 1b question-independent checks and preparation ##################
       
    # remove any non-letter chars + whitespace at the start of response option text (if any)
    response_groups.columns = [re.sub("^[^a-zA-Z]+\s([a-zA-Z].*)", r"\1", col)
                               for col in response_groups.columns]
        
    # remove " (e.g. ...)" from question items (if any)
    response_groups.index = response_groups.index.str.replace("\s\(e.g..*\)", "", regex = True)
    
    # if a question item exceeds 40 chars in length, it needs wrapping:
    response_groups.index = [wrap_func(item) for item in response_groups.index]    
     
    # express values as %s (divide by actual sample size rather than filtered df)
    response_groups = response_groups.applymap(lambda x: x / length)
     
    
    # Does this question require coloring?
    # Refer to color function at top of script
    # Source: https://stackoverflow.com/questions/58183962/how-to-color-ticktext-in-plotly
    if color_text:
        response_groups = response_groups.reset_index() # keep index to use as customdata for hover text!
        customdata = list(response_groups["index"].values)
        response_groups.index = [color("red" if text in neg_responses else "green", text) 
                                 for text in list(response_groups["index"])]


    ################## 1c create horizontally-stacked bar chart ##################

    # figure is loosely based on Q10 "fig"
    fig = {
    'data': [{'customdata' : customdata,
              'alignmentgroup': 'True',
              'hovertemplate': cat_details[cat][1],
              'legendgroup': cat,
              'marker': {'color': cat_details[cat][0],
                         'line' : {'color' : "#000000",
                                   'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'h',
              'showlegend': True,
              'text': response_groups[cat].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'inside',
              'insidetextanchor' : 'middle',
              'type': 'bar',
              'x': response_groups[cat].values,
              'xaxis': 'x',
              'y': response_groups[cat].index.values,
              'yaxis': 'y'}
             for cat in cat_details],
    'layout': {'height' : 600,
               'barmode': 'relative',
               'showlegend' : True,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0},
               'title': {'font': {'color': '#003865'},
                         'text': ""},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range' : [0.0, 1.0],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)},
                         'automargin' : True 
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'automargin' : True, # stops y-axis labels being cut-off
                         'ticklen' : 10
                         }, 
               'template': 'simple_white'
               }
    }

    return [dcc.Graph(figure = fig)] + footnote



######################################## Q13 / Q14 / Q15 / Q16

def horizontal_grouped_plot(df, A_or_B, **kwargs):
    """
    # returns:
        - horizontally-orientated bar plot.
        - This function is designed for a singular column of data, which needs to be split
        into multiple groups. There is no total descending/ascending order of the bars - instead,
        groups are plotted in the order they are passed as data traces.
        - For example, an exclusive response option can be positioned as the last bar / passed as 
        a seperate data trace altogether.
        - 'barmode' : 'overlay'.
        
    # Notes:
        This function is designed to be as generalisable as possible.
    # kwargs:
        {'q_id' : string, # this function is multi-question, thus need to know question id
         'text clusters' : 'Q15 clusters'} # column containing Q15 clusters in Prepared data (only used for Q15) 
    """   
    
    ################## prelim: compute value counts ##################    
    
    # Q15 needs its own prelim work:
    if kwargs["q_id"] == "Q15":
        
        # fetch text clusters column:
        clusters_col = data.corresponding("Variable alias", kwargs["text clusters"], "Column")[0]
        
        # use index of filtered df to look up corresponding 'Q15 clusters' values
        clusters = data.get_data().loc[df.index, clusters_col]
        
        # compute value counts
        value_counts = clusters.value_counts()
        
    # prelim work for all other questions:
    else:
        
        # compute value_counts
        value_counts = df.apply(pd.Series.value_counts, axis = 0)
                   
        # remove " (e.g. ...)" from question items (if any)
        value_counts.columns = [re.sub("\s\(e.g..*\)", "", col) for col in value_counts.columns]
        
        # if a question item exceeds 40 chars in length, it needs wrapping:
        value_counts.columns = [wrap_func(col) for col in value_counts.columns]     
    
        # For development only: notify if question item / column text exceeds 40 chars:
        # for col in value_counts.columns:
        #     if len(col) > 40: print(col)

    ################## 1a prepare response_groups depending on question ##################
    
    # this section is question-dependent:
    
    if kwargs["q_id"] == "Q13":
        
        # isolate "Selected":
        # ensure "Selected" is always last so below index always works
        index = ["Not selected",
                 "Selected"]
        value_counts = value_counts.reindex(index)
        value_counts = value_counts.loc[value_counts.index[-1]].T
        
        # order by improve (ascending will be flipped into descending when plotted)        
        value_counts = value_counts.sort_values(ascending = True)

        # ensure the following item is last in the plot (top in value_counts):
        # "None - I do not want to arrive earlier"
        reindex = list(value_counts.index)
        reindex.remove("None - I do not want to arrive earlier")
        reindex.insert(0, "None - I do not want to arrive earlier")
        value_counts = value_counts.reindex(reindex)       

        # create mapping of group : items / bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["None_item"] = [list(value_counts.index[0:1]), # slice syntax returns iterable
                                    "whitesmoke",
                                   '<b>%{x:.0%}</b> do not want to increase their dwell time</b><extra></extra>',
                                   []] # customdata: none needed for this question
        cat_details["main_items"] = [list(value_counts.index[1:]),
                                     "#CE0058" if A_or_B == "A" else "#4B4F54",
                                     '<b>%{x:.0%}</b> would arrive earlier for <b>%{y}</b><extra></extra>',
                                     []] # customdata: none needed for this question
    
    
    if kwargs["q_id"] == "Q14":
        # isolate "Selected":
        # ensure "Selected" is always last so below index always works
        index = ["Not selected",
                 "Selected"]
        value_counts = value_counts.reindex(index)
        value_counts = value_counts.loc[value_counts.index[-1]].T
        
        # order by improve (ascending will be flipped into descending when plotted)        
        value_counts = value_counts.sort_values(ascending = True)

        # ensure the following item is last in the plot (top in value_counts):
        # "None - I do not want to arrive earlier"
        # also: remove "Others (please specify)"
        reindex = list(value_counts.index)
        reindex.remove("None – I am not interested")
        reindex.insert(0, "None – I am not interested")
        reindex.remove("Others (please specify)")
        value_counts = value_counts.reindex(reindex)       

        # create mapping of group : items / bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["None_item"] = [list(value_counts.index[0:1]), # slice syntax returns iterable
                                    "whitesmoke",
                                   '<b>%{x:.0%}</b> are uninterested in entertainment options</b><extra></extra>',
                                   []] # customdata: none needed for this question
        cat_details["main_items"] = [list(value_counts.index[1:]),
                                     "#CE0058" if A_or_B == "A" else "#4B4F54",
                                     '<b>%{x:.0%}</b> would enjoy <b>%{y}</b><extra></extra>',
                                     []] # customdata: none needed for this question        
    
    
    if kwargs["q_id"] == "Q15":

        # order by improve (ascending will be flipped into descending when plotted)        
        value_counts = value_counts.sort_values(ascending = True)

        # ensure the following items are last in the plot (top in value_counts):
        # "Miscellaneous / Idiosyncratic"
        # "Disengaged travellers"
        reindex = list(value_counts.index)
        reindex.remove("Miscellaneous / Idiosyncratic")
        reindex.insert(0, "Miscellaneous / Idiosyncratic")
        reindex.remove("Disengaged travellers")
        reindex.insert(0, "Disengaged travellers")
        value_counts = value_counts.reindex(reindex)       

        # create mapping of group : items / bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["Disengaged"] = [list(value_counts.index[0:1]), # slice syntax returns iterable
                                    "whitesmoke",
                                   '<b>%{x:.0%}</b> expressed disengagement with this conversation</b><extra></extra>',
                                   []] # customdata: none needed for this question
        
        cat_details["Misc"] = [list(value_counts.index[1:2]), # slice syntax returns iterable
                                    "whitesmoke",
                                   'Most passengers <b>(%{x:.0%})</b> expressed non-generalisable, idiosyncractic desires</b><extra></extra>',
                                   []] # customdata: none needed for this question
        
        cat_details["main_items"] = [list(value_counts.index[2:]),
                                     "#CE0058" if A_or_B == "A" else "#4B4F54",
                                     '<b>%{x:.0%}</b> most want to see <b>%{y}</b><extra></extra>',
                                     []] # customdata: none needed for this question        
   
 
    if kwargs["q_id"] == "Q16":
        # isolate "Selected":
        # ensure "Selected" is always last so below index always works
        index = ["Not selected",
                 "Selected"]
        value_counts = value_counts.reindex(index)
        value_counts = value_counts.loc[value_counts.index[-1]].T
        
        # order by Selected (ascending will be flipped into descending when plotted)        
        value_counts = value_counts.sort_values(ascending = True)

        # ensure the following item is last in the plot (top in value_counts):
        # "I do not want a<br>relationship with the airport"
        # "I do not interact with<br>the airports in anyway
        neg_responses = ["I do not want a<br>relationship with the airport",
                         "I do not interact with<br>the airports in anyway"]
        reindex = list(value_counts.index)
        for x in neg_responses:
            reindex.remove(x)
            reindex.insert(0, x)
        value_counts = value_counts.reindex(reindex)       

        # I want to distinguish between 'negative' and 'positive/neutral' response options
        # Refer to color function at top of script
        # Source: https://stackoverflow.com/questions/58183962/how-to-color-ticktext-in-plotly
        value_counts = value_counts.reset_index() # keep index to use as customdata for hover text!
        value_counts.index = [color("red" if text in neg_responses else "black", text) 
                              for text in list(value_counts["index"])]
        
        # create mapping of group : items / bar color / hovertemplate
        # note: first is plotted at bottom of stack
        cat_details = {}
        cat_details["no_interaction_item"] = [list(value_counts.index[0:1]), # slice syntax returns iterable
                                              "whitesmoke",
                                              '<b>%{x:.0%}</b> do not interact with airports</b><extra></extra>',
                                              list(value_counts["index"][0:1])]
        cat_details["do_not_want_item"] = [list(value_counts.index[1:2]), # slice syntax returns iterable
                                           "#CE0058" if A_or_B == "A" else "#4B4F54",
                                           '<b>%{x:.0%}</b> do not want a relationship with airports</b><extra></extra>',
                                           list(value_counts["index"][1:2])]
        cat_details["main_items"] = [list(value_counts.index[2:]),
                                     "#CE0058" if A_or_B == "A" else "#4B4F54",
                                     '<b>%{x:.0%}</b> said <b>"%{customdata}"</b><extra></extra>',
                                     list(value_counts["index"][2:])]     
        
        # drop old index column / convert back to Series
        value_counts = value_counts.iloc[:,-1]

    # express values as %s
    value_counts = value_counts.apply(lambda x: x / len(df))
    
    
    ################## 1c create horizontally-stacked bar chart ##################

    # figure is loosely based on Q10 "fig"
    fig = {
    'data': [{'alignmentgroup': 'True',
              'customdata' : cat_details[cat][3], 
              'hovertemplate': cat_details[cat][2],
              'legendgroup': cat,
              'marker': {'color': cat_details[cat][1],
                         'line' : {'color' : "#000000",
                                   'width' : 1}
                         },
              'name': cat,
              'offsetgroup': cat,
              'orientation': 'h',
              'showlegend': True,
              'text': value_counts.loc[cat_details[cat][0]].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'outside',
              'insidetextanchor' : 'end',
              'type': 'bar',
              'x': value_counts.loc[cat_details[cat][0]].values,
              'xaxis': 'x',
              'y': value_counts.loc[cat_details[cat][0]].index.values,
              'yaxis': 'y'}
             for cat in cat_details],
    'layout': {'barmode': 'overlay', # means items of each group is positioned in line with x-axis value
               'height' : 600,
               'showlegend' : False,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0},
               'title': {'font': {'color': '#003865'},
                         'text': ""},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range' : [0.0, 1.0],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)},
                         'automargin' : True 
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'automargin' : True, # stops y-axis labels being cut-off
                         'ticklen' : 10,
                         #'ticktext' : value_counts.index.values,
                         }, 
               'template': 'simple_white'
               }
    }

    return [dcc.Graph(figure = fig)]



######################################## Q21 / Q22

def pie_chart_and_breakdown(df, A_or_B, **kwargs):
    """
    # returns:
        - Pie chart confirming proportional breakdown of overarching response themes
        - Horizontal bar chart confirming breakdown of a specific response theme
    # Notes:
        - This function is designed to be as generalisable as possible
    # kwargs:
            {'q_id' : string} # question id is needed
    """
    
    ################## prelim: compute initial breakdown of values ##################
    
    # get value counts of the multi-column df
    values = df.apply(pd.Series.value_counts, axis = 0)


    ################## 1a question dependent preparation ##################

    if kwargs["q_id"] == "Q21":

        # ensure "Selected is always listed last
        index = ["Not selected",
                 "Selected"]
        values = values.reindex(index)
        values = values.loc[values.index[-1]].T
    
        # convert to %s
        values = values.apply(lambda x: x / len(df))

        # compute % of respondents that selected any of the "Replace some" question items
        # isolate the 4 "replace some" columns > access row values and confirm if "Selected" is present > sum up rows where "Selected" is present > divided by len(df)
        values.loc["Replace some retail space"] = df[[c for c in df.columns if "Replace some" in c]].apply(lambda row: 1 if "Selected" in row.values else 0,
                                                                                                           axis = 1).sum() / len(df)
        
        # compute % of responses that ONLY selected "Space for retail outlets should be increased"
        # we can work this out as follows: 100 - ("Replace some retail space" + "I am indifferent")
        # this is because "I am indifferent was an exclusive response". Thus, the remainder must be
        # people that ONLY selected "Space for retail outlets should be increased".
        values.loc["Increase retail space only"] = 1 - (values.loc["Replace some retail space"] + \
                                                        values.loc["I am indifferent"])
    
        
        # prepare pie chart:
        # overarching response themes
        pie_values = values.loc[["Replace some retail space",
                                 "I am indifferent",
                                 "Increase retail space only"]]
        
        pie_hovertemplate = '%{percent:.0%} said <b>"%{label}"</b><extra></extra>'
        pie_colors = ["#CE0058" if A_or_B == "A" else "#4B4F54",
                      "#218D7F",
                      "white"]
        
    
        # prepare bar chart:
        # breakdown of "Replace some" theme
        bar_values = values.loc[values.index.str.contains("Replace some with")].sort_values(ascending = True)
        bar_values.index = bar_values.index.str.replace("Replace some with ", "", regex = False)         
        
        bar_hovertemplate = '%{x:.0%} want <b>"%{customdata}"</b><extra></extra>'
        bar_title = "Breakdown: Replace some retail space with..."


    if kwargs["q_id"] == "Q22":
        
        # convert to %s
        values = values.apply(lambda x: x / len(df))
        # convert to Series
        values = values.iloc[:,0]
        
        # compute % of respondents that said it is an "inconvenience"
        values.loc["It is an inconvenience"] = values.loc[values.index.str.contains("inconvenience")].sum()  
        
        # prepare pie chart:
        # overarching response themes
        #NOTE: reindex is used instead of .loc (see: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#deprecate-loc-reindex-listlike)
        pie_values = values.reindex(["It is an enjoyable experience",
                                     "I am indifferent",
                                     "It is an inconvenience",
                                     "I have not experienced this at an airport"])
        
        pie_hovertemplate = '%{percent:.0%} said <b>"%{label}"</b><extra></extra>'
        pie_colors = ["#218D7F",
                      "white",
                      "#CE0058" if A_or_B == "A" else "#4B4F54",
                      "black"]
        
    
        # prepare bar chart:
        # breakdown of "Replace some" theme
        bar_values = values.loc[values.index.str.contains("inconvenience")].sort_values(ascending = True)
        bar_values = bar_values.drop("It is an inconvenience")         
        
        bar_hovertemplate = '%{x:.0%} said <b>"%{customdata}"</b><extra></extra>'
        bar_title = "Breakdown: It is an inconvenience..."
    
    ################## 1b question independent preparation ##################

    # if a question item exceeds 40 chars in length, it needs wrapping:
    bar_customdata = bar_values.index
    bar_values.index = [wrap_func(col) for col in bar_values.index] 
    
    
    ################## 1c create pie chart of pie_values ##################
    
    # figure is based on Q3 pie chart
    fig = {
    'data': [{'type': 'pie',
              'values': pie_values.values,
              'marker': {'colors': pie_colors, 
                         'line': {'color': '#000000', 
                                  'width': 2}
                         },
              "sort" : False, # ensures fixed order
              "direction" : "clockwise",
              'labels': pie_values.index.values,
              'texttemplate': '%{percent:.0%}',
              'hovertemplate': pie_hovertemplate,
              'pull': 0.03,
              'showlegend': True,
              'textposition': 'inside'}],
    'layout': {'template': 'simple_white',
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0}
               }
    }


    ################## 1d create bar chart of bar_values ##################
    
    # figure is based on Q3 bar chart
    fig_2 = {
    'data': [{'type': 'bar',
              'customdata' : bar_customdata.values,
              'alignmentgroup': 'True',
              'hovertemplate' : bar_hovertemplate,
              'legendgroup': 'Q3B',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'h',
              'showlegend': False,
              'x': bar_values.values,
              'xaxis': 'x',
              'y': bar_values.index.values,
              'yaxis': 'y',
              'text': bar_values.values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'outside'}],
    'layout': {'barmode': 'group',
               'title': {'font': {'color': '#003865'},
                         'text': bar_title},
               'xaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range': [0, 1],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'yaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'title': {},
                         'ticklen' : 10,
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }

    return [dcc.Graph(figure = fig),
            dcc.Graph(figure = fig_2)]



######################################## Q23 / Q24 / Market / Gender

def generic_pie_chart(df, A_or_B, **kwargs):
    """
    # returns:
        - Pie chart confirming proportional breakdown of response options
    # Notes:
        - This function is designed to be as generalisable as possible
    # kwargs:
            {'q_id' : string} # question id is needed
    """
    
    ################## prelim: compute initial breakdown of values ##################
    
    # get value counts of the multi-column df
    values = df.apply(pd.Series.value_counts, axis = 0)
    
    # convert to %s
    pie_values = values.apply(lambda x: x / len(df))
    
    # convert to Series
    pie_values = pie_values.iloc[:,0]
    
    # if a question item exceeds 40 chars in length, it needs wrapping:
    pie_customdata = pie_values.copy() # important to create a new version otherwise pie_customdata will be changed when pie_values is changed
    pie_values.index = [wrap_func(col) for col in pie_values.index] 


    ################## 1a question dependent preparation ##################

    if kwargs["q_id"] == "Q23":
        
        # swap original labels for abbreviated labels
        pie_customdata = pie_customdata.rename(index = 
                                                {"Sit down in-restaurant dining" : "Dining",
                                                "Eat in public seating areas<br>of the airport" : "Seating areas",
                                                "Eat in an airport lounge" : "Lounge",
                                                "Eat on the go" : "On the go",
                                                "Purchase food to take on the airplane" : "Airplane",
                                                "None of the above" : "None"})
        
        pie_hovertemplate = '%{percent:.0%} said <b>"%{label}"</b><extra></extra>'
        pie_colors = ["#CE0058" if A_or_B == "A" else "#4B4F54"]*6
        # "None of the above" color will equal black
        pie_colors[pie_values.index.to_list().index("None of the above")] = "white"
        
        sort = True
        table = []
        
    if kwargs["q_id"] == "Q24":
        
        # keep fixed order: "Yes" always first
        pie_values = pie_values.reindex(["Yes", "No"])
        
        pie_hovertemplate = '%{percent:.0%} said <b>"%{label}"</b><extra></extra>'
        pie_colors = ["#CE0058" if A_or_B == "A" else "#4B4F54",
                      "white"]
        
        sort = False
        table = []
    
    if kwargs["q_id"] == "Market":
        
        # swap original labels for abbreviated labels
        pie_customdata = pie_customdata.rename(index = 
                                                {"China" : "CN",
                                                "USA" : "US",
                                                "Russia" : "RU",
                                                "Spain" : "ES",
                                                "France" : "FR",
                                                "Brazil" : "BR",
                                                "UK" : "UK",
                                                "Italy" : "IT",
                                                "Hong Kong" : "HK",
                                                "Singapore" : "SG"})
        
        pie_hovertemplate = '%{percent:.0%} of Audience A reside in <b>"%{label}"</b><extra></extra>'
        pie_colors = ["#CE0058" if A_or_B == "A" else "#4B4F54"]*10
        
        sort = True
        
        # for market, also create a table of countries sorted A-Z:
        table_values = pie_values.sort_index().reset_index()
        table_values.columns = ["Country", "Share (%)"]
        table_values["Share (%)"] = table_values["Share (%)"].apply(lambda x: "{:.0%}".format(x))
        
        table = dbc.Table.from_dataframe(table_values, bordered = True, hover = True,
                                         style = {"color" : "#CE0058" if A_or_B == "A" else "#4B4F54"})

    if kwargs["q_id"] == "Gender":
        
        # for gender, also create a table of genders sorted A-Z:
        table_values = pie_values.sort_index().reset_index()
        table_values.columns = ["Gender", "Share (%)"]
        table_values["Share (%)"] = table_values["Share (%)"].apply(lambda x: "{:.0%}".format(x)
                                                                    if "{:.0%}".format(x) != "0%"
                                                                    else "{:.2%}".format(x))
        
        table = dbc.Table.from_dataframe(table_values, bordered = True, hover = True,
                                         style = {"color" : "#CE0058" if A_or_B == "A" else "#4B4F54"})

        
        # for the pie chart, merge "Self-describe" and "Prefer not to answer"
        # WARNING: we cannot assume "Self-describe" or "Prefer not to answer" are present in the index:
        other_responses = [x for x in ["Self-describe", "Prefer not to answer"] if x in pie_values.index]

        # "Other" is only created if "Self-describe" and/or "Prefer not to answer" exist
        if other_responses: pie_values.loc["Other"] = sum([pie_values.loc[response] for response in other_responses])
        pie_values.drop(index = other_responses, inplace = True)
        
        # for Gender, there is no difference between pie_values and pie_customdata. So we can simply copy changes made to pie_values.
        pie_customdata = pie_values
        
        pie_hovertemplate = '%{percent:.0%} of Audience A identify as <b>"%{label}"</b><extra></extra>'
        pie_colors = ["#CE0058" if A_or_B == "A" else "#4B4F54"]*10
        
        sort = True
        
        

    # make sure customdata is a list of the labels
    pie_customdata = pie_customdata.index.to_list()
    
    
    ################## 1c create pie chart of pie_values ##################
    
    # figure is based on Q3 pie chart
    fig = {
    'data': [{'type': 'pie',
              'customdata' : pie_customdata,
              'values': pie_values.values,
              'marker': {'colors': pie_colors, 
                         'line': {'color': '#000000', 
                                  'width': 2}
                         },
              "sort" : sort,
              "direction" : "clockwise",
              'labels': pie_values.index.values,
              'texttemplate': '%{customdata} (%{percent:.0%})',
              'hovertemplate': pie_hovertemplate,
              'pull': 0.05,
              'showlegend': False,
              'textposition': 'inside'}],
    'layout': {'template': 'simple_white'}
    }

    return [dcc.Graph(figure = fig)] + [table]



######################################## Q25

def f_and_b_services(df, A_or_B, **kwargs):
    """
    # returns:
        - 2 vertically-orientated bar plots showing:
            - Popularity score
            - Breakdown of response themes
    # kwargs:
            {} # none needed / function is not generalisable
    """
    
    ################## prelim: compute initial breakdown of values ##################
    
    # get value counts of the multi-column df
    values = df.apply(pd.Series.value_counts, axis = 0)
    
    # convert to %s
    values = values.apply(lambda x: x / len(df))
        

    ################## 1a compute sumproduct for "Popularity score" bar plot ##################

    values.loc["Popularity scores"] = [np.nansum([x * y for x, y in zip([int(x[0]) for x in values.index.values], values[col].values)]) / np.nansum(values[col].values)
                                      for col in values.columns]
    
    pop_score_values = values.loc["Popularity scores"].T.sort_values(ascending = False)


    ################## 1b compute breakdown of response themes for "Breakdown" bar plot ##################
    
    # compute counts for: Unlikely and Likely
    values.loc["Unlikely"] = values.apply(lambda x: x[x.index.str.contains("1|2")].sum(),
                                                      axis = 0)
    
    values.loc["Likely"] = values.apply(lambda x: x[x.index.str.contains("4|5")].sum(),
                                                        axis = 0)
    
    # rename "3 - Might Use" to "Might use"
    values = values.rename(index = {"3 - Might Use" : "Might use"})
    
    breakdown_values = values.loc[["Likely",
                                  "Might use",
                                  "Unlikely"]].T.reindex(pop_score_values.index)
    
    col_details = {}
    col_details["Likely"] = ["#67002C" if A_or_B == "A" else "#26272A",
                              '<b>%{y:.0%}</b> said they would be <b>likely</b> to use "%{customdata[1]}"<extra></extra>',
                              []] # customdata: none needed for this question
    col_details["Might use"] = ["#FFFFFF",
                               '<b>%{y:.0%}</b> said they <b>might use</b> "%{customdata[1]}"<extra></extra>',
                               []] # customdata: none needed for this question
    col_details["Unlikely"] = ["#FFC2DC" if A_or_B == "A" else "#DADCDE",
                             '<b>%{y:.0%}</b> said they would be <b>unlikely</b> to use "%{customdata[1]}"<extra></extra>',
                             []] # customdata: none needed for this question


    # customdata:
    # if a question item exceeds 40 chars in length, it needs wrapping:
    customdata = pd.DataFrame({"position" : [pos+1 for pos, label in enumerate(pop_score_values.index)],
                               "label" : [label for pos, label in enumerate(pop_score_values.index)]}).to_numpy()       
    pop_score_values.index = [wrap_func(col) for col in pop_score_values.index] 
    breakdown_values.index = [wrap_func(col) for col in breakdown_values.index]


    ################## 1c markdown for "popularity score" bar plot ##################

    graph_footnote = [dcc.Markdown("5 = 'Definitely would use'"),
                      dcc.Markdown("1 = 'Definitely would not use'")]


    ################## 1d create vertical "Popularity score" bar chart ##################

    fig = {
    'data': [{'customdata' : customdata,
              'alignmentgroup': 'True',
              'hovertemplate': '#%{customdata[0]}: "%{customdata[1]}" has a popularity score of <b>%{y:.2f}</b> out of 5<extra></extra>',
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54",
                         'line' : {'color' : "#000000",
                                   'width' : 1}
                         },
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': pop_score_values.values,
              'texttemplate' : "%{text:.2f}",
              'textposition': 'outside',
              'insidetextanchor' : 'middle',
              'type': 'bar',
              'x': pop_score_values.index.values,
              'xaxis': 'x',
              'y': pop_score_values.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'showlegend' : False,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0},
               'title': {'font': {'color': '#003865'},
                         'text': "Popularity score"},
               'yaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range' : [1, 5],
                         'nticks' : 5, # only show 1-5
                         'title': {'text': 'Popularity score'},
                         'automargin' : True 
                         },
               'xaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'automargin' : True, # stops x-axis labels being cut-off
                         'ticklen' : 10
                         }, 
               'template': 'simple_white'
               }
    }


    ################## 1e create vertical "Breakdown" stacked bar chart ##################

    # figure is based on plot from "horizontal-stacked-plot" function
    fig_2 = {
    'data': [{'customdata' : customdata,
              'alignmentgroup': 'True',
              'hovertemplate': col_details[col][1],
              'legendgroup': col,
              'marker': {'color': col_details[col][0],
                         'line' : {'color' : "#000000",
                                   'width' : 1}
                         },
              'name': col,
              'offsetgroup': col,
              'orientation': 'v',
              'showlegend': True,
              'text': breakdown_values[col].values,
              'texttemplate' : "%{text:.0%}",
              'textposition': 'inside',
              'insidetextanchor' : 'middle',
              'type': 'bar',
              'x': breakdown_values[col].index.values,
              'xaxis': 'x',
              'y': breakdown_values[col].values,
              'yaxis': 'y'}
             for col in col_details],
    'layout': {'barmode': 'relative',
               'showlegend' : True,
               'legend': {'title': {'text': ''}, 
                          'orientation' : 'h',
                          'tracegroupgap': 0,
                          "yanchor" : "bottom",
                          "y" : 1.03,
                          "xanchor" : "right",
                          "x" : 1.0},
               'title': {'font': {'color': '#003865'},
                         'text': "Breakdown of likelihood"},
               'yaxis': {'anchor': 'y',
                         'domain': [0.0, 1.0],
                         'range' : [0.0, 1.0],
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)},
                         'automargin' : True 
                         },
               'xaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'automargin' : True, # stops x-axis labels being cut-off
                         'ticklen' : 10
                         }, 
               'template': 'simple_white'
               }
    }
    
    return [dcc.Graph(figure = fig)] + graph_footnote + [dcc.Graph(figure = fig_2)]



######################################## Age / Income

def distribution_plot(df, A_or_B, **kwargs):
    """
    # returns:
        - vertically-orientated histogram-like bar plot.
        
    # Notes:
        This function is designed to be as generalisable as possible.
    # kwargs:
        {"q_id" : str} # makes known the question id 
    """
    
    ################## prelim: confirm presence of non-number responses and create footnote if needed ##################
    
    # confirm length of column / drop non-numeric responses
    responses = pd.to_numeric(df.iloc[:,0], errors = "coerce").dropna()
    
    # check if a footnote is needed:
    if len(responses) < len(df):
        footnote = [dcc.Markdown("Note: actual sample is {:,} ({:.0%}).".format(len(responses), len(responses)/data.TOTAL_SAMPLE),
                    className = "text-primary",
                    # only include top padding for 1st footnote
                    style = {"paddingTop" : "25px"})
                    ]
    else:
        footnote = []

    
    ################## 1a compute bin distribution ##################
    
    # Note: I wanted the bins to remain fixed regardless of audience filtering. Therefore, the same
    # bins are used - and fetched from data.py - regardless of audience filtering.
    # Additonally, I discovered that it is not easy to apply value_counts() to the "Purchase power bins"
    # data column because there is no easy way to order the resulting value counts by bin. 
    
    if kwargs["q_id"] == "Age":
        
        # group age responses by data.age_bins
        value_counts = responses.value_counts(bins = data.age_bins, sort = False)
        
        # format bins
        value_counts.index = [format_bins(str(x), prepend="") for x in value_counts.index]
        

        ################## Age only: PRODUCE PIE CHART SHOWING GENERATIONAL BREAKDOWN ##################
        
        # pie: colors
        pie_colors = ["#CE0058" if A_or_B == "A" else "#4B4F54"]*10
        
        # pie: group age responses by data.generational_age_bins
        pie_value_counts = responses.value_counts(bins = data.generational_age_bins, sort = False)
        
        # pie: format bins
        pie_value_counts.index = [format_bins(str(x), prepend="") for x in pie_value_counts.index]
        
        # convert values into %s
        pie_value_counts = pie_value_counts.apply(lambda x: x / len(responses))
        
        # pie: hovertemplate
        pie_hovertemplate = '<b>%{percent:.0%}</b> are <b>%{customdata[0]}<extra></extra>'
        
        # pie: customdata / table values
        customdata = pd.DataFrame(data = {"Generation" : data.generation_description,
                                          "Age range" : list(pie_value_counts.index.str.replace("<br>", " ", regex = False)),
                                          "Share (%)" : list(pie_value_counts.values)})
        
        # there is an issue whereby pie chart customdata cannot take multiple values...
        def func(row):
            return "<b>{}</b> <br>({} years)".format(row["Generation"], row["Age range"])
        pie_customdata = customdata.apply(func, axis = 1)
        pie_customdata = pie_customdata.to_numpy()
        
        
        ################## produce table showing generation breakdown ##################

        customdata["Share (%)"] = customdata["Share (%)"].apply(lambda x: "{:.0%}".format(x)
                                                                    if "{:.0%}".format(x) != "0%"
                                                                    else "{:.2%}".format(x))
        
        table = [dbc.Table.from_dataframe(customdata, bordered = True, hover = True,
                                 style = {"color" : "#CE0058" if A_or_B == "A" else "#4B4F54"})]
        
        
        # convert values into %s
        value_counts = value_counts.apply(lambda x: x / len(responses))

        
    if kwargs["q_id"] == "Income":
        
        # group income responses by data.income_bins
        value_counts = responses.value_counts(bins = data.income_bins, sort = False)
        
        # format bins
        value_counts.index = [format_bins(str(x)) for x in value_counts.index]
        
        
        # first bin format:
        # step one: replace first number with "Under"
        value_counts = value_counts.rename(index = {value_counts.index[0] : 
                                                    re.sub("^.*\$", "Under $", value_counts.index[0])
                                                    }
                                           )  
        # step two: undo the substraction by 1 (e.g. $24,999 becomes $25,000 again)
        value_counts = value_counts.rename(index = {value_counts.index[0] : 
                                                    re.sub("(\d.*\d)", 
                                                           lambda x: remove_punc_and_add_one(x.group()), 
                                                           value_counts.index[0])
                                            }
                                   )
    
        # last bin format:
        # step one: find the "$200,000 - 224,999" bracket
        last_bin = value_counts.loc[value_counts.index.str.contains("^\$200,000", regex = True)].index[0]
        # step two: replace the second number with "or more"
        value_counts = value_counts.rename(index = {last_bin : 
                                                    re.sub("(^\$200,000).*", 
                                                           r"\1" + " or more", 
                                                           last_bin)
                                                    }
                                           )      
        # step three: sum up the values from "$200,000 or more" onwards
        last_bin_value = value_counts.loc["$200,000 or more":].sum()
        value_counts.loc["$200,000 or more"] = last_bin_value
        value_counts = value_counts.loc[:"$200,000 or more"]
    
    
        # convert values into %s
        value_counts = value_counts.apply(lambda x: x / len(responses))
    
    
        ################## produce table showing income range breakdown ##################

        table_data = pd.DataFrame(data = {"Income range (US purchase power)" : list(value_counts.index),
                                          "Share (%)" : list(value_counts.values)})

        table_data["Share (%)"] = table_data["Share (%)"].apply(lambda x: "{:.0%}".format(x)
                                                                if "{:.0%}".format(x) != "0%"
                                                                else "{:.2%}".format(x))
        
        table = [dbc.Table.from_dataframe(table_data, bordered = True, hover = True,
                                 style = {"color" : "#CE0058" if A_or_B == "A" else "#4B4F54"})]
        
    
    ################## 1b compute median and IQR for markdown + prepare fig_1 plot ##################

    if kwargs["q_id"] == "Age":
        
        iqr = "{:.0f} - {:.0f}".format(responses.quantile(0.25), responses.quantile(0.75))
        
        markdown = [dcc.Markdown("##### Median: {:.0f} years".format(responses.median()), 
                                 className = "text-danger" if A_or_B == "A" else "text-secondary"),
                    dcc.Markdown("##### IQR: {} years".format(iqr), 
                                 className = "text-danger" if A_or_B == "A" else "text-secondary")]
        
        # hovertemplate text:
        fig_1_hovertemplate = '<b>%{y:.0%}</b> are ages <b>%{customdata}</b> years<extra></extra>'
       
        # plot title
        fig_1_title = "Age distribution"
        
        
    if kwargs["q_id"] == "Income":

        iqr = "${:,.0f} - ${:,.0f}".format(responses.quantile(0.25), responses.quantile(0.75))

        markdown = [dcc.Markdown("##### Median: ${:,.0f}".format(responses.median()), 
                                 className = "text-danger" if A_or_B == "A" else "text-secondary"),
                    dcc.Markdown("##### IQR: {}".format(iqr), 
                                 className = "text-danger" if A_or_B == "A" else "text-secondary")]
  
        # hovertemplate text:
        fig_1_hovertemplate = '<b>%{y:.0%}</b> earn <b>%{customdata}</b><extra></extra>'
       
        # plot title
        fig_1_title = "Household income distribution<br>(US purchase power)"        
   
    
    # create customdata for more readable text via hovertemplate
    fig_1_customdata = list(value_counts.index)


    ################## 1c create histogram-like bar plot ##################
            
    # this is based loosely on the figure used by the function for Q4
    fig = {
    'data': [{'alignmentgroup': 'True',
              'customdata': fig_1_customdata, # used for hovertemplate
              'hovertemplate': fig_1_hovertemplate,
              'marker': {'color': "#CE0058" if A_or_B == "A" else "#4B4F54", 
                         'pattern': {'shape': ''}},
              'name': '',
              'offsetgroup': '',
              'orientation': 'v',
              'showlegend': False,
              'text': value_counts.values,
              "texttemplate" : "%{text:.0%}",
              'textposition': 'outside',
              'type': 'bar',
              'x': value_counts.index.values,
              'xaxis': 'x',
              'y': value_counts.values,
              'yaxis': 'y'}],
    'layout': {'barmode': 'group',
               'legend': {},
               'title': {'font': {'color': '#003865'},
                         'text': fig_1_title},
               'yaxis': {'anchor': 'y',
                         'domain': [0.0, 1], 
                         'range': [0, 1.1], # just in case a 100% value is presented, data label is still visble
                         'tickformat': '.0%',
                         'title': {'text': '% of Audience {}'.format(A_or_B)}
                         },
               'xaxis': {'anchor': 'x', 
                         'domain': [0.0, 1.0], 
                         'ticklen' : 10,
                         'title': {},
                         "automargin" : True, # very important: stops labels from being cut-off
                         },
               'template': 'simple_white'
               }
    }

    
    ################## 1d AGE ONLY: Pie chart of generation breakdown ##################    
    
    # figure is based on Q3 pie chart
    if kwargs["q_id"] == "Age":
        fig_2 = {
        'data': [{'type': 'pie',
                  'customdata' : pie_customdata,
                  'values': pie_value_counts.values,
                  'marker': {'colors': pie_colors, 
                             'line': {'color': '#000000', 
                                      'width': 2}
                             },
                  "sort" : True,
                  "direction" : "clockwise",
                  'labels': data.generation_description,
                  'texttemplate': '%{label}<br>(%{percent:.0%})',
                  'hovertemplate': pie_hovertemplate,
                  'pull': 0.05,
                  'showlegend': False,
                  'textposition': 'inside'}],
        'layout': {'template': 'simple_white',
                   'title' : {'font': {'color': '#003865'},
                              'text': "Generation breakdown"}
                   }
        }
    
    if kwargs["q_id"] == "Age": return markdown + [dcc.Graph(figure = fig_2)] + table + [dcc.Graph(figure = fig)] + footnote
    
    if kwargs["q_id"] == "Income": return markdown + [dcc.Graph(figure = fig)] + table + footnote



######################################## Appendix

# This section contains the original code used to contrust each and every figure.

# Great resource by plotly on figure construction apporaches and architecture:
# https://plotly.com/python/creating-and-updating-figures/

# As recommended in the above article, plotly.express was originally used to start creating each and
# every figure. They were then modified as required using:
    # fig.update_traces (updates properties of fig.data)
    # fig.update_layout (updates properties of fig.layout)

# Once constructed as desired and tested, each figure was printed to obtain the raw dictionary structure.
# Raw dictionary structures are used in the final code of each function because this low-level approach
# builds the figure the quickest.

# For instance, here is an experiment conducted:
    # when selecting Q1 for Audience A after launch
    # this code was used: https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
    # it was sandwiched between the run_question_function() line in callbacks.py
    
    # convenience approach (plotly.express & ad-hoc updates):
    # 0.8926432132720947 seconds
    
    # dictionary approach (raw dictionary):
    # 0.10425162315368652 seconds



######################################## Q1 / Q2

######## Figure: create bar chart of "All return trips"

    # fig = px.bar(all_trips, x = all_trips.index, y = all_trips.name,
    #               text = all_trips.name,
    #               title = "Return trips {}<br>All trips".format(timeframe))
    
    # # update figure data properties:
    # fig.update_traces(marker_color = "#CE0058" if A_or_B == "A" else "#4B4F54",
                      
    #                   hovertemplate =  "%{y:.0%} took %{x} return trips<extra></extra>", 
                      
    #                   texttemplate = '%{text:.0%}', 
    #                   textposition = 'outside', # https://plotly.com/python/text-and-annotations/
                      
    #                   showlegend = False)   
    
    # # update figure layout properties:
    # fig.update_layout(title_font_color = "#003865",
                      
    #                   xaxis_title_text = "Number of trips taken annually before 2020",
    #                   yaxis_title_text = "% of Audience {}".format(A_or_B),
                      
    #                   yaxis_tickformat = ".0%",
    #                   yaxis_range = [0,1.1]) # fixes range / goes to 110% so a "100%" label can be seen
    
    # print(fig)


######## Figure: create bar chart of purpose/domain breakdowns

    # fig_2 = px.bar(breakdown_trips, barmode = "group",
    #                 title = "Return trips {}<br>By trip type".format(timeframe))
    
    # # update color of each trace:
    # # Leisure, Business, Domestic, International (column order is constant)
    # colors = ["#007DBA", "#96172E", "#218D7F", "#D64D6E"]
    # color_dict = {trace : color for trace, color in zip(breakdown_trips.columns, colors)}
    # for trace in fig_2.data:
    #     trace["marker"]["color"] = color_dict[trace["name"]]
    
    # # update hovertemplate of each trace:
    # hovertemplate_base = "%{y:.0%} took %{x} "
    # for trace in fig_2.data:
    #     trace["hovertemplate"] = hovertemplate_base + "{}<extra></extra>".format(trace["name"].lower())
    
    # # update figure layout properties:
    # fig_2.update_layout(title_font_color = "#003865",
                        
    #                     xaxis_title_text = "Number of trips taken annually before 2020",
    #                     yaxis_title_text = "% of Audience {}".format(A_or_B),
    #                     yaxis_tickformat = ".0%",  
                        
    #                     legend_title_text = "Trip type",  
    #                     legend_bgcolor = "rgba(0,0,0,0)",  
    #                     legend_x = 0.75,  
    #                     legend_y = 0.95,  
    #                     yaxis_range = [0,1.1], # fixes range / stops autoscaling on legend select
                        
    #                     xaxis_showgrid = True,
    #                     xaxis_ticks = "outside",
    #                     xaxis_tickson = "boundaries",
    #                     xaxis_ticklen = 10)
    
    # print(fig_2)



######################################## Q3 / Q3B

######## Figure: 1b create Yes-No pie chart

    # fig = go.Figure(data = [go.Pie(values = Q3_values.values, labels = Q3_values.index.values)
    #                         ],
    #                 )

    # # update figure data properties:
    # fig.update_traces(texttemplate = '%{label} (%{percent:.0%})', 
    #                   textposition = 'inside',    
    #                   hovertemplate =  "%{percent:.0%} said %{label}<extra></extra>",
    #                   showlegend = False, 
    #                   marker = {"colors" : colors,
    #                             "line" : {"color" : "#000000",
    #                                       "width" : 2}},
    #                   pull = 0.03) 

    # print(fig)

######## Figure: create stacked bar chart of Q3B values

    # fig_2 = px.bar(Q3B_values.iloc[:,:2], barmode = "relative", orientation = "h",
    #                title = data.corresponding("Variable alias", kwargs["follow-up question"], "Question")[0])
           
    # # will be accessed for hover label text
    # fig_2.update_traces(customdata = Q3B_values["Total"])
    
    # # add annotation above each bar: sum of each bar 
    # # note that axes are flipped in horizontal orientation
    # total_labels = [{"x": total + .02, "y": x, "text": "{:.0%}".format(total), "showarrow": False} 
    #                 for x, total in zip(Q3B_values.index, Q3B_values["Total"])]
    # fig_2 = fig_2.update_layout(annotations = total_labels)
      
    # # add data labels for only first bar: Base Tier - shows breakdown
    # fig_2.data[0]["text"] = ["{:.0%}".format(Q3B_values[Q3B_values.columns[0]][0])]
    # fig_2.data[1]["text"] = ["{:.0%}".format(Q3B_values[Q3B_values.columns[1]][0])]
    
    # # update figure layout properties:
    # fig_2.update_layout(title_font_color = "#003865",
                      
    #                     yaxis_title_text = None,
    #                     xaxis_title_text = "% of Audience {}".format(A_or_B),
                        
    #                     xaxis_tickformat = ".0%",
    #                     xaxis_range = [0,1]) # fixes range / goes to 110% so a "100%" label can be seen
    
    # print(fig_2)
    
    # Note: the following properties were manipulated in raw dictionary only:
    # color of bars
    # legend
