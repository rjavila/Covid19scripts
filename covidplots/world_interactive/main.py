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
# Read and handle data

# Get continent definitions for each country
by_cont = census_continents()

# Define region names
all_countries = by_cont["All"]
all_conts = by_cont.keys().to_list()

# Read in data for world
data_d = {}
for deaths in [False, True]:
    data, pops = get_data.get_data("world", deaths=deaths)
    data = data.diff()
    # Use 7 day average as the defacto data
    data = data.rolling(7, center=False, min_periods=2).mean()
    
    # Calculate per capita values
    data_capita = capita * data.div(pops.iloc[0], axis="columns")
    
    # Add the index (date) as a column for convenience
    data["date"] = data.index

    data_d[deaths] = {"data": data, "data_capita": data_capita, 
                      "worstinds_d": {}, "worstinds_capita_d": {}}

#-----------------------------------------------------------------------------#

def make_data_src(region_list, percapita=False, deaths=False):
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

    worst.button_type = "default"

    data = data_d[deaths]["data"]

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

def get_active_tab():
    """
    Get the name of the active tab.
    Returns:
        tab_title (str): Name of active tab.
    """
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
            all_regions_d[tab_title][0][i] for i in checkbox_d[tab_title][0].active]\
         + [all_regions_d[tab_title][1][i] for i in checkbox_d[tab_title][1].active]

    # Corresponds to unscaled
    if scaling.active == 0:
        percapita = False
    # Corresponds to per capita
    else:
        percapita = True

    # Corresponds to cases
    if data_type.active == 0:
        new_src = make_data_src(regions_to_plot, percapita=percapita, deaths=False)
    # Corresponds to deaths
    else:
        new_src = make_data_src(regions_to_plot, percapita=percapita, deaths=True)

    srcs[tab_title].data.update(new_src.data)

#-----------------------------------------------------------------------------#

def text_update(attr, old, new):
    """
    When text is entered in the textbox, see if entered text matches 
    countries in the current tab and plot them.
    """
    tab_title = get_active_tab()
    text = textinput_d[tab_title].value
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
    textinput_d[tab_title].value = ""
    if tab_title == "All":
        for ms in multi_selects:
            ms.value = []

#-----------------------------------------------------------------------------#

def get_worst(cont, data=data, worstx=worstx):
    """
    Get the worst X regions (by default, 5).
    Args:
        cont (str): Continent name.
        worstx (int): Get worst countries 1 - worstx, be default 5. 
    Returns:
        worstnames (list): Names of worst countries.
    """

    data_cont = data.loc[:, by_cont[cont]]
    data_sorted = data_cont.T.sort_values(data_cont.index[-1], ascending=False).T
    topworst = data_sorted.iloc[:, :worstx] 
    worstnames = topworst.columns.values
    return worstnames

#-----------------------------------------------------------------------------#

def worst_update():
    """ 
    Select worst regions for display. Worst is defined as highest number of 
    cases on the last available date.
    """
   
    # Corresponds to cases
    if data_type.active == 0:
        d0 = data_d[False]
    else:
        d0 = data_d[True]
 
    # Corresponds to unscaled
    if scaling.active == 0:
        worstinds_d_use = d0["worstinds_d"]
    else: # Per capita
        worstinds_d_use = d0["worstinds_capita_d"]
    tab_title = get_active_tab()
    if tab_title == "All":
        for ms in multi_selects:
            ms.value = []
    checkbox_d[tab_title][0].active = worstinds_d_use[tab_title][0]
    checkbox_d[tab_title][1].active = worstinds_d_use[tab_title][1]

    worst.button_type = "primary"

#-----------------------------------------------------------------------------#

def create_text(cont):
    """
    Create a box to enter text for each tab.
    Args:
        cont (str): Continent name.
    Returns:
        text_input (:obj:`TextAreaInput`): Text input box.
    """
    text_input = TextAreaInput(value="",
        rows=6, 
        title="Manually enter line-separated countries, hit tab when finished") 
    text_input.on_change("value", text_update)
    return text_input

#-----------------------------------------------------------------------------#

def create_checkboxes(cont):
    """
    Create checkboxes.
    Args:
        cont (str): Continent name.
    Returns:
        all_regions1 (list): List of regions corresponding to checkbox column1. 
        all_regions2 (list): List of regions corresponding to checkbox column2.
        region_selection1 (:obj:`CheckboxGroup`): Checkbox column1.
        region_selection2 (:obj:`CheckboxGroup`): Checkbox column2.
    """
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
    """
    Create a multiselect box for each continent, for the "All" tab.
    Args:
        cont (str): Continent name.
    Returns:
        multi_select (:obj:`MultiSelect`): Multiselect box.
    """
    multi_select = MultiSelect(title=cont, value=[], 
                               options=by_cont[cont])
    multi_select.on_change("value", multi_update)
    return multi_select

