import numpy as np
import os
import matplotlib
matplotlib.use('agg')
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
    LAST_C = "lightcoral"

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
                 'Italy','South Korea','Mexico','Russia','Spain','Sweden','US']

EU_COUNTRIES = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia',
                'Denmark','Estonia','Finland','France','Germany','Greece',
                'Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg',
                'Malta','Netherlands','Poland','Portugal','Romania','Slovakia',
                'Slovenia','Spain','Sweden']

LATIN_COUNTRIES = ['Argentina','Belize','Bolivia','Brazil','Chile','Colombia',
                   'Costa Rica','Cuba','Dominican Republic','Ecuador',
                   'El Salvador','Guatemala','Honduras','Mexico','Nicaragua',
                   'Panama','Paraguay','Peru','Uruguay','Venezuela']

# Taken from matplotlib, and modified 
# https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/rainbow_text.html
def rainbow_text(x, y, strings, colors, styles=None, weights=None,
                 orientation='horizontal', ax=None, fig=None, 
                 tstring="axes", **kwargs):
    """
    Take a list of *strings* and *colors* and place them next to each
    other, with text strings[i] being shown in colors[i].

    Parameters
    ----------
    x, y : float
        Text position in data coordinates.
    strings : list of str
        The strings to draw.
    colors : list of color
        The colors to use.
    styles: list of styles
        Styles for each string 
    weights: list of weights
        Weights for each string 
    orientation : {'horizontal', 'vertical'}
    ax : Axes, optional
        The Axes to draw into. If None, the current axes will be used.
	t : transform to use for text coordinates
    **kwargs
        All other keyword arguments are passed to plt.text(), so you can
        set the font size, family, etc.
    """
    if ax is None:
        ax = plt.gca()

    tstring = tstring.lower()
    if tstring == "axes":
        t = ax.transAxes
    elif tstring == "data":
        t = ax.transData
    elif tstring == "figure":
        t = fig.transFigure
    elif tstring == "display":
        t = None
    elif tstring == "xaxis":
        t = ax.get_xaxis_transform()
    elif tstring == "yaxis":
        t = ax.get_yaxis_transform()
    else:
        t = None

    if styles == None:
        styles = "normal"
    if isinstance(styles, str):
        styles = [styles for x in strings]
    if weights == None:
        weights = "normal"
    if isinstance(weights, str):
        weights = [weights for x in strings]
    
    canvas = ax.figure.canvas

    assert orientation in ['horizontal', 'vertical']
    if orientation == 'vertical':
        kwargs.update(rotation=90, verticalalignment='bottom')

    for i in range(len(strings)):
        text = ax.text(x, y, strings[i], color=colors[i], 
                       transform=t, style=styles[i], weight=weights[i], 
                       **kwargs)

        # Need to draw to update the text position.
        text.draw(canvas.get_renderer())

        bbox = text.get_window_extent().transformed(t.inverted())
        if orientation == "horizontal":
            x = bbox.x1
        else:
            y = bbox.y1
    return bbox

def grid_plot(data, region, vax=False, outdir="plots", deaths=False, 
              *args, **kwargs):
    """
    Make subplot grid plots for each state/country of interest in list.
    Args:
        data (:obj:`pandas.DataFrame`): Covid statistics on region of interest.
        region (str): Country/state of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
        outdir (str): Name of directory to save plots to.
        deaths (Bool): If True, download data on deaths.
    """
  
    eu_usa_pops = {"US": 328, "EU": 445} 
    if vax is True:
        BAR_C = "lightskyblue"
        CONTRAST_C = "royalblue"
        ALPHA = 0.3
        OUTSIDE_PLOT_C = "dimgrey"
        VLINE_C = "darkgrey" 
        BOX_EDGE_C = "black"
        BOX_FACE_C = "lightgrey"
        LAST_C = "deepskyblue"
    else:
        BAR_C = "#e5aabc"
        CONTRAST_C = "crimson"
        ALPHA = 0.3
        OUTSIDE_PLOT_C = "dimgrey"
        VLINE_C = "darkgrey" 
        BOX_EDGE_C = "black"
        BOX_FACE_C = "lightgrey"
        LAST_C = "lightcoral"

    months = mdates.MonthLocator()
    
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if vax is True:
        lbl = "vax"
        plottitle = "fully vaccinated"
    elif deaths is True:
        lbl = "deaths"
        plottitle = "deaths"
    else:
        lbl = "cases"
        plottitle = "cases"

    if vax is True:
        partialdata,fullydata = get_data.vax_by_region(data)
        partial = partialdata.diff()
        fully = fullydata.diff()
        data = fullydata
    else:
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
        fontsize = "x-small"
        filename = f"states_new_{lbl}.pdf"
    elif region == "eu_vs_usa":
        if vax is True:
            partialdata["EU"] = partialdata.loc[:,EU_COUNTRIES].sum(axis=1)
            fullydata["EU"] = fullydata.loc[:,EU_COUNTRIES].sum(axis=1)
            partial = partialdata.diff()
            fully = fullydata.diff()
        else:
            data["EU"] = data.loc[:,EU_COUNTRIES].sum(axis=1)
            dailydata = data.diff()
        subplots = (2, 1)
        figsize = (15, 11)
        lw = 1.5
        labelsize = "medium"
        fontsize = "large"
        statenations = ["US", "EU"]
        filename = f"EU_vs_USA_{lbl}.pdf"
    elif region in ["worst_usa", "worst_global", "worst_world"]:
        if vax is True:
            avg_fully = fully.rolling(7, center=True, min_periods=2).mean()
            avg_partial = partial.rolling(7, center=True, min_periods=2).mean()
            fully_sorted = avg_fully.T.sort_values(avg_fully.index[-1], ascending=False).T
            partial_sorted = avg_partial.T.sort_values(avg_partial.index[-1], ascending=False).T
