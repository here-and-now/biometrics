from bokeh.plotting import figure,show
from bokeh.io import save
from bokeh.models import HoverTool
from bokeh.models.axes import LinearAxis
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.models import CustomJS, DateRangeSlider, ColumnDataSource, CheckboxButtonGroup, RadioButtonGroup, Toggle
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
import pandas as pd
from sqlalchemy import create_engine, inspect
import datetime
import os
from pathlib import Path
from bokeh.models import Line

from collections import defaultdict

db_dict = {'garmin': 'garmin.db',
            'activities': 'garmin_activities.db',
            'monitoring': 'garmin_monitoring.db',
            'garmin_summary': 'garmin_summary.db',
            'summary': 'summary.db'}

today = datetime.date.today()
date_range_slider = DateRangeSlider(value=(today - datetime.timedelta(days=7), today),
                                    start=today - datetime.timedelta(days=30),
                                    end=today + datetime.timedelta(days=1))

def update_plots(p):
    callback = CustomJS(args=dict(p=p), code="""
        p.x_range.start = cb_obj.value[0]
        p.x_range.end = cb_obj.value[1]
        p.x_range.change.emit()
        """)
    return callback


# Callback function for DateRangeSlider
def load_dbs(db_dict):
    recursive_dict = lambda: defaultdict(recursive_dict)
    dfs_dict = recursive_dict()

    for db, fname in db_dict.items():
        db_path = str(Path.home()) + '/HealthData/DBs/' + fname
        engine = create_engine('sqlite:////' + db_path)

        cnx = engine.connect()
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        for table in table_names:
            dfs_dict[db][table] = pd.read_sql_table(table, cnx)
            # print(dfs_dict[db][table])
    return dfs_dict


def plot_anything(dfs_dict, db, table, p, x='timestamp', y=None, index_col=None):
    if index_col == None:
        index_col = x
    
    dfs_dict[db][table] = dfs_dict[db][table].set_index(index_col).sort_index()
    source = ColumnDataSource(dfs_dict[db][table])
    p.line(x=x,y=y,source=source,name=y)

    return p

def toggle_plots(p,name):
    gr = p.select(name=name)
    callback = CustomJS(args=dict(gr=gr), code="""
        gr[0].visible = this.active
        """)
    return callback

def plot_hr(dfs_dict,p):
    db = 'monitoring'
    table = 'monitoring_hr'
    index_col = 'timestamp'
    x = 'timestamp'
    y = 'heart_rate'

    dfs_dict[db][table] = dfs_dict[db][table].set_index(index_col).sort_index()
    source = ColumnDataSource(dfs_dict[db][table])
    
    p.line(x=x,y=y,source=source,name=y, color='red')

    return p
 

def plot_stress(dfs_dict,p):
    db = 'garmin'
    table = 'stress'
    index_col = 'timestamp'
    x = 'timestamp'
    y = 'stress'

    dfs_dict[db][table] = dfs_dict[db][table].set_index(index_col).sort_index()
    source = ColumnDataSource(dfs_dict[db][table])
    
    p.vbar(x=x,top=y,source=source,name=y)

    return p
    
# Load dbs into pandas dicts
dfs_dict = load_dbs(db_dict)

#Initiate figure
p = figure(x_axis_type='datetime')

#Plot metrics
# p = plot_anything(dfs_dict, 'monitoring', 'monitoring_hr',p, x='timestamp', y='heart_rate')
# p = plot_anything(dfs_dict, 'garmin', 'stress',p, x='timestamp', y='stress')

p = plot_hr(dfs_dict,p)
p = plot_stress(dfs_dict,p)

#Aesthetics
p.sizing_mode = 'scale_width'
p.aspect_ratio = 3


# Toggle stress
toggle_stress = Toggle(label='Stress', button_type='success')
# Toggle stress plot button callback
cb_stress = toggle_plots(p,'stress')
toggle_stress.js_on_click(cb_stress)

#date range slider callback
for plot in [p]:
    callback = update_plots(plot)
    date_range_slider.js_on_change('value_throttled', callback)

#Layout
l = layout([
            [date_range_slider],
            [p],
            [toggle_stress]
])
# Scale layout
l.sizing_mode = 'scale_width'


curdoc().add_root(l)

# show(l)



