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
import datetime
import os
from pathlib import Path


def plot_dnb():
    brain_file = str(Path.home()) + '/.brainworkshop/data/stats.txt'
    
    brain_columns = ['time', 'dnb', 'percent', 'mode', 'back', 'ticks_per_trial', 'num_trials_total',
                  'manual','session_number','pos1','audio','color','visvis','audiovis', 'arithmetic',
                  'image','visaudio','audio2','pos2','pos3','pos4','vis1','vis2','vis3','vis4',
                  'tickstimesnumtimestrials','None']
    
    # Pandas stuff
    df = pd.read_csv(brain_file, names=brain_columns)
    # convert to datetime and sort 
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time').sort_index()
    #compute score
    df['score'] = df['back'] * 100 + df['percent']

    # plot stuff


    tool = [('d', '$metric.score'), ('a', '$index')]

    p = figure(x_axis_type='datetime', tooltips=tool)

    p.sizing_mode ='scale_width'
    p.aspect_ratio = 3
    p.legend.location = 'top_right'
    p.legend.click_policy = 'hide'

    for nback in df['dnb'].unique():
        
        #select based on nback and groupby date
        df_sel = df.loc[df['dnb'] == nback]
        groups = df_sel.groupby([df_sel.index.date])
        
        #compute dategroup metrics
        daily_mean, daily_min, daily_max = groups.mean(), groups.min(), groups.max()
        daily_std = groups.std()
        lower = daily_mean - daily_std
        upper = daily_mean + daily_std
        
        #CDS and add whisker layout 
        source = ColumnDataSource(data=dict(base=lower.index,lower=lower.score, upper=upper.score))
        p.add_layout(Whisker(source=source,base='base', upper='upper',lower='lower'))
        
        # plot daily stuff
        sizes = [groups.size(), 8, 8]
        markers = ['hex', 'inverted_triangle', 'triangle']
        for index,metric in enumerate([daily_mean,daily_min,daily_max]):
            p.scatter(x=metric.index,
                      y=metric['score'],
                      size=sizes[index],
                      marker=markers[index],
                      legend_label=nback)
        # p.hover([("daily_mean", "$score")])

    return p

# Pandas df stuff

