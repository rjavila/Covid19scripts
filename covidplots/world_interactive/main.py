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
from bokeh.models import HoverTool, ColumnDataSource, TextInput, TextAreaInput, MultiSelect
from bokeh.models.widgets import CheckboxGroup, Button, RadioButtonGroup, Panel, Tabs
from bokeh.layouts import column, row
from bokeh.palettes import Category20, Category20c, Category20b

from covidplots import get_data
from covidplots.continents import census_continents

#-----------------------------------------------------------------------------#
# Read and handle data

# Get continent definitions for each country
by_cont = census_continents()

# Define region names
all_countries = by_cont["All"]
all_conts = by_cont.keys().to_list()

# Read in data for world
data, pops = get_data.get_data("world")
data = data.diff()
# Use 7 day average as the defacto data
data = data.rolling(7, center=True, min_periods=2).mean()

# Add the index (date) as a column for convenience
data["date"] = data.index

#-----------------------------------------------------------------------------#
# Define constants

# Worst X number of countries
worstx = 5

# Define per capita number
capita = 1000000

# Define list of colors to use  
colors_l = Category20[20] + Category20b[20] +  Category20c[20]

# Set x limits to be March 1 -> now + 1 day
xleft = datetime.datetime(2020, 3, 1)
xright = datetime.datetime.now() + datetime.timedelta(days=1)

#-----------------------------------------------------------------------------#

def make_data_src(region_list, percapita=False):
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

    xs = [data["date"] for x in range(len(region_list))]
    if percapita is True:
        ys = [capita * data[region].div(pops[region].iloc[0]) for region in region_list] 
    else:
        ys = [data[region].values for region in region_list]          
    names = [np.array([region]) for region in region_list]
    colors = colors_l[:len(region_list)]
    
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
    # Create a line for each region
    p.multi_line(source=src, xs="xs", ys="ys", color="colors", 
                 line_width=3, legend_field="names")              

    p.legend.location = "top_left"
    p.legend.label_text_font_size = "13pt"

    # Style figure
    p = style(p)

    return p

#-----------------------------------------------------------------------------#

def get_active_tab():
    tab_i = tabs.active
    tab_title = tabs.tabs[tab_i].title
    return tab_title

#-----------------------------------------------------------------------------#

def update_plot(attr, old, new):
    """
    Boilerplate function for updating plot using a new bokeh data source.
    This is triggered when the regions to display is changed, either via
    checkbox selection or button activation (e.g. "select all")
    """
    
    tab_title = get_active_tab()
    regions_to_plot = [
            checkbox_d[tab_title][0].labels[i] for i in checkbox_d[tab_title][0].active]\
         + [checkbox_d[tab_title][1].labels[i] for i in checkbox_d[tab_title][1].active]

    # Corresponds to unscaled
    if radio_buttons.active == 0:
        new_src = make_data_src(regions_to_plot)
    # Corresponds to per capita
    else:
        new_src = make_data_src(regions_to_plot, percapita=True)
    
    srcs[tab_title].data.update(new_src.data)

#-----------------------------------------------------------------------------#

def all_update_plot(attr, old, new):
    tab_title = get_active_tab()
    regions_to_plot = []
    for ms in multi_selects:
        regions_to_plot += ms.value
    text = all_text_input.value
    if text != "":
        regions_to_plot += text.split("\n")
    
    # Corresponds to unscaled
    if radio_buttons.active == 0:
        new_src = make_data_src(regions_to_plot)
    # Corresponds to per capita
    else:
        new_src = make_data_src(regions_to_plot, percapita=True)
    
    srcs[tab_title].data.update(new_src.data)

#-----------------------------------------------------------------------------#

def text_update(attr, old, new):
    tab_title = get_active_tab()
    text = text_input.value
    regions_to_plot = text.split("\n")
    try:
        inds_bool0 = np.in1d(checkbox_d[tab_title][0].labels, regions_to_plot)
        inds0 = np.where(inds_bool0 == True)[0]
        inds_bool1 = np.in1d(checkbox_d[tab_title][1].labels, regions_to_plot)
        inds1 = np.where(inds_bool1 == True)[0]
        checkbox_d[tab_title][0].active = list(inds0)
        checkbox_d[tab_title][1].active = list(inds1)
    except KeyError:
        pass

