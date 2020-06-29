import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys
import argparse
import datetime

import get_data

stylesheet = "seaborn-dark"
#stylesheet = "dark_background"
matplotlib.style.use(stylesheet)
if stylesheet == "dark_background":
    BAR_C = "#8dd3c7"
    CONTRAST = "gold"
    ALPHA = 1.0
else:
    BAR_C = "crimson"
    CONTRAST_c = "crimson"
    ALPHA = 0.3

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

ALL_COUNTRIES = ['Brazil','Costa Rica','El Salvador','Germany','Iran',
                 'Italy','Korea, South','Mexico','Russia','Spain','Sweden','US']

EU_COUNTRIES = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia',
                'Denmark','Estonia','Finland','France','Germany','Greece',
                'Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg',
                'Malta','Netherlands','Poland','Portugal','Romania','Slovakia',
                'Slovenia','Spain','Sweden']

LATIN_COUNTRIES = ['Mexico','Guatemala','Belize','El Salvador','Honduras',
                   'Nicaragua','Costa Rica','Panama','Colombia','Venezuela',
                   'Ecuador','Peru','Brazil','Bolivia','Paraguay','Uruguay',
                   'Argentina','Chile','Cuba','Dominican Republic']

def grid_plot(data, region, outdir="plots", deaths=False):
    """
    Make subplot grid plots for each state/country of interest in list.
    Args:
        data (:obj:`pandas.DataFrame`): Covid statistics on region of interest.
        region (str): Country/state of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
        outdir (str): Name of directory to save plots to.
        deaths (Bool): If True, download data on deaths.
    """
   
    months = mdates.MonthLocator()
    
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if deaths is True:
        lbl = "deaths"
    else:
        lbl = "cases"

    dailydata = data.diff()
    
    if region in ["world", "global", "latin"]:
        subplots = (3, 4)
        figsize = (12, 6)
        lw = 1.25
        labelsize = "small"
        fontsize = "medium"
        if region in ["world", "global"]:
            statenations = ALL_COUNTRIES
            filename = f"global_new_{lbl}.pdf"
        else:
            statenations = LATIN_COUNTRIES
            filename = f"latin_new_{lbl}.pdf"
    elif region == "usa":
        subplots = (5, 10)
        figsize = (20, 9)
        statenations = STATES
        lw = 0.75
        labelsize = "xx-small"
        fontsize = "small"
        filename = f"states_new_{lbl}.pdf"
    elif region == "eu_vs_usa":
        data["EU"] = data.loc[:,EU_COUNTRIES].sum(axis=1)
        dailydata = data.diff()
        subplots = (2, 1)
        figsize = (6, 6)
        lw = 1.5
        labelsize = "small"
        fontsize = "large"
        statenations = ["US", "EU"]
        filename = f"EU_vs_USA_{lbl}.pdf"
    elif region in ["worst_usa", "worst_global", "worst_world"]:
        data_sorted = dailydata.T.sort_values(dailydata.index[-1], ascending=False).T
        dailydata = data_sorted.iloc[:, :10]
        subplots = (3, 3)
        figsize = (13, 10)
        lw = 1.5
        labelsize = "small"
        fontsize= "medium"
        statenations = dailydata.columns.values
        if region == "worst_usa":
            filename = f"worst_usa_{lbl}.pdf"
        else:
            filename = f"worst_global_{lbl}.pdf"
    else:
        raise KeyError("Region {region} not in acceptable values")

    fig, axes = plt.subplots(subplots[0], subplots[1],
                             figsize=(figsize[0], figsize[1]),
                             sharex=True)
    plt.subplots_adjust(wspace=0.35)
    plt.subplots_adjust(hspace=0.35)

    #daily_sorted = dailydata.reindex(dailydata.sum(axis=0).sort_values(ascending=False).index, axis=1)

    for i,ax in enumerate(axes.flatten()):

        ax.bar(dailydata.index, dailydata[statenations[i]], color=BAR_C,
               alpha=ALPHA)
        ax.plot(dailydata[statenations[i]].rolling(5,
                                              center=True,
                                              min_periods=2).mean(),
                                              c=CONTRAST_c, lw=lw)
        ax.set_ylim(bottom=0)
        total = int(dailydata[statenations[i]].sum())
        lastval = int(dailydata[statenations[i]][-1])
        ax.annotate(f"{statenations[i]}, total: {total:,}", (0.035, 1.05), 
                    xycoords="axes fraction", size=fontsize)
        ax.annotate(f"Last: {lastval:,}", (0.035, .9), 
                    xycoords = "axes fraction", size=fontsize, style="italic",
                    color="crimson")
        ax.set_xlim(left=datetime.date(2020, 2, 27))
        
        plt.gcf().autofmt_xdate(rotation=60, ha="center")

        ax.tick_params('both', labelsize=labelsize, length=2)
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.yaxis.set_ticks_position('both')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(months)

    plt.suptitle(f'New daily {lbl}\n{dailydata.index[-1]:%B %d, %Y}',
                 fontsize='large')
    outfilename = os.path.join(outdir, filename)
    plt.savefig(outfilename, bbox_inches='tight')
    print(f"Saved {outfilename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deaths", action="store_true",
                        default=False,
                        help="Switch to plot deaths instead of cases")
    parser.add_argument('--regions', nargs='+')
    args = parser.parse_args()
    
    allowed_regions = ["world", "usa", "latin", "eu_vs_usa", "worst_usa", "worst_global"]
    if args.regions is None:
        regions = allowed_regions
    else:
        regions = []
        for item in args.regions:
            if item in allowed_regions:
                regions.append(item)
            else:
                print(f"Region {item} not recognized\nAllowed values: {allowed_regions}")

    for item in regions:
        data, pops = get_data.get_data(item, deaths=args.deaths)
        grid_plot(data, item, deaths=args.deaths)
