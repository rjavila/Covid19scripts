import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import datetime

import get_data

matplotlib.use('agg')
matplotlib.style.use('ggplot')
plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True

SUBSET_STATES = ['Arkansas','California','Indiana','Maryland','New Jersey',
                 'New York','Ohio','Texas','Washington']
SUBSET_COUNTIRES = ['China','El Salvador','Iran','Italy','Japan',
                    'Korea, South','Spain','Taiwan*','US']
N_MIN = 100

def overlaid_plots(region, all_data, pops, region_subset=None, outdir="plots"):
    if region is not None:
        capita = 100000
        region_subset = region
    if region == "world":
        capita = 1000000
        region_subset = SUBSET_COUNTRIES
    else:
        capita = 100000
        region_subset = SUBSET_STATES
   
    clist = plt.cm.tab20(np.linspace(0, 1, len(region_subset)))
    data_subset = all_data[region_subset]
    data_subset_capita = capita * data_subset.div(pops[region_subset].iloc[0], 
                                          axis="columns")

    for log in [False, True]:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_xlabel("Date", fontsize="large")
        ax.set_ylabel(f'Number of Cases Per {capita:,}', fontsize='large')
        data_subset_capita.plot(ax=ax, marker="o", ms=5, colormap="tab20")
        ax.set_xlim(datetime.date(2020, 3, 1), datetime.datetime.now() + datetime.timedelta(days=2))
        if log is True:
            ax.set_ylim(bottom=1)
            ax.semilogy()
            ax.yaxis.set_major_formatter(ScalarFormatter())
            filename = os.path.join(outdir, f"{region}_capita_date_log.png")
            title = f"Log Number of Cases  Per {capita:,} by Date"
        else:
            filename = os.path.join(outdir, f"{region}_capita_date.png")
            title = f"Number of Cases  Per {capita:,} by Date"
        fig.suptitle(title)
        fig.savefig(filename, bbox_inches="tight")
        print(f"Saved {filename}")

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_xlabel("Date", fontsize="large")
        ax.set_ylabel(f'Number of Cases', fontsize='large')
        data_subset.plot(ax=ax, marker="o", ms=5, colormap="tab20")
        ax.set_xlim(datetime.date(2020, 3, 1), datetime.datetime.now() + datetime.timedelta(days=2))
        if log is True:
            ax.semilogy()
            filename = os.path.join(outdir, f"{region}_date_log.png")
            title = "Log Number of Cases by Date"
        else:
            filename = os.path.join(outdir, f"{region}_date.png")
            title = "Number of Cases by Date"
        fig.suptitle(title)
        fig.savefig(filename, bbox_inches="tight")
        print(f"Saved {filename}")

        fig1, ax1 = plt.subplots(1, 1, figsize=(12, 8))
        fig2, ax2 = plt.subplots(1, 1, figsize=(12, 8))
        ax1.set_xlabel(f"Days Since {N_MIN} Cases", fontsize="large")
        ax2.set_xlabel(f"Days Since {N_MIN} Cases", fontsize="large")
        ax1.set_ylabel("Number of Cases", fontsize="large")
        ax2.set_ylabel(f'Number of Cases Per {capita:,}', fontsize='large')
        for i,statenation in enumerate(region_subset):
            data_subset_date = data_subset.loc[lambda df: df[statenation] > N_MIN, statenation]
            data_subset_capita_date = capita * data_subset_date.div(pops[statenation].iloc[0])
            ax1.plot(data_subset_date.values, label=statenation, 
                     marker="o", ms=5, c=clist[i]) 
            ax2.plot(data_subset_capita_date.values, label=statenation,
                     marker="o", ms=5, c=clist[i]) 
        if log is True:
            ax.set_ylim(bottom=100)
            ax1.semilogy()
            ax2.semilogy()
            ax1.yaxis.set_major_formatter(ScalarFormatter())
            ax2.yaxis.set_major_formatter(ScalarFormatter())
            filename1 = os.path.join(outdir, f"{region}_days_log.png")
            filename2 = os.path.join(outdir, f"{region}_capita_days_log.png")
            title1 = "Log Number of Cases Since 100 Infected"
            title2 = f"Log Number of Cases Per {capita:,} Since 100 Infected"
        else:
            filename1 = os.path.join(outdir, f"{region}_days.png")
            filename2 = os.path.join(outdir, f"{region}_capita_days.png")
            title1 = "Number of Cases Since 100 Infected"
            title2 = f"Number of Cases Per {capita:,} Since 100 Infected"
        fig1.suptitle(title1)
        fig2.suptitle(title2)
        ax1.legend()
        ax2.legend()
        fig1.savefig(filename1, bbox_inches="tight")
        print(f"Saved {filename1}")
        fig2.savefig(filename2, bbox_inches="tight")
        print(f"Saved {filename2}")

if __name__ == "__main__":
    regions = ["usa"]
    for item in regions:
        data, pops = get_data.get_data(item)
        overlaid_plots(item, data, pops)
