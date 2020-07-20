import datetime
import pandas as pd
import numpy as np
from bokeh.io import show, curdoc
from bokeh.plotting import figure
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel, Legend
from bokeh.models.widgets import CheckboxGroup, Button, RadioButtonGroup
from bokeh.layouts import column, row, WidgetBox, gridplot, layout
from bokeh.palettes import Category20, Category20c, Category20b, Set3

from covidplots import get_data

# All region names
STATES = ['Alabama','Alaska','Arizona','Arkansas','California',
          'Colorado','Connecticut','Delaware','Florida',
          'Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa',
          'Kansas','Kentucky','Louisiana','Maine','Maryland',
          'Massachusetts','Michigan','Minnesota','Mississippi',
          'Missouri','Montana','Nebraska','Nevada','New Hampshire',
          'New Jersey','New Mexico','New York','North Carolina',
          'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania',
          'Rhode Island','South Carolina','South Dakota','Tennessee',
          'Texas','Utah','Vermont','Virginia','Washington',
          'West Virginia','Wisconsin','Wyoming']
all_regions = STATES
all_regions.sort()
all_regions1 = all_regions[:25]
all_regions2 = all_regions[25:]

# Read in data
data, pops = get_data.get_data("usa")
data = data.diff()
data = data.rolling(7, center=True, min_periods=2).mean()

# Sort and get worst 9 states
data_sorted = data.T.sort_values(data.index[-1], ascending=False).T
worst9 = data_sorted.iloc[:, :9] 
worst9names = worst9.columns.values
worst9inds1 = [x for x in range(len(all_regions1)) if all_regions1[x] in worst9names]
worst9inds2 = [x for x in range(len(all_regions2)) if all_regions2[x] in worst9names]

# Add the index (date) as a column
data["date"] = data.index

CAPITA = 100000

# Define immutable colors for each state
#colors = Category20[20] + Category20b[20] +  Category20c[10]
colors_l = Category20[20] + Category20b[20] +  Category20c[20]
colors_d = dict(zip(all_regions, colors_l[:len(all_regions)]))

# Set some constants
xleft = datetime.datetime(2020, 3, 1)
xright = datetime.datetime.now() + datetime.timedelta(days=1)

# Dataset based on selected regions
def make_dataset(region_list, percapita=False):

    xs = [data["date"] for x in range(len(region_list))]
    if percapita is True:
        ys = [CAPITA * data[region].div(pops[region].iloc[0]) for region in region_list] 
    else:
        ys = [data[region].values for region in region_list]          
    names = [np.array([region]) for region in region_list]
    colors = [colors_d[x] for x in region_list]
    
    dct = {"xs": xs, "ys": ys, "names": names, "colors": colors}
    src = ColumnDataSource(dct)

    return src 

# Styling for a plot
def style(p):
    # Title 
    p.title.align = 'center'
    p.title.text_font_size = '20pt'

    # Axis titles
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_style = 'bold'

    # Tick labels
    p.xaxis.major_label_text_font_size = '15pt'
#    p.xaxis.major_label_text_font_style = 'bold'
    p.yaxis.major_label_text_font_size = '15pt'
#    p.yaxis.major_label_text_font_style = 'bold'
    p.xaxis.formatter=DatetimeTickFormatter(months=["%b %Y"])

    hover = HoverTool(tooltips=[("State", "@names"),
                                ("Cases", "$data_y{int}"),
                                ("Date", "$data_x{%b %d %Y}")],
                      formatters={"$data_x": "datetime"},)     
    hover.point_policy="snap_to_data"
    p.add_tools(hover)                                            

    return p

# Function to make the plot
def make_plot(src):

    # Blank plot with correct labels
    p = figure(plot_width = 1500, plot_height = 1000, 
              title = 'New Daily Covid-19 Cases, 7-day Average',
              x_axis_type="datetime", x_range=(xleft, xright))
    p.multi_line(source=src, xs="xs", ys="ys", color="colors", 
                 line_width=3, legend_field="names")              

    p.legend.location = "top_left"
    p.legend.label_text_font_size = "13pt"
#    p.legend.click_policy = 'hide'

    # Styling
    p = style(p)

    return p

# Update the plot based on selections
def update(attr, old, new):
    regions_to_plot = [region_selection1.labels[i] for i in region_selection1.active] + [region_selection2.labels[i] for i in region_selection2.active]

    if radio_buttons.active == 0:
        new_src = make_dataset(regions_to_plot)
    else:
        new_src = make_dataset(regions_to_plot, percapita=True)
    
    src.data.update(new_src.data)

def select_all_update():
    region_selection1.active = list(range(len(all_regions1)))
    region_selection2.active = list(range(len(all_regions2)))

def deselect_all_update():
    region_selection1.active = []
    region_selection2.active = []

def worst9_update():
    region_selection1.active = worst9inds1
    region_selection2.active = worst9inds2

def update_scaling(attr, old, new):
    regions_to_plot = [region_selection1.labels[i] for i in region_selection1.active] + [region_selection2.labels[i] for i in region_selection2.active]
    if radio_buttons.active == 0:
        new_src = make_dataset(regions_to_plot)
    else:
        new_src = make_dataset(regions_to_plot, percapita=True)
    src.data.update(new_src.data)

# Radio button group for selecting per capita
radio_buttons = RadioButtonGroup(labels=["Unscaled", "Per 100000"], active=0, css_classes=["custom_button"])
radio_buttons.on_change("active", update_scaling)

# Select and Deselect all
select_all = Button(label="Select All", css_classes=["custom_button"])
select_all.on_click(select_all_update)
deselect_all = Button(label="Unselect All", css_classes=["custom_button"])
deselect_all.on_click(deselect_all_update)

# Button for worst 9
worst9 = Button(label="Show Worst 9 States", css_classes=["custom_button"])
worst9.on_click(worst9_update)

# CheckboxGroup to select region to display
region_selection1 = CheckboxGroup(labels=all_regions1, active = [0, 1], css_classes =["custom_checkbox"])
region_selection2 = CheckboxGroup(labels=all_regions2, active = [], css_classes =["custom_checkbox"])
region_selection1.on_change('active', update)
region_selection2.on_change('active', update)

# Find the initially selected regions
initial_regions = [region_selection1.labels[i] for i in region_selection1.active]
src = make_dataset(initial_regions)
p = make_plot(src)

# Put controls in a single element
widgets = column(radio_buttons, 
                 row(select_all, deselect_all, width=350), 
                 worst9,
                 row(region_selection1, region_selection2, width=350),
                 width=350, height=1000)#, width=200) 
#controls = WidgetBox(region_selection, width=100)

# Create a row layout
#grid = layout(children=[[controls, p]], spacing=1)
grid = row(widgets, p, spacing=75)

# Add it to the current document (displays plot)
curdoc().add_root(grid)
