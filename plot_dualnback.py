from bokeh.plotting import figure,show
from bokeh.io import save
from bokeh.models import HoverTool
from bokeh.models.axes import LinearAxis
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.models import CustomJS, DateRangeSlider, ColumnDataSource, CheckboxButtonGroup, RadioButtonGroup, Toggle, Label, LabelSet, Span, Whisker
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
        groups = df_sel.groupby([df_sel.index.date])

        # source = ColumnDataSource(df_sel)
        
        daily_mean, daily_min, daily_max = groups.mean(), groups.min(), groups.max()
        daily_std = groups.std()
        
        lower = daily_mean - daily_std
        upper = daily_mean + daily_std

        print(lower)
        print(upper)
        source = ColumnDataSource(data=dict(score=, lower=lower, upper=upper))
        p.add_layout(Whisker(base=upper.index,upper=upper.score, lower=lower.score))

        p.scatter(x=daily_mean.index,
                  y=daily_mean['score'],
                  legend_label=nback) 
        p.scatter(x=daily_min.index,
                  y=daily_min['score'],
                  legend_label=nback) 

        p.scatter(x=daily_max.index,
                  y=daily_max['score'],
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


###### garbage whisker
        # q1 = groups.quantile(q=0.25)
        # q2 = groups.quantile(q=0.5)
        # q3 = groups.quantile(q=0.75)
        # iqr = q3 - q1
        # upper = q3 + 1.5*iqr
        # lower = q1 - 1.5*iqr
        # print(upper)

        # qmin = groups.quantile(q=0.00)
        # qmax = groups.quantile(q=1.00)
        # print("-----------------" , qmin)
        # upper.score = [min([x,y]) for (x,y) in zip(list(qmax.iloc[:,0]),upper.score)]
        # lower.score = [max([x,y]) for (x,y) in zip(list(qmin.iloc[:,0]),lower.score)]

        # print(upper.score)
        # p.segment(upper.index, upper.score, upper.index, q3.score, line_width=2, line_color="black")
        # p.segment(lower.index, lower.score, lower.index, q1.score, line_width=2, line_color="black")


        # p.vbar(q2.index, 0.7, q2.score, q3.score, fill_color="#E08E79", line_color="black")
        # p.vbar(q1.index, 0.7, q1.score, q2.score, fill_color="#3B8686", line_color="black")


        # p.rect(lower.index, lower.score, 0.2, 0.01, line_color="black")
        # p.rect(upper.index, upper.score, 0.2, 0.01, line_color="black")
## garbage end