#-----------------------------------------------------------------------------#

def multi_update(attr, old, new):
    """ When a multiselect box is updated, change regions to display. """
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

# Radio button group for selecting cases vs deaths
data_type = RadioButtonGroup(labels=["Cases", "Deaths"], active=0,
                                 css_classes=["custom_button"])
data_type.on_change("active", update_plot)

# Radio button group for selecting unscaled vs per capita
scaling = RadioButtonGroup(labels=["Unscaled", "Per Million"], active=0, 
                                 css_classes=["custom_button"])
scaling.on_change("active", update_plot)

# Select and unselect all
select_all = Button(label="Select All", css_classes=["custom_button"])
select_all.on_click(select_all_update)
unselect_all = Button(label="Unselect All", css_classes=["custom_button"])
unselect_all.on_click(unselect_all_update)

# Button for displaying worst regions
worst = Button(label=f"Show Worst {worstx} Countries", css_classes=["custom_button"])
worst.on_click(worst_update)

all_regions_d = {}
checkbox_d = {}
textinput_d = {}
multi_selects = []
srcs = {}
tabs = []
for cont in all_conts:
    # Make multi select widgets for each continent, to be used in "All" tab
    multi_select = create_multiselect(cont)
    multi_selects.append(multi_select)

    # Text input to enter individual countries
    text_input = create_text(cont)
    textinput_d[cont] = text_input
    
    # Checkboxes to select regions to display
    all_regions1, all_regions2, region_selection1, region_selection2 = create_checkboxes(cont)
    checkbox_d[cont] = [region_selection1, region_selection2]
    all_regions_d[cont] = [all_regions1, all_regions2]

    for deaths in [False, True]:
        # Get worst countries
        if cont == "All":
            worstnames = get_worst(cont, data_d[deaths]["data"], 9)
            worstnames_capita = get_worst(cont, data_d[deaths]["data_capita"], 9)
        else: 
            worstnames = get_worst(cont, data_d[deaths]["data"], worstx) 
            worstnames_capita = get_worst(cont, data_d[deaths]["data_capita"], worstx) 
        worstinds1 = [x for x in range(len(all_regions1)) if all_regions1[x] in worstnames]
        worstinds2 = [x for x in range(len(all_regions2)) if all_regions2[x] in worstnames]
        worstinds1_capita = [x for x in range(len(all_regions1)) if all_regions1[x] in worstnames_capita]
        worstinds2_capita = [x for x in range(len(all_regions2)) if all_regions2[x] in worstnames_capita]
        data_d[deaths]["worstinds_d"][cont] = [worstinds1, worstinds2]
        data_d[deaths]["worstinds_capita_d"][cont] = [worstinds1_capita, worstinds2_capita]

    if cont == "All":
        continue

    # Determine the initial default selected regions 
    # Create initial data & plot
    initial_regions = [all_regions1[i] for i in region_selection1.active]
    src = make_data_src(initial_regions)
    srcs[cont] = src
    p = make_plot(src)

    # Put controls/widgets in a single columns element
    widgets = column(data_type,
                     scaling, 
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
# Radio button group for selecting cases vs deaths
all_data_type = RadioButtonGroup(labels=["Cases", "Deaths"], active=0,
                                 css_classes=["custom_button"])
all_data_type.on_change("active", update_plot)
# Radio button group for selecting unscaled vs per capita
all_scaling = RadioButtonGroup(labels=["Unscaled", "Per Million"], active=0, 
                                 css_classes=["custom_button"])
all_scaling.on_change("active", update_plot)
# Button for displaying worst regions for ALL countries
all_worst = Button(label=f"Worst 9", css_classes=["custom_button"])
all_worst.on_click(worst_update)
# Unselect all
all_unselect_all = Button(label="Unselect All", css_classes=["custom_button"])
all_unselect_all.on_click(unselect_all_update)
# Put controls/widgets in a single columns element
widgets = column(all_data_type,
                 all_scaling, 
                 row(all_worst, all_unselect_all, width=350),
                 text_input,
                 column(children=multi_selects),
                 width=350, height=1000,)#, width=200)
grid = row(widgets, p, spacing=75)
tab = Panel(child=grid, title=cont)
tabs.append(tab)

# Add tabs to the current document (displays plot)
tabs = Tabs(tabs=tabs)
curdoc().add_root(tabs)
