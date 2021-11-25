from bokeh.plotting import figure,show
from bokeh.io import save
from bokeh.models import HoverTool
from bokeh.models.axes import LinearAxis
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.models import CustomJS, DateRangeSlider, ColumnDataSource, CheckboxButtonGroup, RadioButtonGroup, Toggle, Label, LabelSet, Span
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
import pandas as pd
from sqlalchemy import create_engine, inspect
import datetime
import os
from pathlib import Path
from bokeh.models import Line

from plot_dualnback import plot_dnb

from collections import defaultdict

# from bokeh.palettes import 

db_dict = {'garmin': 'garmin.db',
            'activities': 'garmin_activities.db',
            'monitoring': 'garmin_monitoring.db',
            'garmin_summary': 'garmin_summary.db',
            'summary': 'summary.db'}

today = datetime.date.today()
date_range_slider = DateRangeSlider(value=(today - datetime.timedelta(days=7), today),
                                    start=today - datetime.timedelta(days=30),
                                    end=today + datetime.timedelta(days=1))

# Callback function for DateRangeSlider
def update_plots(p):
    callback = CustomJS(args=dict(p=p), code="""
        p.x_range.start = cb_obj.value[0]
        p.x_range.end = cb_obj.value[1]
        p.x_range.change.emit()
        """)
    return callback

# Returns callback for toggle button presses
def toggle_plots(p,name):
    gr = p.select(name=name)
    callback = CustomJS(args=dict(gr=gr), code="""
        gr[0].visible = this.active
        """)
    return callback

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

# Plot Heart rate
def plot_hr(dfs_dict,p):
    db = 'monitoring'
    table = 'monitoring_hr'
    index_col = 'timestamp'
    x = 'timestamp'
    y = 'heart_rate'

    df = dfs_dict[db][table]
    df = df.set_index(index_col).sort_index().dropna()
    source = ColumnDataSource(df)

    
    p.line(x=x,y=y,source=source,name=y, color='red', legend_label='Heart rate')

    return p
 
# Plot stress as proxy for HRV
def plot_stress(dfs_dict,p):
    db = 'garmin'
    table = 'stress'
    index_col = 'timestamp'
    x = 'timestamp'
    y = 'stress'

    df = dfs_dict[db][table]
    df = df.set_index(index_col).sort_index().dropna()
    source = ColumnDataSource(df)

    
    p.vbar(x=x,top=y,source=source,name=y, legend_label='Stress', alpha=0.5, color='gray')

    return p

def plot_sleep(dfs_dict,p):
    db = 'garmin'
    table = 'sleep'
    index_col = 'day'
    start = 'start'
    end = 'end'

    df = dfs_dict[db][table]
    df = df.set_index(index_col).sort_index().dropna()
    source = ColumnDataSource(df)

    y_offset = -5 
    p.scatter(x=start,
             y=y_offset,
             source=source,
             marker='star',
             color='yellow')
    p.scatter(x=end,
             y=y_offset,
             source=source,
             marker='star_dot',
             color='yellow')

    for start, end in zip(source.data['start'], source.data['end']):
        
        p.line(x=[start,end],y=[-5,-5])
        #TODO: annotate sleep time with total sleep time label
        # spa = Span(location='start', dimension='timestamp')
    # labels = LabelSet(x='start',y='end',text='total_sleep', level='glyph', source=source, y_offset=-10, render_mode='canvas')
    # p.add_layout(labels)
    return p


def plot_sleep_metrics(dfs_dict,p=None):
    db = 'garmin'
    table = 'sleep'
    index_col = 'day'
    start = 'start'
    end = 'end'
    total_sleep = 'total_sleep'
    
    df = dfs_dict[db][table]
    df = df.set_index(index_col).sort_index().dropna()

    df['norm'] = df['total_sleep'].apply(lambda x: x.hour * 60 + x.minute)
    df['norm'] = (df['norm'] - df['norm'].min()) / (df['norm'].max() - df['norm'].min()) * 100
    
    source = ColumnDataSource(df)

    p = figure(x_axis_type='datetime')
    p.scatter(x='day', y='total_sleep', size='norm', source=source)

    return p

 
# Load dbs into pandas dicts
dfs_dict = load_dbs(db_dict)

#Initiate figure
p = figure(x_axis_type='datetime')
p_sleep = plot_sleep_metrics(dfs_dict)

#Plot metrics
p = plot_hr(dfs_dict,p)
P = plot_stress(dfs_dict,p)
p = plot_sleep(dfs_dict,p)

p.legend.location = 'top_right'
p.legend.click_policy="hide"
#Aesthetics
p.sizing_mode = 'scale_width'
p.aspect_ratio = 3

p_dnb = plot_dnb()


# Toggle stress/HR
toggle_stress = Toggle(label='Stress', button_type='success')
cb_stress = toggle_plots(p,'stress')
toggle_stress.js_on_click(cb_stress)

toggle_hr = Toggle(label='Heart rate', button_type='success')
cb_hr = toggle_plots(p,'heart_rate')
toggle_hr.js_on_click(cb_hr)

#date range slider callback
for plot in [p]:
    callback = update_plots(plot)
    date_range_slider.js_on_change('value_throttled', callback)

#Layout
l = layout([
            [date_range_slider],
            [p],
            [toggle_hr,toggle_stress],
            [p_sleep, p_dnb]
])
# Scale layout
l.sizing_mode = 'scale_width'


curdoc().add_root(l)

# show(l)



