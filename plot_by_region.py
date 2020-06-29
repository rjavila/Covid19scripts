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

fontsize = "x-large"
labelsize = "large"

def plot_by_region(region, data_world, data_usa, outdir="plots", deaths=False):

    if deaths is True:
        lbl = "deaths"
    else:
        lbl = "cases"

    try:
        data_region = data_world[region]
    except:
        data_region = data_usa[region]
    
    fig, ax = plt.subplots(1, 1, figsize=(10,5))
    ax.bar(data_region.index, data_region.diff(), color=bar_c, alpha=alpha)
    ax.plot(data_region.diff().rolling(5, center=True, min_periods=2).mean(), 
                c=contrast_c, lw=2)
    lastval = int(data_region.diff()[-1])
    future = data_region.index[-1] + datetime.timedelta(days=1)
    ax.annotate(f"{lastval:,}", (future, lastval), ha="left", 
                va="center", size="large", style="italic", color=bar_c)
    total = int(data_region.diff().sum())
    past = datetime.date(2020, 3, 1)
    ax.annotate(f"Total {lbl}: {total:,}", (.05, .9), 
                xycoords="axes fraction", size="large", style="italic")
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))               
    months = mdates.MonthLocator()
    ax.xaxis.set_major_locator(months)
    ax.set_xlim(left=datetime.date(2020, 2, 27))
    plt.gcf().autofmt_xdate(rotation=60, ha='center')
    ax.tick_params('both', labelsize=labelsize, length=2)
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))    
    ax.yaxis.set_ticks_position('both')                         

    plt.ylabel(f'New daily {lbl}', fontsize=fontsize)
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
    plot_by_region(args.region, data_world, data_usa, deaths=args.deaths)