#-----------------------------------------------------------------------------#

def all_text_update(attr, old, new):
    tab_title = get_active_tab()
    text = all_text_input.value
    regions_to_plot = text.split("\n")
    try:# Corresponds to unscaled
        if radio_buttons.active == 0:
            new_src = make_data_src(regions_to_plot)
        # Corresponds to per capita
        else:
            new_src = make_data_src(regions_to_plot, percapita=True)
        srcs[tab_title].data.update(new_src.data)
    except KeyError:
        pass

#-----------------------------------------------------------------------------#

def select_all_update():
    """ Select all regions for display. """
    tab_title = get_active_tab()
    checkbox_d[tab_title][0].active = list(range(len(all_regions_d[tab_title][0])))
    checkbox_d[tab_title][1].active = list(range(len(all_regions_d[tab_title][1])))

#-----------------------------------------------------------------------------#

def unselect_all_update():
    """ Unselect all regions for display. """
    tab_title = get_active_tab()
    checkbox_d[tab_title][0].active = []
    checkbox_d[tab_title][1].active = []

#-----------------------------------------------------------------------------#

def all_unselect_all_update():
    """ Unselect all regions for display. """
    tab_title = get_active_tab()
    checkbox_d[tab_title][0].active = []
    checkbox_d[tab_title][1].active = []
    for ms in multi_selects:
        ms.value = []
    text_input.value = ""

#-----------------------------------------------------------------------------#

def worst_update():
    """ 
    Select worst regions for display. Worst is defined as highest number of 
    cases on the last available date.
    """
    tab_title = get_active_tab()
    checkbox_d[tab_title][0].active = worstinds_d[tab_title][0]
    checkbox_d[tab_title][1].active = worstinds_d[tab_title][1]

#-----------------------------------------------------------------------------#

def all_worst_update():
    """ 
    Select worst regions for display. Worst is defined as highest number of 
    cases on the last available date.
    """
    
    all_unselect_all_update()
    tab_title = get_active_tab()
    # Corresponds to unscaled
    if radio_buttons.active == 0:
        new_src = make_data_src(worstallnames)
    # Corresponds to per capita
    else:
        new_src = make_data_src(worstallnames, percapita=True)
    srcs[tab_title].data.update(new_src.data)

#-----------------------------------------------------------------------------#

def create_checkboxes(cont):
    # Split into groups to make the checkboxes 2 columns
    all_regions = by_cont[cont]
    middle = int(np.floor(len(all_regions)/2))
    all_regions1 = all_regions[:middle]
    all_regions2 = all_regions[middle:]
    region_selection1 = CheckboxGroup(labels=all_regions1, active = [0], 
                                      css_classes =["custom_checkbox"])
    region_selection2 = CheckboxGroup(labels=all_regions2, active = [], 
                                      css_classes =["custom_checkbox"])
    region_selection1.on_change('active', update_plot)
    region_selection2.on_change('active', update_plot)

    return all_regions1, all_regions2, region_selection1, region_selection2

#-----------------------------------------------------------------------------#

def create_multiselect(cont):
    multi_select = MultiSelect(title=cont, value=[], 
                               options=by_cont[cont])
    multi_select.on_change("value", multi_update)
    return multi_select

#-----------------------------------------------------------------------------#

def multi_update(attr, old, new):
    tab_title = get_active_tab()
    regions_to_plot = []
    for ms in multi_selects:
        regions_to_plot += ms.value
    all_regions0 = all_regions_d[tab_title][0]
    all_regions1 = all_regions_d[tab_title][1]
    inds0 = [x for x in range(len(all_regions0)) if all_regions0[x] in regions_to_plot]
    inds1 = [x for x in range(len(all_regions1)) if all_regions1[x] in regions_to_plot]
    checkbox_d[tab_title][0].active = inds0
    checkbox_d[tab_title][1].active = inds1

