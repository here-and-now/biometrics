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
import sqlalchemy 

# df = pd.read
cnx = sqlalchemy.create_engine('sqlite:///garmin_summary.db').connect()

df = pd.read_sql_table('summary', cnx)


print(df)
