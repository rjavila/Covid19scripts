import datetime
import pandas as pd
import numpy as np
from bokeh.io import show, curdoc
from bokeh.plotting import figure
from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel, Legend
from bokeh.models.widgets import CheckboxGroup, Button, RadioButtonGroup
from bokeh.layouts import column, row, WidgetBox, gridplot, layout
from bokeh.palettes import Category20, Category20c, Category20b, Set3

from covidplots import get_data

#colors = Category20[20] + Category20b[20] +  Category20c[10]
colors_l = Category20[20] + Category20b[20] +  Category20c[20]

# Read in data
data, pops = get_data.get_data("usa")
data = data.diff()
data["date"] = data.index

CAPITA = 100000

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
    colors = colors_l[:len(region_list)]
    
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
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.major_label_text_font_size = '12pt'

    return p

# Function to make the plot
def make_plot(src):

    # Blank plot with correct labels
    p = figure(plot_width = 1500, plot_height = 1000, 
              title = 'Covid-19 Cases',
              x_axis_type="datetime", x_range=(xleft, xright))
    p.multi_line(source=src, xs="xs", ys="ys", color="colors", 
                 line_width=3, legend_field="names")              

    p.legend.location = "top_left"
    # Hover tool with vline mode
    hover = HoverTool(tooltips=[('State', '@name'), 
                                ('Cases', '@top')],
                      mode='vline')

    p.add_tools(hover)

#    p.legend.click_policy = 'hide'

    # Styling
    p = style(p)

    return p

# Update the plot based on selections
def update(attr, old, new):
    regions_to_plot = [region_selection.labels[i] for i in region_selection.active]

    new_src = make_dataset(regions_to_plot)

    src.data.update(new_src.data)

def select_all_update():
    region_selection.active = list(range(len(all_regions)))

def deselect_all_update():
    region_selection.active = []

def update_scaling(attr, old, new):
    regions_to_plot = [region_selection.labels[i] for i in region_selection.active]
    if radio_buttons.active == 0:
        new_src = make_dataset(regions_to_plot)
    else:
        new_src = make_dataset(regions_to_plot, percapita=True)
    src.data.update(new_src.data)

# Radio button group for selecting per capita
radio_buttons = RadioButtonGroup(labels=["Unscaled", "Per 100000"], active=0)
radio_buttons.on_change("active", update_scaling)

# Select and Deselect all
select_all = Button(label="Select All")
select_all.on_click(select_all_update)
deselect_all = Button(label="Unselect All")
deselect_all.on_click(deselect_all_update)

# CheckboxGroup to select region to display
region_selection = CheckboxGroup(labels=all_regions, active = [0, 1], css_classes =["custom_checkbox"])
region_selection.on_change('active', update)

# Find the initially selected regions
initial_regions = [region_selection.labels[i] for i in region_selection.active]
src = make_dataset(initial_regions)
p = make_plot(src)

# Put controls in a single element
widgets = column(radio_buttons, select_all, deselect_all, region_selection)#, width=200) 
#controls = WidgetBox(region_selection, width=100)

# Create a row layout
#grid = layout(children=[[controls, p]], spacing=1)
grid = row(widgets, p, spacing=50)

# Add it to the current document (displays plot)
curdoc().add_root(grid)

