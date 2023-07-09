# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 11:20:08 2021

@author: Joseph.Moyes

File information: 
    entry-point for launching the app.
    all files (app, layout, callback) are imported (executed) from here.
"""
# note: the time to load the app is taken up almost completely by importing the data file 
#       (df) in data.py. However, know that this is imported when "from layout import layout"
#       runs. Although callbacks.py also imports data (via importing layout), this does not
#       result in the data file being imported twice because python does not re-evaluate a 
#       module when re-imported - every subsequent import of a module is accessed via sys.modules
# source: https://stackoverflow.com/questions/12487549/how-safe-is-it-to-import-a-module-multiple-times
# additional note: I have since pickled the data, so data load time is now ~3 seconds instead of ~30 seconds!

# import app object
from app_instantiation import app
server = app.server

# import app layout / run layout module
from layout import layout
# import callback functions
import callbacks


# The below allowed me to modify the title (text that appears on the tab next to my favicon)
# Resources for the below:
# documentation: https://dash.plotly.com/external-resources
# example: https://github.com/davidcomfort/dash_sample_dashboard/blob/master/index.py
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Collinson Research 2021</title>
        {%favicon%}
        {%css%}
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

app.layout = layout

if __name__ == "__main__":
    app.run_server()