#-----------------------------------------------------------------------------#

def get_worst(cont, worstx=worstx):
    data_cont = data.loc[:, by_cont[cont]]
    data_sorted = data_cont.T.sort_values(data_cont.index[-1], ascending=False).T
    topworst = data_sorted.iloc[:, :worstx] 
    worstnames = topworst.columns.values
    return worstnames

#-----------------------------------------------------------------------------#

# Radio button group for selecting unscaled vs per capita
radio_buttons = RadioButtonGroup(labels=["Unscaled", "Per Million"], active=0, 
                                 css_classes=["custom_button"])
radio_buttons.on_change("active", update_plot)

# Select and unselect all
select_all = Button(label="Select All", css_classes=["custom_button"])
select_all.on_click(select_all_update)
unselect_all = Button(label="Unselect All", css_classes=["custom_button"])
unselect_all.on_click(unselect_all_update)

# Button for displaying worst regions
worst = Button(label=f"Show Worst {worstx} Countries", css_classes=["custom_button"])
worst.on_click(worst_update)

# Text input to enter individual countries
text_input = TextAreaInput(value="",
                rows=6, 
                title="Manually enter line-separated countries, hit tab when finished") 
text_input.on_change("value", text_update)

all_regions_d = {}
checkbox_d = {}
multi_selects = []
worstinds_d = {}
srcs = {}
tabs = []
for cont in all_conts:
    # Make multi select widgets for each continent, to be used in "All" tab
    multi_select = create_multiselect(cont)
    multi_selects.append(multi_select)

    # Checkboxes to select regions to display
    all_regions1, all_regions2, region_selection1, region_selection2 = create_checkboxes(cont)
    checkbox_d[cont] = [region_selection1, region_selection2]
    all_regions_d[cont] = [all_regions1, all_regions2]

    # Get worst countries
    if cont == "All":
        worstnames = get_worst(cont, 9)
    else: 
        worstnames = get_worst(cont) 
    worstinds1 = [x for x in range(len(all_regions1)) if all_regions1[x] in worstnames]
    worstinds2 = [x for x in range(len(all_regions2)) if all_regions2[x] in worstnames]
    worstinds_d[cont] = [worstinds1, worstinds2]

    if cont == "All":
        continue

    # Determine the initial default selected regions 
    # Create initial data & plot
    initial_regions = [region_selection1.labels[i] for i in region_selection1.active]
    src = make_data_src(initial_regions)
    srcs[cont] = src
    p = make_plot(src)

    # Put controls/widgets in a single columns element
    widgets = column(radio_buttons, 
                     row(select_all, unselect_all, width=350), 
                     worst,
                     row(region_selection1, region_selection2, width=350),
                     text_input,
                     width=350, height=1000,)#, width=200)

    # Create a row layout with widgets and plot
    grid = row(widgets, p, spacing=75)
    tab = Panel(child=grid, title=cont)
    tabs.append(tab)

# Now handle the "All" tab
src = make_data_src([])
srcs[cont] = src
p = make_plot(src)
# Radio button group for selecting unscaled vs per capita
all_radio_buttons = RadioButtonGroup(labels=["Unscaled", "Per Million"], active=0, 
                                 css_classes=["custom_button"])
all_radio_buttons.on_change("active", all_update_plot)
# Button for displaying worst regions for ALL countries
all_worst = Button(label=f"Worst 9", css_classes=["custom_button"])
all_worst.on_click(worst_update)
# Unselect all
all_unselect_all = Button(label="Unselect All", css_classes=["custom_button"])
all_unselect_all.on_click(all_unselect_all_update)
# Put controls/widgets in a single columns element
widgets = column(radio_buttons, 
                 row(all_worst, all_unselect_all, width=350),
                 text_input,
                 column(children=multi_selects),
                 width=350, height=1000,)#, width=200)
grid = row(widgets, p, spacing=75)
tab = Panel(child=grid, title=cont)
tabs.append(tab)

tabs = Tabs(tabs=tabs)

# Add it to the current document (displays plot)
curdoc().add_root(tabs)