#            fully_statenations = fully_sorted.iloc[:, :10].columns.values
#            partial_statenations = partial_sorted.iloc[:, :10].columns.values
            statenations = fully_sorted.iloc[:, :10].columns.values
            if region == "worst_usa":
                filename = f"best_usa_{lbl}.pdf"
            else:
                filename = f"best_global_{lbl}.pdf"
        else:
            avg = dailydata.rolling(7, center=True, min_periods=2).mean()
            data_sorted = avg.T.sort_values(avg.index[-1], ascending=False).T
            statenations = data_sorted.iloc[:, :10].columns.values
            if region == "worst_usa":
                filename = f"worst_usa_{lbl}.pdf"
            else:
                filename = f"worst_global_{lbl}.pdf"
        subplots = (3, 3)
        figsize = (13, 10)
        lw = 1.5
        labelsize = "small"
        fontsize= "medium"
    else:
        raise KeyError("Region {region} not in acceptable values")

    if vax is True:
        avg_fully = fully.rolling(7, center=True, min_periods=2).mean()
        avg_partial = partial.rolling(7, center=True, min_periods=2).mean()
        avgs = [avg_fully]
        dailydatas = [fully]
        #avgs = [avg_partial, avg_fully]
        #dailydatas = [partial, fully]
    else:
        avg = dailydata.rolling(7, center=True, min_periods=2).mean()
        avgs = [avg]
        dailydatas = [dailydata]
    fig, axes = plt.subplots(subplots[0], subplots[1],
                             figsize=(figsize[0], figsize[1]),
                             sharex=True)
    plt.subplots_adjust(wspace=0.35)
    plt.subplots_adjust(hspace=0.35)

    #daily_sorted = dailydata.reindex(dailydata.sum(axis=0).sort_values(ascending=False).index, axis=1)

    for i,ax in enumerate(axes.flatten()):
        for k in range(len(avgs)):
            dailydata = dailydatas[k]
            if statenations[i] not in dailydata:
                continue
            avg = avgs[k]
            ax.bar(dailydata.index, dailydata[statenations[i]], color=BAR_C, zorder=5)
            ax.plot(avg[statenations[i]], c=CONTRAST_C, lw=lw, zorder=10)
            
            total = int(dailydata[statenations[i]].sum())
            lastval = int(dailydata[statenations[i]][-1])
            avglastval = int(avg[statenations[i]][-1])
            
            plt.gcf().autofmt_xdate(rotation=45, ha="center")
            
            ax.tick_params('both', labelsize=labelsize, length=3)
            ax.get_yaxis().set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
            ax.yaxis.set_ticks_position('both')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.xaxis.set_major_locator(months)
            ax.yaxis.get_major_ticks()[0].label1.set_visible(False)
            ax.yaxis.set_major_locator(plt.MaxNLocator(5))
            
            if region != "eu_vs_usa":
                max_avg = np.nanmax(avg[statenations[i]])
                ax.set_ylim(0, max_avg+0.08*max_avg)
                if vax is True:
                    ax.set_xlim(datetime.date(2021, 1, 1))
                else:
                    ax.set_xlim(datetime.date(2020, 2, 27))
                ax.annotate(f"{statenations[i]}, total: {total:,}", (0.035, 1.05), 
                    xycoords="axes fraction", size=fontsize)
                words = ["Last: ", f"{lastval:,}", "/", f"{avglastval:,}"]
                colors = ["black", LAST_C, "black", CONTRAST_C]
                weights = ["normal", "normal", "normal", "bold"]
                rainbow_text(0.035, .9, words, colors, weights=weights, ax=ax, fig=fig, tstring="axes", size=fontsize, zorder=15)
            else:
                if vax is True:
                    ax.set_xlim(datetime.date(2021, 1, 1), dailydata.index[-1]+datetime.timedelta(days=7))
                    # Use the last 7 days (exluding last 4 days which are unreliable)
                    # to estimate the growth in vax per day, then use that to determine
                    # when country reaches 70 and 90% population vaccinated.
                    x0 = 7
                    total_minus4 = int(dailydata[statenations[i]][:-4].sum())
                    recenty = avg[statenations[i]][-x0-4:-4].values
                    recentx = np.arange(len(recenty))
                    z = np.polyfit(recentx, recenty, 1)
                    p = np.poly1d(z)
                    pop = eu_usa_pops[statenations[i]] * 1e6
                    perc70 = (pop * 0.7) - total_minus4
                    perc90 = (pop * 0.9) - total_minus4
                    x = np.arange(x0, x0+1095)
                    emp = p(x)
                    # Biden has stated a goal of 5 million doses a day. Let's say
                    # this equates to 2.1 million people fully vaccinated a day.
                    emp = np.where(emp > 2.1e6, 2.1e6, emp)
                    cumul = np.cumsum(emp)
                    ndays70 = int(np.where(cumul > perc70)[0][0]) 
                    ndays90 = int(np.where(cumul > perc90)[0][0])
                    perc70date = dailydata.index[-4] + datetime.timedelta(days=ndays70)
                    perc90date = dailydata.index[-4] + datetime.timedelta(days=ndays90)
                else:
                    ax.set_xlim(datetime.date(2020, 2, 21), dailydata.index[-1]+datetime.timedelta(days=7))
                # Get the maximum number of intervals/10,000s of cases so far
                lbl_days_thresh = 15
                lbl_d_thresh = 6
                lbl_num_thresh = 3
                if lbl == "deaths":
                    interval = 40000
                    unit = 1000
                    vline_lbl = "k"
                    vline_lbl_tiny = "k"
                elif lbl == "vax":
                    interval = 10000000
                    unit = 1000000
                    vline_lbl = " million"
                    vline_lbl_tiny = " million"
                    lbl_days_thresh = 5
                    lbl_d_thresh = 4
                    lbl_num_thresh = 3
                else:
                    interval = 1000000
                    unit = 1000000
                    vline_lbl = " mil"
                    vline_lbl_tiny = "m"
                if vax is True:
                    maxinterval = fullydata[statenations[i]][-1] - fullydata[statenations[i]][-1] % interval
                else:
                    maxinterval = data[statenations[i]][-1] - data[statenations[i]][-1] % interval
                intervals = np.concatenate((np.array([100]),
                                            np.arange(interval, maxinterval+interval, interval)))
                # The indices for the next entry after each interval unit
                if vax is True:
                    intervals_inds = [np.argmax(fullydata[statenations[i]] > x) for x in intervals]
                else:
                    intervals_inds = [np.argmax(data[statenations[i]] > x) for x in intervals]
                # Vertical lines will be put at 100 cases and each million afterward
                # The last index is for marking the last date, but no vline
                vline_inds = intervals_inds + [len(dailydata)-1]
                ndays = np.array(vline_inds)[1:] - np.array(vline_inds)[:-1]
                # Get the transformation function the data coordinates in X and
                # axis fraction in Y
                trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)
                # Make one continuous line from 100 cases to last date
                ax.plot([dailydata.index[[intervals_inds[0]]], dailydata.index[[vline_inds[-1]]]],
                        [1.03, 1.03], transform=trans, color=OUTSIDE_PLOT_C, lw=.9,  
                        clip_on=False)
                skip = False
                for j in range(len(vline_inds)):
                    # If on the last index (last entry in dataset), we don't plot the vline
                    # or little | symbol
                    if j == len(vline_inds)-1:
                        continue
                    
                    ant_kwargs = {"size": 8, "color": OUTSIDE_PLOT_C, "va": "center", "ha": "center",
                                  "xycoords": ("data", "axes fraction")}
                    # This makes the | symbol at the end of each time segment
                    ax.annotate("|", xy=(dailydata.index[[vline_inds[j]]], 1.03), 
                                **ant_kwargs)
                    
                    # Annotate how many days elapsed since last integer million cases
                    # Extra annotation at the end for last integer million -> now
                    # Depending on number of days in the interval, the time unit
                    # will be days, d, no unit at all, or no number at all
                    middle_i = vline_inds[j] + int(ndays[j]/2)
                    if ndays[j] > lbl_days_thresh: 
                        elapsed_lbl = f"{ndays[j]} days"
                    elif ndays[j] >= lbl_d_thresh:
                        elapsed_lbl = f"{ndays[j]}d"
                    elif ndays[j] >= lbl_num_thresh:
                        elapsed_lbl = f"{ndays[j]}"
                    else:
                        elapsed_lbl = ""
                    ax.annotate(elapsed_lbl, (dailydata.index[[middle_i]], 1.05), 
                        xycoords= ("data", "axes fraction"), ha="center", 
                        color=OUTSIDE_PLOT_C, style="italic")
                    
                    # Make a vertical line in the plot.
                    # Annotate how many cases/deaths occurred in the interval period.
                    ax.axvline(dailydata.index[[vline_inds[j]]], color=VLINE_C, 
                               ls="dotted", 
                               alpha=0.7, zorder=0)
                   
                    # Make the label for the vline (e.g. 8 mil or 200k)
                    # Depending on the number of days in the interval, the unit
                    # label may change
                    number = f"{intervals[j]/unit:.0f}"
                    ant_kwargs = {}
                    time_off = 6
                    if skip == True:
                        lab = ""
                        skip = False
                    elif len(number) == 1:
                        if ndays[j] > 10 or j == len(vline_inds)-2:
                            lab = f"{number}{vline_lbl}"
                        elif ndays[j] < 7:
                            lab = f"{number}"
                        else:
                            lab = f"{number}{vline_lbl_tiny}"
                    else:
                        if j == len(vline_inds)-2:
                            lab = f"{number}{vline_lbl_tiny}"
                        elif ndays[j] > 14:
                            lab = f"{number}{vline_lbl}"
                        elif ndays[j] < 11:
                            lab = f"{number}"
                            if ndays[j] < 5:
                                ant_kwargs = {"size": 8}
                            elif ndays[j] < 6:
                                ant_kwargs = {"size": 8.5}
                            if number[0] == "2":
                                time_off = -1
                            else:
                                time_off = -6
                        else:
                            lab = f"{number}{vline_lbl_tiny}"
                    if j == 0:
                        lab = "100"
                    ax.annotate(lab, 
                                (dailydata.index[[vline_inds[j]]]+datetime.timedelta(hours=time_off), .93),
                                xycoords=("data", "axes fraction"), 
                                style="italic", color=VLINE_C, **ant_kwargs)
                
            
                # Define axis fraction coords for the Total and Last annotations
                # and the box surrounding them
                text_x0 = 0.027
                text_x1 = [0]
                text_y0 = 0.84
                bbox = rainbow_text(text_x0, text_y0, [f"Total: {total:,}"], ["black"], ax=ax, fig=fig, 
                                    tstring="axes", size=fontsize, styles="italic", ha="left",
                                    va="center", zorder=20)
                text_x1.append(bbox.x1)
                text_y1 = 0.75
                words = ["Last: ", f"{lastval:,}", "/", f"{avglastval:,}"]
                colors = ["black", LAST_C, "black", CONTRAST_C]
                weights = ["normal", "normal", "normal", "bold"]
                bbox = rainbow_text(text_x0, text_y1, words, colors, ax=ax, fig=fig, 
                                    tstring="axes", weights=weights, styles="italic", 
                                    size=fontsize, ha="left", va="center", zorder=20)
                text_x1.append(bbox.x1)
                max_x = max(text_x1)
                box = Rectangle((text_x0-0.003, text_y1-0.03), (max_x-text_x0)+0.006, .08*2, 
                    transform=ax.transAxes, edgecolor=BOX_EDGE_C, facecolor=BOX_FACE_C, alpha=0.5, zorder=20)
                ax.add_patch(box)
            
                
                if vax is True:
                    words70 = ['70%: ', f'{perc70date:%b %d %Y}'] 
                    words90 = [ '90%: ', f'{perc90date:%b %d %Y}']
                    colors = ['black', 'black']
                    weights = ['normal', 'normal']
                    text_y2 = 0.66
                    bbox = rainbow_text(text_x0, text_y2, words70, colors, weights=weights, ax=ax, fig=fig, tstring="axes", size=fontsize, styles='italic', ha='left', va='center', zorder=20)
                    text_x1.append(bbox.x1)
                    text_y3 = 0.57
                    bbox = rainbow_text(text_x0, text_y3, words90, colors, weights=weights, ax=ax, fig=fig, tstring="axes", size=fontsize, styles='italic', ha='left', va='center', zorder=20)
                    text_x1.append(bbox.x1)
                    max_x = max(text_x1)
                    box = Rectangle((text_x0-0.003, text_y3-0.03), (max_x-text_x0)+0.006, .08*2, 
                        transform=ax.transAxes, edgecolor=BOX_EDGE_C, facecolor=BOX_FACE_C, alpha=0.5, zorder=20)
                    ax.add_patch(box)

                # Define US and EU population (in units of intervals) by hand
                # and write a title
                if vax is True:
                    vaccinated = round((total / (eu_usa_pops[statenations[i]] * 1e6)) * 100.)
                    lab = f"$\\bf{statenations[i]}$, population: {eu_usa_pops[statenations[i]]:,} million ({vaccinated}% vaccinated)"
                elif deaths is False:
                    infected = round((total / (eu_usa_pops[statenations[i]] * 1e6)) * 100.)
                    lab = f"$\\bf{statenations[i]}$, population: {eu_usa_pops[statenations[i]]:,} million ({infected}% infected)"
                else:
                    lab = f"$\\bf{statenations[i]}$, population: {eu_usa_pops[statenations[i]]:,} million ({mort[statenations[i]]}% mortality)"
                ax.set_title(lab, loc="left", pad=27, fontsize=fontsize)
  

   
    if region == "eu_vs_usa": 
        # Set both US and EU ylim maximum to the same value 
        us_ymax = axes[0].get_ylim()[1]
        eu_ymax = axes[1].get_ylim()[1]
        max_max = max(us_ymax, eu_ymax)
        max_max_buffer = max_max + (0.05 * max_max)
        axes[0].set_ylim(0, max_max_buffer)
        axes[1].set_ylim(0, max_max_buffer)

    words = ["Last: ", "value", "/", "7 day average"]
    colors = ["black", LAST_C, "black", CONTRAST_C]
    weights = ["normal", "normal", "normal", "bold"]
    ax = plt.gca()
    canvas = ax.figure.canvas
    t = fig.transFigure
    text = ax.text(0.5, .945, "".join(words), color="white", 
                   transform=t, size='x-large', ha="center")
    text.draw(canvas.get_renderer())
    bbox = text.get_window_extent().transformed(t.inverted())
    x0 = bbox.x0
    
    rainbow_text(x0, .945, words, colors, weights=weights, fig=fig, tstring="figure", size='x-large')
    plt.suptitle(f'New daily {plottitle}\n{dailydata.index[-1]:%B %d, %Y}',
                 fontsize='x-large', y=1.01)
    outfilename = os.path.join(outdir, filename)
    plt.savefig(outfilename, bbox_inches='tight')
    print(f"Saved {outfilename}")

