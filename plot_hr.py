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


# connect sql db
engine = create_engine('sqlite:///garmin_summary.db')
cnx = engine.connect()

# Read sql into dataframe
df = pd.read_sql('intensity_hr', cnx,index_col='timestamp')
# df.index= pd.to_datetime(df.index)

# Inspect table names
inspector = inspect(engine)
table_names = inspector.get_table_names()
# column_names = [column.name for column in cnx.columns]

column_names = inspector.get_columns('intensity_hr')

print(table_names)
print(column_names)

radio_button_group = RadioButtonGroup(labels=table_names)



source = ColumnDataSource(df)

# bokeh plot stuff
plot_w, plot_h = 1800, 500

p = figure(title='Heart Rate',
            x_axis_type='datetime',
            plot_width=plot_w,
            plot_height=plot_h)

p.line(x='timestamp',
       y='heart_rate',
       source=source)

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

for plots in [p]:
    callback = update_plots(plots)
    date_range_slider.js_on_change('value_throttled', callback)


l = layout([
            [radio_button_group],
            [date_range_slider],
            [p]
])
# curdoc().add_root(l)

show(l)



