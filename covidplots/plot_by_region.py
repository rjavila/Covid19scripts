import datetime
import argparse
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

def plot_by_region(region, data_world, data_usa, pops_world, pops_usa, 
                   outdir="plots", deaths=False):
    """
    Plot a bar plot of daily new cases or deaths for a single state or country.
    Args:
        region (str): Country/state of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
        data_world (:obj:`pandas.DataFrame`): Global covid statistics.
        data_usa (:obj:`pandas.DataFrame`): USA covid statistics.
        data_world (:obj:`pandas.DataFrame`): Global populations.
        data_usa (:obj:`pandas.DataFrame`): USA state populations..
        outdir (str): Name of directory to save plots to.
        deaths (Bool): If True, download data on deaths.
    """

    if deaths is True:
        lbl = "deaths"
    else:
        lbl = "cases"

    try:
        data_region = data_world[region].diff()
        if region == "US":
            population = 328000000
        else:
            population = None
    except:
        data_region = data_usa[region].diff()
        population = pops_usa[region][0]
    
    fig, ax = plt.subplots(1, 1, figsize=(10,5))
    ax.bar(data_region.index, data_region, color=bar_c, alpha=alpha)
    ax.plot(data_region.rolling(5, center=True, min_periods=2).mean(), 
                c=contrast_c, lw=2)
    lastval = int(data_region[-1])
    future1day = data_region.index[-1] + datetime.timedelta(days=1)
    future3day = data_region.index[-1] + datetime.timedelta(days=3)
#    ax.annotate(f"{lastval:,}", (future1day, lastval), ha="left", 
#                va="center", size="large", style="italic", color=bar_c)
    total = int(data_region.sum())
    past = datetime.date(2020, 3, 1)
    
    if population is not None:
        ax.annotate(f"Population: {population:,}", (.035, 1.02), 
                    xycoords="axes fraction", size="large")
        perc = (total / population) * 100
        totallab = f"Total: {total:,} ({perc:.1f}%)"
    else:
        totallab = f"Total: {total:,}"
    ax.annotate(totallab, (.035, .94), 
                xycoords="axes fraction", size="large", style="italic")
    ax.annotate(f"Last: {lastval:,}", (.035, .87), 
                xycoords="axes fraction", size="large", style="italic",
                color=bar_c)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))               
    months = mdates.MonthLocator()
    ax.xaxis.set_major_locator(months)
    ax.set_xlim(datetime.date(2020, 2, 27), future3day)
    plt.gcf().autofmt_xdate(rotation=60, ha='center')
    ax.tick_params('both', labelsize="large", length=2)
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))    
    ax.yaxis.set_ticks_position('both')                         

    plt.suptitle(f"{region} new daily {lbl}", fontsize='x-large')

    if not os.path.exists(outdir):
        os.mkdir(outdir)
    outfilename = os.path.join(outdir, f"{region}_new_{lbl}.png")
    plt.savefig(outfilename, bbox_index='tight')
    print(f"Saved {outfilename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="region",
                        help="Name of state or nation to plot")
    parser.add_argument("-d", "--deaths", action="store_true",
                        default=False,
                        help="Switch to plot deaths instead of cases")
    args = parser.parse_args()

    data_usa, pops_usa = get_data.get_data("usa", deaths=args.deaths)
    data_world, pops_world = get_data.get_data("world", deaths=args.deaths)
    plot_by_region(args.region, data_world, data_usa, pops_world, pops_usa, 
                   deaths=args.deaths)

