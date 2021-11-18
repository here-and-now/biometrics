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

from collections import defaultdict

# from bokeh.palettes import 

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

def plot_dnb(df):
    # df['norm'] = df['total_sleep'].apply(lambda x: x.hour * 60 + x.minute)
    # df['norm'] = (df['norm'] - df['norm'].min()) / (df['norm'].max() - df['norm'].min()) * 100
    
    nbacks = df['dnb'].unique()
    uni_days = df.index.map(lambda x: x.date()).unique()
    
    p = figure(x_axis_type='datetime')
    for nback in nbacks:
        df_sel = df.loc[df['dnb'] == nback]
        group = df_sel.groupby([df_sel.index.date])

        source = ColumnDataSource(df_sel)
      
        p.scatter(x=group.mean().index,
                  y=group.mean()['score'],
                  legend_label=nback) 

    return p

# Pandas df stuff
df = pd.read_csv(str(Path.home()) + '/.brainworkshop/data/stats.txt')
df.columns = ['time', 'dnb', 'percent', 'mode', 'back', 'ticks_per_trial', 'num_trials_total',
              'manual','session_number','pos1','audio','color','visvis','audiovis', 'arithmetic',
              'image','visaudio','audio2','pos2','pos3','pos4','vis1','vis2','vis3','vis4',
              'ticks_per_trial_times_tick_duration_times_num_trials_total','None']
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time').sort_index()
df['score'] = df['back'] * 100 + df['percent']


# plot stuff
p = plot_dnb(df)

p.sizing_mode ='scale_width'
p.aspect_ratio = 3
p.legend.location = 'top_right'
p.legend.click_policy = 'hide'


for plot in [p]:
    callback = update_plots(plot)
    date_range_slider.js_on_change('value_throttled', callback)

# #Layout
l = layout([
            [date_range_slider],
            [p],
])
 # Scale layout
l.sizing_mode = 'scale_width'


curdoc().add_root(l)

# show(l)