def mortality_rate(statenation, d_data, c_data):
    """
    Determine the mortality rate for a given state or country.
    Args:
        statenation (str): Name of state or country.
        d_data (`:obj:pd.dataframe`): Deaths data.
        c_data (`:obj:pd.dataframe`): Cases data.
    Returns:
        mort (int): Mortality rate.
    """

    if statenation == "EU": 
        d_data["EU"] = d_data.loc[:,EU_COUNTRIES].sum(axis=1)
        c_data["EU"] = c_data.loc[:,EU_COUNTRIES].sum(axis=1)
    d_dailydata = d_data.diff()
    c_dailydata = c_data.diff()
    c_total = int(c_dailydata[statenation].sum())
    d_total = int(d_dailydata[statenation].sum())
    mort = round((d_total / c_total) * 100.)

    return mort

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deaths", action="store_true",
                        default=False,
                        help="Switch to plot deaths instead of cases")
    parser.add_argument("-v", "--vax", action="store_true",
                        default=False,
                        help="Switch to plot vaccination rates")
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
        if args.vax is True:
            data, pops = get_data.get_data(item, vax=True)
        else:
            data, pops = get_data.get_data(item, deaths=args.deaths)
        if item == "eu_vs_usa" and args.deaths is True:
            data2, pops2 = get_data.get_data(item, deaths=False)
            usa_mort = mortality_rate("US", data, data2)
            eu_mort = mortality_rate("EU", data, data2)
            mort = {"US": usa_mort, "EU": eu_mort}
            grid_plot(data, item, deaths=args.deaths, mort=mort, vax=args.vax)
        else:
            grid_plot(data, item, deaths=args.deaths, vax=args.vax)
