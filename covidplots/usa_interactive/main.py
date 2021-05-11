"""
Create an interactive plot of covid-19 cases for each state, using Bokeh.

Run instructions:
From the Covid19scripts/covidplots directory, run:
> bokeh serve --show interactive

This will open a tab in your browser with the plot. 
"""

import datetime
import pandas as pd
import numpy as np
from bokeh.io import show, curdoc
from bokeh.plotting import figure
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models.widgets import CheckboxGroup, Button, RadioButtonGroup
from bokeh.layouts import column, row
from bokeh.palettes import Category20, Category20c, Category20b

from covidplots import get_data

#-----------------------------------------------------------------------------#
# Define constants

# Define region names
# For now, only optimized for USA states
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
          'West Virginia','Wisconsin','Wyoming','District of Columbia']
all_regions = STATES
all_regions.sort()
# Split into two lists so that we can have two columns of checkboxes
all_regions1 = all_regions[:25]
all_regions2 = all_regions[25:]

# Define per capita number
CAPITA = 100000

# Define immutable colors for each state
colors_l = Category20[20] + Category20b[20] +  Category20c[20]
colors_d = dict(zip(all_regions, colors_l[:len(all_regions)]))

# Set x limits to be March 1 -> now + 1 day
xleft = datetime.datetime(2020, 3, 1)
xright = datetime.datetime.now() + datetime.timedelta(days=1)

#-----------------------------------------------------------------------------#
# Read and handle data

# Read in data for USA
dtype_kwargs = {"cases": {"deaths": False, "vax": False}, 
          "deaths": {"deaths": True, "vax": False}, 
          "vax": {"deaths": False, "vax": True},
          "percvax": {"deaths": False, "vax": True}}
data_d = {}
for dtype in dtype_kwargs:
    kwargs = dtype_kwargs[dtype]
    data, pops = get_data.get_data("usa", **kwargs)
    if dtype in ["vax", "percvax"]:
        partialdata,data = get_data.vax_by_region(data)
    if dtype == "percvax":
        data = data/pops * 100.
    else:
        data = data.diff()
        # Use 7 day average as the defacto data
        data = data.rolling(7, center=True, min_periods=2).mean()
    
    data_d[dtype] = {"data": data}
    # Sort and determine worst and best 9 states, both raw and per capita
    subs = {"worst": [0,9], "best": [-9,len(data)]} 
    for rang in subs:
        data_sorted = data.T.sort_values(data.index[-1], ascending=False).T
        sub = data_sorted.iloc[:, subs[rang][0]:subs[rang][1]] 
        names = sub.columns.values
        inds1 = [x for x in range(len(all_regions1)) if all_regions1[x] in names]
        inds2 = [x for x in range(len(all_regions2)) if all_regions2[x] in names]
        data_capita = CAPITA * data.div(pops.iloc[0], axis="columns")
        data_capita_sorted = data_capita.T.sort_values(data_capita.index[-1], ascending=False).T
        sub_capita = data_capita_sorted.iloc[:, subs[rang][0]:subs[rang][1]] 
        names_capita = sub_capita.columns.values
        inds1_capita = [x for x in range(len(all_regions1)) if all_regions1[x] in names_capita]
        inds2_capita = [x for x in range(len(all_regions2)) if all_regions2[x] in names_capita]
        data_d[dtype][f"{rang}9inds1"] = inds1
        data_d[dtype][f"{rang}9inds2"] = inds2
        data_d[dtype][f"{rang}9inds1_capita"] = inds1_capita
        data_d[dtype][f"{rang}9inds2_capita"] = inds2_capita
    
    # Add the index (date) as a column for convenience
    data["date"] = data.index

#-----------------------------------------------------------------------------#

def make_data_src(region_list, percapita=False, dtype="cases"):
    """
    Create and update a bokeh data source depending on the selected regions
    to display.
    Args:
        region_list (array-like): Names of regions to display.
        percapita (Bool): If True, data is scaled by population.
    Returns:
        src (`obj: bokeh.ColumnDataSource`): bokeh ColumnDataSource object 
            containing the case numbers as a function of date, the name
            of the region, and color of the region.
    """

    worst9.button_type = "default"

    data = data_d[dtype]["data"]

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

#-----------------------------------------------------------------------------#

def style(p):
    """
    Define the styling of the bokeh plot, including fonts and hover tool.
    Args:
        p (`obj: bokeh.figure`): bokeh figure object for display.
    Return:
        p (`obj: bokeh.figure`): bokeh figure object for display, with updated
            styling added.
    """

    # Title 
    p.title.align = 'center'
    p.title.text_font_size = '20pt'

    # Axis titles
    # Right now there are no axis labels.
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.axis_label_text_font_style = 'bold'

    # Tick labels
    p.xaxis.major_label_text_font_size = '15pt'
    p.yaxis.major_label_text_font_size = '15pt'
    p.xaxis.formatter=DatetimeTickFormatter(months=["%b %Y"])

    hover = HoverTool(tooltips=[("State", "@names"),
                                ("Cases", "$data_y{int}"),
                                ("Date", "$data_x{%b %d %Y}")],
                      formatters={"$data_x": "datetime"},)     
    p.add_tools(hover)                                            

    return p

