import argparse
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import get_data

def plot_by_region(region, data_world, data_usa, outdir="plots"):

    try:
        data_region = data_world[region]
    except:
        data_region = data_usa[region]
    
    fig = plt.figure(figsize=(6,4))
    plt.bar(data_region.index, data_region.diff())
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))               
    plt.gcf().autofmt_xdate(rotation=0, ha='center')

    plt.ylabel('Daily new cases')
    plt.suptitle(region, fontsize='x-large')

    outfilename = os.path.join(outdir, f"{region}_new_cases.png")
    plt.savefig(outfilename, bbox_index='tight')
    print(f"Saved {outfilename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="region",
                        help="Name of state or nation to plot")
    args = parser.parse_args()

    data_usa, pops_usa = get_data.get_data("usa")
    data_world, pops_world = get_data.get_data("world")
    plot_by_region(args.region, data_world, data_usa)

