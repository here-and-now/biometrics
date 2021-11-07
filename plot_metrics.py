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
        
        for table in table_names:
            dfs_dict[db][table] = pd.read_sql_table(table, cnx)
            # print(dfs_dict[db][table])


today = datetime.date.today()
date_range_slider = DateRangeSlider(value=(today - datetime.timedelta(days=7), today),
                                    start=today - datetime.timedelta(days=30),
                                    end=today + datetime.timedelta(days=1))
load_dbs()
# iniate dataframe and bokeh source
p = figure(x_axis_type='datetime')

#date range slider callback
for plot in [p]:
    callback = update_plots(plot)
    date_range_slider.js_on_change('value_throttled', callback)

# radio button group change listeners
l = layout([
            [date_range_slider],
            [p]
])
curdoc().add_root(l)

# show(l)



