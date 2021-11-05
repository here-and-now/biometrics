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

def get_column_names():
    return [cn['name'] for cn in inspector.get_columns(table_names[rbg_tables.active])]


def refresh_db(attr,old,new):
    rbg_tables.update(labels=table_names)
    table = table_names[rbg_tables.active]
    df = pd.read_sql(table, cnx,index_col='timestamp')

    column_names = get_column_names()
    rbg_columns_x.update(labels=column_names)
    rbg_columns_y.update(labels=column_names)

    source.update(data=df)
    

def change_plot(attrname, old, new):
    column_names = get_column_names()
    x = column_names[rbg_columns_x.active]
    y = column_names[rbg_columns_y.active]

    print('Selected x: ', x)
    print('Selected y: ', y)

    for line in list(p.renderers):
        p.renderers.remove(line)

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


today = datetime.date.today()
date_range_slider = DateRangeSlider(value=(today - datetime.timedelta(days=7), today),
                                    start=today - datetime.timedelta(days=30),
                                    end=today + datetime.timedelta(days=1))

# connect sql db
engine = create_engine('sqlite:///garmin_monitoring.db')
cnx = engine.connect()

#inspect db and get table names
inspector = inspect(engine)
table_names = inspector.get_table_names()

# populate radiobuttongroups
rbg_tables = RadioButtonGroup(labels=table_names,active=3)

column_names = get_column_names()
rbg_columns_x = RadioButtonGroup(labels=column_names,active=0)
rbg_columns_y = RadioButtonGroup(labels=column_names,active=1)

# iniate dataframe and bokeh source
active_table = table_names[rbg_tables.active]
df = pd.read_sql(active_table, cnx,index_col='timestamp')
source = ColumnDataSource(df)

refresh_db(None,None,None)

plot_w, plot_h = 1800, 500

p = figure(title='Heart Rate',
            x_axis_type='datetime',
            plot_width=plot_w,
            plot_height=plot_h)

change_plot(None,None,None)

#date range slider callback
for plot in [p]:
    callback = update_plots(plot)
    date_range_slider.js_on_change('value_throttled', callback)

# radio button group change listeners
rbg_tables.on_change('active', refresh_db)
rbg_columns_x.on_change('active', change_plot)
rbg_columns_y.on_change('active', change_plot)

l = layout([
            [rbg_tables],
            [rbg_columns_x],
            [rbg_columns_y],
            [date_range_slider],
            [p]
])
curdoc().add_root(l)

# show(l)