#-----------------------------------------------------------------------------#

def make_plot(src):
    """
    Create the bokeh figure and add data.
    Args:
        src (`obj: bokeh.ColumnDataSource`): bokeh ColumnDataSource object
    Returns:
        p (`obj: bokeh.figure`): bokeh figure object for display.
    """

    # Create figure
    p = figure(plot_width = 1500, plot_height = 1000, 
              title = 'New Daily Covid-19 Cases, 7-day Average',
              x_axis_type="datetime", x_range=(xleft, xright))
    p.sizing_mode = 'scale_both'
    # Create a line for each region
    p.multi_line(source=src, xs="xs", ys="ys", color="colors", 
                 line_width=3, legend_field="names")              

    p.legend.location = "top_left"
    p.legend.label_text_font_size = "13pt"

    # Style figure
    p = style(p)

    return p

#-----------------------------------------------------------------------------#

def update_plot(attr, old, new):
    """
    Boilerplate function for updating plot using a new bokeh data source.
    This is triggered when the regions to display is changed, either via
    checkbox selection or button activation (e.g. "select all")
    """

    regions_to_plot = [region_selection1.labels[i] for i in region_selection1.active]\
         + [region_selection2.labels[i] for i in region_selection2.active]

    # Corresponds to unscaled
    if scaling.active == 0:
        percapita = False
    # Corresponds to per capita
    else:
        percapita = True

    # Select which data we're currently looking at
    dtype = select_data_type()
    new_src = make_data_src(regions_to_plot, percapita=percapita, dtype=dtype)
    
    src.data.update(new_src.data)

#-----------------------------------------------------------------------------#

def select_all_update():
    """ Select all regions for display. """
    region_selection1.active = list(range(len(all_regions1)))
    region_selection2.active = list(range(len(all_regions2)))

#-----------------------------------------------------------------------------#

def unselect_all_update():
    """ Unselect all regions for display. """
    region_selection1.active = []
    region_selection2.active = []

#-----------------------------------------------------------------------------#

def worst9_update():
    """ 
    Select worst 9 regions for display. Worst is defined as highest number of 
    cases on the last available date.
    """
    # Select which data we're currently looking at
    dtype = select_data_type()
    worst_d = data_d[dtype]

    # Corresponds to unscaled
    if scaling.active == 0:
        region_selection1.active = worst_d["worst9inds1"]
        region_selection2.active = worst_d["worst9inds2"]
    # Corresponds to per capita
    else:
        region_selection1.active = worst_d["worst9inds1_capita"]
        region_selection2.active = worst_d["worst9inds2_capita"]

    worst9.button_type = "primary"

#-----------------------------------------------------------------------------#

def select_data_type():
    relation = {0: "cases",
                1: "deaths",
                2: "vax",
                3: "percvax"}
    dtype = relation[data_type.active]
    return dtype

#-----------------------------------------------------------------------------#

# Radio button group for selecting cases vs deaths
data_type = RadioButtonGroup(labels=["Cases", "Deaths", "Fully Vax People", "% Population Vax"], active=0, 
                                 css_classes=["custom_button"])
data_type.on_change("active", update_plot)

# Radio button group for selecting unscaled vs per capita
scaling = RadioButtonGroup(labels=["Unscaled", "Per 100,000"], active=0, 
                                 css_classes=["custom_button"])
scaling.on_change("active", update_plot)

# Select and unselect all
select_all = Button(label="Select All", css_classes=["custom_button"])
select_all.on_click(select_all_update)
unselect_all = Button(label="Unselect All", css_classes=["custom_button"])
unselect_all.on_click(unselect_all_update)

# Button for displaying worst 9 regions
worst9 = Button(label="Show Worst 9 States", css_classes=["custom_button"])#, button_type="success")
worst9.on_click(worst9_update)

# Checkboxes to select regions to display
# Split into groups to make the checkboxes 2 columns
region_selection1 = CheckboxGroup(labels=all_regions1, active = [0, 1], 
                                  css_classes =["custom_checkbox"])
region_selection2 = CheckboxGroup(labels=all_regions2, active = [], 
                                  css_classes =["custom_checkbox"])
region_selection1.on_change('active', update_plot)
region_selection2.on_change('active', update_plot)

# Determine the initial default selected regions and create initial data & plot
initial_regions = [region_selection1.labels[i] for i in region_selection1.active]
src = make_data_src(initial_regions)
p = make_plot(src)

# Put controls/widgets in a single columns element
widgets = column(data_type,
                 scaling, 
                 row(select_all, unselect_all, width=350), 
                 worst9,
                 row(region_selection1, region_selection2, width=350),
                 width=350, height=1000)#, width=200) 

# Create a row layout with widgets and plot
grid = row(widgets, p, spacing=75)

# Add it to the current document (displays plot)
curdoc().add_root(grid)
