from bokeh.plotting import figure,show
from bokeh.io import save
from bokeh.models import HoverTool
from bokeh.models.axes import LinearAxis
from bokeh.layouts import layout
from bokeh.io import show
from bokeh.models import CustomJS, DateRangeSlider, ColumnDataSource
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, curdoc
import pandas as pd
from sqlalchemy import create_engine, inspect

# df = pd.read
engine = create_engine('sqlite:///garmin_summary.db')
inspector = inspect(engine)
cnx = engine.connect()

df = pd.read_sql('intensity_hr', cnx,index_col='timestamp')

print(inspector.get_table_names())

source = ColumnDataSource(df)

p = figure(title='test')
p.line(x='timestamp', y='heart_rate', source=source)

print(df['heart_rate'])

# l = layout([p])
# curdoc().add_root(l)

show(p)



print(df)
