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
    bar_c = "#8dd3c7"
    contrast = "gold"
    alpha = 1.0
else:
    bar_c = "crimson"
    contrast_c = "crimson"
    alpha = 0.3

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

def grid_plot(data, region, outdir="plots", eu_vs_usa=True, deaths=False):
    months = mdates.MonthLocator()
    
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if deaths is True:
        lbl = "deaths"
    else:
        lbl = "cases"

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
        subplots = (2, 1)
        figsize = (6, 6)
        lw = 1.5
        labelsize = "small"
        fontsize = "large"
        statenations = ["US", "EU"]
        filename = f"EU_vs_USA_{lbl}.pdf"

    fig, axes = plt.subplots(subplots[0], subplots[1],
                             figsize=(figsize[0], figsize[1]),
                             sharex=True)
    plt.subplots_adjust(wspace=0.35)
    plt.subplots_adjust(hspace=0.35)

    dailydata = data.diff()

    for i,ax in enumerate(axes.flatten()):

        ax.bar(dailydata.index, dailydata[statenations[i]], color=bar_c,
               alpha=alpha)
        ax.plot(dailydata[statenations[i]].rolling(5,
                                              center=True,
                                              min_periods=2).mean(),
                                              c=contrast_c, lw=lw)
        ax.set_ylim(bottom=0)
        total = int(dailydata[statenations[i]].sum())
        ax.annotate(f"{statenations[i]}", (0.035, 1.05), xycoords="axes fraction", 
                    size=fontsize)
        ax.annotate(f"{total:,}", (0.035, .85), 
                    xycoords = "axes fraction", size=fontsize, style="italic")
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
    args = parser.parse_args()
    
    regions = ["world", "usa", "latin", "eu_vs_usa"]
#    regions = ["usa"]
    for item in regions:
        data, pops = get_data.get_data(item, deaths=args.deaths)
        grid_plot(data, item, deaths=args.deaths)
