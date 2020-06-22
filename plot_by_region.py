import argparse
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import get_data

def plot_by_region(region, data_world, data_usa, outdir="plots", deaths=False):

    if deaths is True:
        lbl = "deaths"
    else:
        lbl = "cases"

    try:
        data_region = data_world[region]
    except:
        data_region = data_usa[region]
    
    fig = plt.figure(figsize=(6,4))
    plt.bar(data_region.index, data_region.diff())
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))               
    plt.gcf().autofmt_xdate(rotation=0, ha='center')

    plt.ylabel(f'Daily new {lbl}')
    plt.suptitle(region, fontsize='x-large')

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

