import argparse

import get_data
import grid_plots
import overlaid_plots

def make_all_plots(deaths=False):
    # Get all data
    data_usa, pops_usa = get_data.get_data("usa", deaths=deaths)
    data_world, pops_world = get_data.get_data("world", deaths=deaths)

    regions = ["world", "usa", "latin", "eu_vs_usa"]
    datas = [data_world, data_usa, data_world, data_world]
    pops = [pops_world, pops_usa, pops_world, pops_world]
    # Make grid plots
    for r,d,p in zip(regions, datas, pops):
        grid_plots.grid_plot(d, r, deaths=deaths)

    # Make overlaid plots
    overlaid_plots.overlaid_plots("usa", data_usa, pops_usa, deaths=deaths)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deaths", action="store_true",
                        default=False,
                        help="Switch to plot deaths instead of cases")
    args = parser.parse_args()

    make_all_plots(args.deaths) 
