'''
Script to make a movie showing the weekly progression of COVID on 
a county level.

Using the percentile option, the weekly cases by population, are broken
down into nationwide percentiles, and shown on a map.  

Using the percapita option, the weekly cases by population, mapped by  
number of cases per 1000 people.  

This script takes the US county shapefiles and population data and 
merges them into a single geopandas dataframe. This is then combined 
with the COVID19 data to make the maps.

The ffmpeg magic incantation that works on Apple Silicon is:

    > ffmpeg -r 1 -f image2 -pattern_type glob -i '*.jpg' -vcodec libx264 -an outfile.mp4

Requirements
------------
Besides the python dependencies, this script requires the FFMPEG
be installed on the system. 
'''
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pandas as pd
import geopandas as gpd
import numpy as np
import argparse
from copy import copy
from datetime import datetime
import sys
import os

from covidplots.get_data import download_data
#Colormap to use
CMAPNAME = 'Blues'
VMIN = 0.001
VMAX = 50


def prepare_data():
    #Reading in government tables.
    allpop = pd.read_csv('geo_pop_data/co-est2020.csv') 
    map_df = gpd.read_file('geo_pop_data/cb_2019_us_county_500k.shp')

    #Keep only the 50 states and DC
    idx = map_df.STATEFP.astype('float')<57
    map_df = map_df[idx]

    #Extracting population information
    allpop['FIPS'] = [f'{st:0>2d}{cty:0>3d}' for st,cty in np.array(allpop[['STATE','COUNTY']].values,dtype=int)]

    pop = allpop[['FIPS','POPESTIMATE2019']] 

    #Extracting map information
    map_df['FIPS'] = [f'{st:0>2d}{cty:0>3d}' for st,cty in np.array(map_df[['STATEFP','COUNTYFP']].values,dtype=int)]  

    maps = copy(map_df[['FIPS','geometry','ALAND']])
    maps.ALAND = maps.ALAND/2.59e6   #Convert square meters to square miles.

    data = maps.merge(pop,on='FIPS')
    data.FIPS = data.FIPS.astype('float')


    #Reading in the COVID data
    covid = pd.read_csv('covid_data/time_series_covid19_confirmed_US.csv',
                        index_col='FIPS')
    countynames = covid.Combined_Key
    covid.drop(columns=['UID','iso2','iso3','code3','Combined_Key',
                        'Admin2','Province_State','Country_Region',
                        'Lat','Long_'],
               inplace=True)

    covid = covid.diff(axis=1)
    covid[covid<0.] = 0.  #Removing negative values


    dt_idx = pd.to_datetime(covid.columns)
    covid = covid.T
    covid.index = dt_idx
    covid = covid.iloc[5:].resample('W',label='right',closed='right').sum()
    covid.rename(index=str,inplace=True)
    covid = covid.T
    covid = pd.concat([countynames,covid],axis=1,ignore_index=False)

    data = data.merge(covid,on='FIPS') 

    data[data.columns[5:]] = 1000*data[data.columns[5:]].div(data.POPESTIMATE2019,axis=0)

    #Setting the map projection
    data.to_crs('EPSG:2163',inplace=True)

    return data

def fig_setup(figtype):

    #Setting up figure
    fig,ax = plt.subplots(1,figsize=(8,5))
    ax.axis('off')
    ax.set_xlim(-2.2e6,2.7e6)
    ax.set_ylim(-2.3e6,9e5)
    date_text = ax.text(0.5,0.95,'',transform=ax.transAxes,
                        horizontalalignment='center',fontsize=16)

    #Adding a colorbar

    if figtype == 'percentile':

        sm = plt.cm.ScalarMappable(cmap=plt.cm.get_cmap(CMAPNAME,10),
                            norm=plt.Normalize(vmin=0,vmax=100))
        cbar = fig.colorbar(sm,orientation='horizontal',label='Percentile',
                            fraction=0.025,pad=0.1,aspect=30)
        cbar.set_ticks([0,20,40,60,80,100])

    elif figtype == 'percapita':

        sm = plt.cm.ScalarMappable(cmap=CMAPNAME,
                           norm=colors.LogNorm(vmin=VMIN,vmax=VMAX))
        cbar = fig.colorbar(sm,orientation='horizontal',label='Cases per 1000',
                            fraction=0.025,pad=0.1,aspect=30)

    return fig,ax,sm,date_text


#Function that makes cloropleth
def make_plots(data,plot_type):

    for col in data.columns[5:]:
    
        outputfile = f'plots/county_maps/{plot_type}_{col[:10]}.jpg'

        if not os.path.exists(f'{outputfile}'):

            dt1 = datetime.now()
            fig,ax,cmap,date_text = fig_setup(plot_type)

            if 'covidplots' not in plt.colormaps():
                plt.cm.register_cmap(name='covidplots',cmap=cmap.cmap)

            if plot_type == 'percentile':
                ax = data.plot(column=col,cmap='covidplots',scheme='percentiles',
                               classification_kwds={'pct':[0,10,20,30,40,50,60,70,80,90,100]},
                               linewidth=0.25,ax=ax,edgecolor='0.5')
                date_text.set_text(f'{col[:10]}')
           
            else:
                ax = data.plot(column=col,cmap=cmap.cmap,
                               norm=colors.LogNorm(vmin=VMIN,vmax=VMAX),
                               linewidth=0.25,ax=ax,edgecolor='0.5')
                date_text.set_text(f'{col[:10]}')

            fig.tight_layout()
            fig.savefig(f'{outputfile}',dpi=200)
            plt.close(fig)
            print(f'Created {outputfile} {(datetime.now()-dt1).total_seconds():5.2f}')

        else:
            print(f'Skipping {outputfile}')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--percentile',action='store_true',
           default=False,
           help='Switch to plot percentile')
    parser.add_argument('--percapita',action='store_true',
           default=False,
           help='Switch to plot per-capita')
    
    args = parser.parse_args()

    if args.percentile or args.percapita:
        data = prepare_data()
    else:
        sys.exit('Please choose at least one of "percentile" and "percapita" to plot.')


    if args.percentile:

        make_plots(data,'percentile')

    if args.percapita:

        make_plots(data,'percapita')
