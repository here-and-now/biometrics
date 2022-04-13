import datetime
import os
import pandas as pd


from bokeh.plotting import figure,show
from bokeh.io import save
from bokeh.models import HoverTool
from bokeh.models.axes import LinearAxis
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.models import CustomJS, DateRangeSlider, ColumnDataSource, CheckboxButtonGroup, RadioButtonGroup, Toggle, Label, LabelSet, Span
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
from bokeh.models import Line 
from bokeh.models.ranges import Range1d

from sqlalchemy import create_engine, inspect
from collections import defaultdict
from pathlib import Path

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


def plot_hrv_metrics(dfs_dict, activity, p=None):
    db = 'activities'
    table = activity
    index_col = 'timestamp'
    
    df = dfs_dict[db][table]
    df = df.set_index(index_col).sort_index()#.dropna()

    source = ColumnDataSource(df)
    
    p = figure(x_axis_type='datetime', y_range=(0,200))

    p.line(x='timestamp', y='hrv_rmssd', source=source, color='black', width=width_high, alpha=1, legend_label='RMSSD')

    p.line(x='timestamp', y='hrv_pnn20', source=source, color='red', dash='dotted', width=width_low, alpha=alpha_high, legend_label='pnn20')
    p.line(x='timestamp', y='hrv_pnn50', source=source, color='red', dash='dashed', width=width_low, alpha=alpha_high, legend_label='pnn50')

    p.line(x='timestamp', y='hrv_sdrr_f', source=source, color='blue', dash='dotted', width=width_low, alpha=alpha_low, legend_label='SDRR_start')
    p.line(x='timestamp', y='hrv_sdrr_l', source=source, color='blue', dash='dashed', width=width_low, alpha=alpha_low, legend_label='SDDR_end')
    
    p.line(x='timestamp', y='min_hr', source=source, color='orange', dash='dashdot', width=width_low, alpha=alpha_low, legend_label='min_hr')
    
    if activity=='meditation_sessions':
        p.extra_y_ranges = {'time': Range1d(start=0, end=35) }
        p.add_layout(LinearAxis(y_range_name='time'), 'right')
        p.vbar(x='timestamp', top='elapsed_time', source=source, bottom=0,y_range_name='time')
    
    # p.line(x='timestamp', y='hrv_btb', source=source, color='green')
    # p.line(x='timestamp', y='stress_hrpa', source=source)
    return p


alpha_low = 0.5
alpha_high = 0.7
width_low = 2
width_high = 3


# Load dbs into pandas dicts
dfs_dict = load_dbs(db_dict)

#Initiate figure
p_meditation = plot_hrv_metrics(dfs_dict, 'meditation_sessions')
p_test_hrv = plot_hrv_metrics(dfs_dict, 'test_hrv_sessions')

p_meditation.title = 'Meditation'
p_test_hrv.title = 'Test HRV'

for p in [p_meditation, p_test_hrv]:
    p.legend.location = 'top_right'
    p.legend.click_policy="hide"
    #Aesthetics
    p.sizing_mode = 'scale_width'
    p.aspect_ratio = 5

#Layout
l = layout([
            [p_meditation],
            [p_test_hrv]
])

# Scale layout
l.sizing_mode = 'scale_width'

curdoc().add_root(l)




