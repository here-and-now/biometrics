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

df = pd.read_sql_table('summary', cnx)

print(inspector.get_table_names())


print(df)
