# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 11:50:49 2021

@author: Joseph.Moyes

There are 4 worksheets expected in the "application-ready data file":
    1. Labels: mapping of column names and survey questions, as well as variable aliases
    2. Questions: Survey headers and questions
    3: Dashboard filters: provide 'shortcut' radio button options on filter menu

Note: the data worksheet has been saved to "temp.json.gz". See section: import "Data" sheet
"""

import pandas as pd
import numpy as np
import json

# hardcode total sample to save on memory
TOTAL_SAMPLE = 6024

# determine demographic variables/columns that are accessed within this script as part of initial data preparation
# only those columns will be instantiated to save on memory
demos = ["Gender", "Age", "Income", "Travel", "Q1 travel outlier", "Travel purpose", "Travel domain"]


######################################## application-ready data file location ########################################

data_file = r"Prepared data.xlsx"


######################################## import "Data" sheet ########################################
# fetch the data of the application.

# pickle the dataset and save it for super fast loading (load time: < 1 second; file size: 968KB):
# df = pd.read_excel("Data sheet extracted from Prepared data.xlsx", sheet_name = "Data")
# df.to_pickle("Prepared data pickled.gz", compression = "gzip")

# OR

# convert the dataset to compressed json for fast loading and efficient memory usage (load time: ~ 4 seconds; file size: 3MB):
# df = pd.read_excel("Data sheet extracted from Prepared data.xlsx", sheet_name = "Data")
# df.to_json('temp.json.gz', orient='records', lines=True, compression='gzip')

# helpful sources for the latter:
# https://stackoverflow.com/questions/39257147/convert-pandas-dataframe-to-json-format
# https://stackoverflow.com/questions/39450065/python-3-read-write-compressed-json-objects-from-to-gzip-file
# https://stackoverflow.com/questions/30088006/loading-a-file-with-more-than-one-line-of-json-into-pandas 

# NOTE: clearly the former is the better option therefore I have implemeneted that.


# see following Dash resource that explains use of this syntax/function:
# https://dash.plotly.com/performance  
# @cache.memoize(timeout = 60*30)
def get_data():    
    return pd.read_pickle("Prepared data pickled.gz", compression = "gzip")


# a df containing demographic-only columns is declared below (section: filter menu options) and deleted at end of script


######################################## import "Labels" sheet ########################################
# This worksheet contains a mapping of variables to their label description.
# It also contains a column named "variable alias" for the identification of ...
# ... key variables.

# assign labels worksheet name:
labels_worksheet = "Labels"

# column name in Data (df) and question wording
dfL = pd.read_excel(data_file, sheet_name = labels_worksheet)

# function that fetches corresponding value in given column
# very handy: used throughout application code to e.g. fetch actual data column name from variable alias name
# new: I have added the option of including a preliminary filtering of dfL. This is essential when looking up question items/components
# ...because the same question item/component may be found across multiple questions! 
def corresponding(value_col, value, target_col, initial_filter_col = None, initial_filter_value = None):
    dfL_temp = dfL
    if initial_filter_col and initial_filter_value:
        dfL_temp = dfL_temp[dfL_temp[initial_filter_col] == initial_filter_value]
    return dfL_temp[dfL_temp[value_col] == value][target_col].to_list()


# Useful rounding up/down function:
# used to produce income bins
# Resource: https://stackoverflow.com/questions/8866046/python-round-up-integer-to-next-hundred
def _round(x, up_or_down = "up", nearest = 1000):
    if up_or_down == "up":
        return x if x % nearest == 0 else (x + nearest) - (x % nearest)
    elif up_or_down == "down":
        return x if x % nearest == 0 else x - (x % nearest)


######################################## import "Questions" sheet ########################################
# This worksheet contains the menu headers (column titles) and associated ...
# ... questions (column entries).

# assign questions worksheet name:
questions_worksheet = "Questions"

# read in "Questions" sheet
dfQ = pd.read_excel(data_file, sheet_name = questions_worksheet)


# ensure "Unnamed" empty columns are removed
dfQ = dfQ[[col for col in dfQ.columns if not "Unnamed" in col]]

# sections:

# compile dictionary {section : {questions : [section questions],
#                                id : index}}
# necessary to have a corresponding dash component id -friendly value
sections = {col : {'questions' : list(dfQ[col].dropna().values),
                   'id' : "section{}".format(ind)} 
                   for ind, col in enumerate(dfQ.columns)}

# questions:

# compile list of questions
# iterate over each column first to preserve order of questions!
questions_order = [dfQ.iloc[row, col] for col in range(dfQ.shape[1]) for row in range(dfQ.shape[0])
                   if not pd.isnull(dfQ.iloc[row, col])]

# question_ids is used in the produce_graphic callback to map from selected question to id
# the id is looked up via the Labels worksheet/dfL and the corresponding data columns under "Column" are retrieved
# the ids are also used as component ids (for each question button in the menu)
question_ids = {q : corresponding("Question", q, "Variable alias")[0]
                for q in questions_order}


######################################## import "Dashboard filters" sheet ########################################
# This worksheet contains filter menu radio buttons.
# It is used e.g. to store markets' corresponding region, which can be selected via radio buttons.

# assign dashboard filters worksheet name:
filters_worksheet = "Dashboard filters"

# read in "Dashboard filters" sheet
dfD = pd.read_excel(data_file, sheet_name = filters_worksheet)


# ensure "Unnamed" empty columns are removed
dfD = dfD[[col for col in dfD.columns if not "Unnamed" in col]]


######################################## filter menu options ########################################

# create demographic columns -only df for this script
# saves on memory
# it is deleted at end of script
# IMPORTANT NOTE: this is first time that get_data() is called - the result should be cached for reuse in the callback function: filter_and_summaries 
demo_df = get_data()[[corresponding("Variable alias", demo, "Column")[0] for demo in demos]]


######## markets

# fetch 'Market' values from 'Dashboard filters' worksheet
markets = [value for value in dfD["Market"].dropna()]

# fetch 'Market region' values from 'Dashboard filters' worksheet
# make region : markets dictionary [for region quickfire buttons]:
market_regions = {}
market_regions["All"] = markets
for region in dfD["Market region"].dropna():
    market_regions[region] = list(dfD.loc[dfD["Market region"] == region, "Market"].dropna()) 


######## genders

# fetch 'Gender' values from 'Data' worksheet
genders = demo_df[corresponding("Variable alias", "Gender", "Column")[0]].unique()

# make gender option : gender dictionary [for gender quickfire options]:
gender_groups = {}
def gender_options(gender_option):
    if gender_option == "All":
        return [gender for gender in genders]
    elif gender_option == "Exclude NAs":
        return [gender for gender in genders if gender != "Prefer not to answer"]
    else:
        return [gender_option]

for gender_option in dfD["Gender groupings"].dropna():
    gender_groups[gender_option] = gender_options(gender_option)


######## ages

# fetch 'Age' descriptive statistics via 'Data' worksheet
ages = demo_df[corresponding("Variable alias", "Age", "Column")[0]].describe().apply(round).to_dict()

# make age option : age_range dictionary [for age quickfire options]:
age_groups = {}
def age_ranges(age_group):
    if age_group == "All":
        return [ages['min'], ages['max']]
    elif age_group == "Bottom 25%":
        return [ages['min'], ages['25%']]
    elif age_group == "Bottom 50%":
        return [ages['min'], ages['50%']]
    elif age_group == "Top 50%":
        return [ages['50%'], ages['max']]
    elif age_group == "Top 25%":
        return [ages['75%'], ages['max']]
    
for option in dfD["Age groupings"].dropna():
    age_groups[option] = age_ranges(option)

# produce age bins (these are used by agg_functions.distribution_plot)
age_data = demo_df[corresponding("Variable alias", "Age", "Column")[0]]
_max = _round(age_data.max(), up_or_down = "up", nearest = 5) # this should equal chosen bin fequency

age_bins_1 = [(18, 25)]
age_bins_2 = list(pd.interval_range(start = 25, freq = 5, end = 70, closed = 'left').to_tuples())
age_bins_3 = [(70, _max+1)]

# combine:
age_bins = pd.IntervalIndex.from_tuples(age_bins_1 + age_bins_2 + age_bins_3, closed = "left")


# generational age bins (as of the year 2021):
generational_age_bins = pd.IntervalIndex.from_tuples([(18,25), (25, 41), (41, 57), (57, 76), (76, _max+1)], closed = "left")
generation_description = ["Gen Z", "Millennials", "Gen X", "Boomers", "Elders"]

######## incomes

# fetch 'Income' descriptive statistics via 'Data' worksheet
# round is needed to convert to integer (values were rounded to nearest 000 in data file)
incomes = demo_df[corresponding("Variable alias", "Income", "Column")[0]].describe().apply(round).to_dict()

# make income option : income_range dictionary [for income quickfire options]:
income_groups = {}
def income_ranges(income_group):
    if income_group == "All":
        return [incomes['min'], incomes['max']]
    elif income_group == "Bottom 25%":
        return [incomes['min'], incomes['25%']]
    elif income_group == "Bottom 50%":
        return [incomes['min'], incomes['50%']]
    elif income_group == "Top 50%":
        return [incomes['50%'], incomes['max']]
    elif income_group == "Top 25%":
        return [incomes['75%'], incomes['max']]
    
for option in dfD["Income groupings"].dropna():
    income_groups[option] = income_ranges(option)

# produce income bins (these are used by agg_functions.distribution_plot)
income_data = demo_df[corresponding("Variable alias", "Income", "Column")[0]]
_max = _round(income_data.max(), up_or_down = "up", nearest = 25000) # this should equal chosen bin fequency
income_bins = pd.interval_range(start = 0, freq = 25000, end = _max, closed = 'left')


######## travels

# fetch 'Travel' descriptive statistics via 'Data' worksheet
# outliers are excluded from travel total column to obtain describe() details e.g. min and max.
travels = demo_df.loc[demo_df[corresponding("Variable alias", "Q1 travel outlier", "Column")[0]] == False,
             corresponding("Variable alias", "Travel", "Column")[0]].describe().apply(round).to_dict()

# make travel option : travel_range dictionary [for travel quickfire options]:
travel_groups = {}
def travel_ranges(travel_group):
    if travel_group == "All":
        return [travels['min'], travels['max']]
    elif travel_group == "Bottom 25%":
        return [travels['min'], travels['25%']]
    elif travel_group == "Bottom 50%":
        return [travels['min'], travels['50%']]
    elif travel_group == "Top 50%":
        return [travels['50%'], travels['max']]
    elif travel_group == "Top 25%":
        return [travels['75%'], travels['max']]
    
for option in dfD["Travel groupings"].dropna():
    travel_groups[option] = travel_ranges(option)
    
# "Other" is excluded. 
# Note the use of sorted - I used this to dictate how the purpose radio buttons and domain radio buttons will be ordered in the UI.
traveller_purposes = {"{} travelers".format(purpose) : purpose for purpose in sorted(demo_df[corresponding("Variable alias", "Travel purpose", "Column")[0]].dropna().unique(), reverse = True) if purpose != "Other"} 
traveller_domains = {"{} travelers".format(domain) : domain for domain in sorted(demo_df[corresponding("Variable alias", "Travel domain", "Column")[0]].dropna().unique())} 


######################################## behavioural filter menu options ########################################

# in this section, I build a dictionary of question : question items : all response values
# purpose: this means we don't have to reference the dataset every time "on_custom_selected_item" is called. Otherwise, we would have to perform quite an
# expensive operation to establish what values should be shown if a given question is selected. Instead of doing that on the fly, I have done it in advance
# below, and then simply load the dictionary from json, meaning that response values per question are efficiently obtainable.
# NOTE: very important to look up the question item pertaining to the appropriate question due to the same question item existing across multiple questions. 

# def fetch_and_sort_uniques(question_item, question):
#     uniques = pd.Series(get_data()[corresponding("Component", question_item, "Column",
#                                                   initial_filter_col = "Question", initial_filter_value = question)[0]].unique())     
    
#     # if values include string values ensure all values are of type string before sorting
#     if uniques.dtype == "O":
#         uniques = uniques.apply(str)
        
#         # exclude empty response values (e.g. Q3B has empties)
#         uniques = uniques.loc[uniques.str.contains("[a-zA-Z0-9]+")]
        
#         # sort values
#         uniques = uniques.sort_values()
        
#         # we now have to convert any numbers back from strings
#         uniques = uniques.apply(lambda x: int(x) if x.isnumeric() else x)
        
        
#     # if values are integers, we must ensure they are stored as Python int (otherwise cannot store resulting dictionary as json)
#     # sources: https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable/50916741
#               # https://stackoverflow.com/questions/12648624/python-converting-an-numpy-array-data-type-from-int64-to-int
#               # note: the only way to achieve type "int" seemed to be using the .to_list() method.
    
#     # simply sort all values if numbers
#     else:        
#         uniques = uniques.sort_values()
     
#     return uniques.to_list()
    
# # demographic questions are excluded
# question_items_values_dict = {question : {question_item : fetch_and_sort_uniques(question_item, question)
#                                           for question_item in sorted(corresponding("Question", question, "Component"))} 
#                               for question in questions_order[:-4]}
    
# # ad hoc edits are required:
# # 1. add Q3B as a question item under "Q3 Are you a member of any airline frequent flyer programmes?"
# Q3 = "Q3 Are you a member of any airline frequent flyer programmes?"
# Q3B = "Q3B Please select your highest tier of membership with an airline frequent flyer programme:"
# question_items_values_dict[Q3][Q3B] = fetch_and_sort_uniques(Q3B, Q3)
# # 2. replace open-ended responses, as values for Q15, with top 50 words + "Other words"
# Q15 = "Q15 What innovation or improvement would you most like to see at the airport of the future?"
# question_items_values_dict[Q15][Q15] = sorted(list(pd.read_excel("Q15 keyword database.xlsx", header = 1)["Word"].iloc[:50].values))

# # write to a json file:
# with open("question_values.json", "w") as file:
#     json.dump(question_items_values_dict, file)

# import question : question items : all response values dictionary
with open("question_values.json") as file:
    question_items_values_dict = json.load(file)



# clean up the following variables to save on memory:
del demo_df
del dfQ
del dfD
del data_file
del labels_worksheet
del questions_worksheet
del filters_worksheet