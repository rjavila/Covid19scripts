import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.transforms as transforms
from matplotlib.patches import Rectangle
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
    BAR_C = "#e5aabc"
    CONTRAST_C = "crimson"
    ALPHA = 0.3
    OUTSIDE_PLOT_C = "dimgrey"
    VLINE_C = "darkgrey" 
    BOX_EDGE_C = "black"
    BOX_FACE_C = "lightgrey"

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

LATIN_COUNTRIES = ['Argentina','Belize','Bolivia','Brazil','Chile','Colombia',
                   'Costa Rica','Cuba','Dominican Republic','Ecuador',
                   'El Salvador','Guatemala','Honduras','Mexico','Nicaragua',
                   'Panama','Paraguay','Peru','Uruguay','Venezuela']

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
        figsize = (18, 9)
        lw = 1.25
        labelsize = "small"
        fontsize = "medium"
        if region in ["world", "global"]:
            statenations = ALL_COUNTRIES
            filename = f"global_new_{lbl}.pdf"
        else:
            statenations = LATIN_COUNTRIES
            filename = f"latin_new_{lbl}.pdf"
            subplots = (4,5)
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
        figsize = (12, 10)
        lw = 1.5
        labelsize = "medium"
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
        
#        if region == "eu_vs_usa":
        ax.bar(dailydata.index, dailydata[statenations[i]], color=BAR_C, zorder=5)
        ax.plot(dailydata[statenations[i]].rolling(7,
                                              center=True,
                                              min_periods=2).mean(),
                                              c=CONTRAST_C, lw=lw, zorder=10)
        ax.set_ylim(bottom=0)
        total = int(dailydata[statenations[i]].sum())
        lastval = int(dailydata[statenations[i]][-1])
        
        ax.set_xlim(left=datetime.date(2020, 2, 27))
        
        plt.gcf().autofmt_xdate(rotation=60, ha="center")

        ax.tick_params('both', labelsize=labelsize, length=2)
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.yaxis.set_ticks_position('both')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(months)
        ax.yaxis.get_major_ticks()[0].label1.set_visible(False)
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        
        if region != "eu_vs_usa":
            ax.annotate(f"{statenations[i]}, total: {total:,}", (0.035, 1.05), 
                xycoords="axes fraction", size=fontsize)
            ax.annotate(f"Last: {lastval:,}", (0.035, .9), 
                xycoords = "axes fraction", size=fontsize, style="italic",
                color=CONTRAST_C)
        else:
            ax.set_xlim(left=datetime.date(2020, 2, 21))
            # Get the maximum number of intervals/10,000s of cases so far
            if lbl == "deaths":
                interval = 20000
                unit = 1000
                vline_lbl = "k"
            else:
                interval = 1000000
                unit = 1000000
                vline_lbl = " mil"
            maxinterval = data[statenations[i]][-1] - data[statenations[i]][-1] % interval
            intervals = np.arange(interval, maxinterval+interval, interval)
            # The indices for the next entry after each million cases
            intervals_inds = [np.argmax(data[statenations[i]] > x) for x in intervals]
            # Get the index corresponding to the next entry after 100 cases
            cases100_i = np.argmax(data[statenations[i]] > 100)
            # Vertical lines will be put at 100 cases and each million afterward
            # The last index is for marking the last date, but no vline
            vline_inds = [cases100_i] + intervals_inds + [len(dailydata)-1]
            # Get the transformation function the data coordinates in X and
            # axis fraction in Y
            trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
            # Make one continuous line from 100 cases to last date
            ax.plot([dailydata.index[[cases100_i]], dailydata.index[[-1]]],
                    [1.03, 1.03], transform=trans, color=OUTSIDE_PLOT_C, lw=.9,  
                    clip_on=False)
            
            for j in range(len(vline_inds)):
                ant_kwargs = {"size": 8, "color": OUTSIDE_PLOT_C, "va": "center", "ha": "center",
                              "xycoords": ("data", "axes fraction")}
                # This makes the | symbol at the end of each time segment
                ax.annotate("|", xy=(dailydata.index[[vline_inds[j]]], 1.03), 
                            **ant_kwargs)

                # Annotate how many days elapsed since last integer million cases
                # Extra annotation at the end for last integer million -> now
                if j != 0: # j=0 corresponds to 100 cases
                    ndays = vline_inds[j] - vline_inds[j-1]
                    middle_i = vline_inds[j] - int(ndays/2)
                    if ndays > 10: # if <10, not enough room for full label
                        elapsed_lbl = f"{ndays} days"
                    else:
                        elapsed_lbl = f"{ndays}d"
                    ax.annotate(elapsed_lbl, (dailydata.index[[middle_i]], 1.05), 
                        xycoords= ("data", "axes fraction"), ha="center", 
                        color=OUTSIDE_PLOT_C, style="italic")
                
                # If on the last index (last entry in dataset), we don't plot the vline
                if j == len(vline_inds)-1:
                    continue
                # Make a vertical line in the plot
                ax.axvline(dailydata.index[[vline_inds[j]]], color=VLINE_C, ls="dotted", 
                           alpha=0.7, zorder=0)
                if j == 0:
                    lab = "100"
                else:
                    lab = f"{intervals[j-1]/unit:.0f}{vline_lbl}"
                ax.annotate(lab, 
                            (dailydata.index[[vline_inds[j]]]+datetime.timedelta(hours=12), .93),
                            xycoords=("data", "axes fraction"), 
                            style="italic", color=VLINE_C)
            
            # Define axis fraction coords for the Total and Last annotations
            # and the box surrounding them
            ant_x = 0.027
            ant_ylo = 0.75
            ant_yhi = ant_ylo + 0.09
            # Put a box around the Total and Last annotations
            box = Rectangle((ant_x-0.003, ant_ylo-0.020), .137, .16, transform=ax.transAxes,
                edgecolor=BOX_EDGE_C, facecolor=BOX_FACE_C, alpha=0.5)
            ax.add_patch(box)
            ax.annotate(f"Total: {total:,}", (ant_x, ant_yhi), va="center", ha="left", 
                xycoords = "axes fraction", size=fontsize, style="italic")
            ax.annotate(f"Last: {lastval:,}", (ant_x, ant_ylo), 
                xycoords = "axes fraction", size=fontsize, style="italic",
                color=CONTRAST_C)
            
            # Define US and EU population (in units of intervals) by hand
            # and write a title
            eu_usa_pops = {"US": 328, "EU": 445} 
            tester = "US"
            ax.set_title(f"$\\bf{statenations[i]}$, population: {eu_usa_pops[statenations[i]]:,} million", 
                loc="left", pad=27, fontsize=fontsize)
   
    if region == "eu_vs_usa": 
        # Set both US and EU ylim maximum to the same value 
        us_ymax = axes[0].get_ylim()[1]
        eu_ymax = axes[1].get_ylim()[1]
        max_max = max(us_ymax, eu_ymax)
        axes[0].set_ylim(top=max_max)
        axes[1].set_ylim(top=max_max)

    plt.suptitle(f'New daily {lbl}\n{dailydata.index[-1]:%B %d, %Y}',
                 fontsize='x-large', y=1.01)
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
    
    allowed_regions = ["world", "usa", "latin", "eu_vs_usa", "worst_usa", "worst_world"]
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
