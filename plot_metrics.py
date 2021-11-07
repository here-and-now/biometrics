from bokeh.plotting import figure,show
from bokeh.io import save
from bokeh.models import HoverTool
from bokeh.models.axes import LinearAxis
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.models import CustomJS, DateRangeSlider, ColumnDataSource, CheckboxButtonGroup, RadioButtonGroup
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
import pandas as pd
from sqlalchemy import create_engine, inspect
import datetime
import os
from pathlib import Path

from collections import defaultdict
today = datetime.date.today()
date_range_slider = DateRangeSlider(value=(today - datetime.timedelta(days=7), today),
                                    start=today - datetime.timedelta(days=30),
                                    end=today + datetime.timedelta(days=1))

db_dict = {'garmin': 'garmin.db',
            'activities': 'garmin_activities.db',
            'monitoring': 'garmin_monitoring.db',
            'garmin_summary': 'garmin_summary.db',
            'summary': 'summary.db'}

def change_plot(attrname, old, new):

    print('Selected x: ', x)
    print('Selected y: ', y)
    p.plot.xaxis.axis_label= x
    p.plot.yaxis.axis_label= y
    p.plot_height = 600
    p.plot_width = 1800

    for line in list(p.renderers):
        p.renderers.remove(line)
    # p.title(y)
    p.line(x=x,
           y=y,
           source=source)

    # update_plots(p)
    
def update_plots(p):
    callback = CustomJS(args=dict(p=p), code="""
        p.x_range.start = cb_obj.value[0]
        p.x_range.end = cb_obj.value[1]
        p.x_range.change.emit()
        """)
    return callback

def load_dbs():
    recursive_dict = lambda: defaultdict(recursive_dict)
    dfs_dict = recursive_dict()

    for db, fname in db_dict.items():

        db_path = str(Path.home()) + '/HealthData/DBs/' + fname
        engine = create_engine('sqlite:////' + db_path)

        cnx = engine.connect()
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        if db == 'monitoring': 
            idx_col='timestamp'
        else:
            idx_col = None

        for table in table_names:
            
            dfs_dict[db][table] = pd.read_sql_table(table, cnx, index_col=idx_col)
            dfs_dict[db][table].sort_index(inplace=True)
            # print(dfs_dict[db][table])
    return dfs_dict

def plot_anything(dfs_dict, db, table, x='timestamp', y=None, index_col=None):
    dfs_dict[db][table]
    source = ColumnDataSource(dfs_dict[db][table])
    print(source.data) 
        
    p = figure(x_axis_type='datetime')
    p.line(x=x,y=y,source=source)
    
    return p


dfs_dict = load_dbs()
p = plot_anything(dfs_dict, 'monitoring', 'monitoring_hr', x='timestamp', y='heart_rate')
# iniate dataframe and bokeh source

p.sizing_mode = 'scale_width'
p.aspect_ratio = 3
#date range slider callback
for plot in [p]:
    callback = update_plots(plot)
    date_range_slider.js_on_change('value_throttled', callback)

# radio button group change listeners
l = layout([
            [date_range_slider],
            [p]
])
l.sizing_mode = 'scale_width'
curdoc().add_root(l)

# show(l)



