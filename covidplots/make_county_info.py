'''
Script to merge together the US county shapefiles and population 
data into a single pandas dataframe. This can then be used with
the COVID19 data to make some maps.
'''
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import geopandas as gpd
import numpy as np
from astropy.time import Time

import matplotlib.pyplot as plt

vmin,vmax = 0,5000
cmap = 'pink_r'

#Reading in government tables.
allpop = pd.read_csv('data/county_pop.csv') 
map_df = gpd.read_file('data/cb_2019_us_county_500k.shp')


#Extracting population information
allpop['FIPS'] = [f'{st:0>2d}{cty:0>3d}' for st,cty in np.array(allpop[['STATE','COUNTY']].values,dtype=int)]

pop = allpop[['FIPS','POPESTIMATE2019']] 


#Extracting map information
map_df['FIPS'] = [f'{st:0>2d}{cty:0>3d}' for st,cty in np.array(map_df[['STATEFP','COUNTYFP']].values,dtype=int)]  

maps = map_df[['FIPS','geometry']]

data = maps.merge(pop,on='FIPS')
data.FIPS = data.FIPS.astype('float')


#Reading in the COVID data
covid = pd.read_csv('data/time_series_covid19_confirmed_US.csv',
                    index_col='FIPS')
covid.drop(columns=['UID','iso2','iso3','code3','Combined_Key',
                    'Admin2','Province_State','Country_Region',
                    'Lat','Long_'],
           inplace=True)

covid = covid.diff(axis=1)

dt_idx = pd.to_datetime(covid.columns)
covid = covid.T
covid = covid.reindex(dt_idx)
covid = covid.iloc[5:].resample('W',label='right',closed='right').sum()
covid.rename(index=str,inplace=True)
covid = covid.T

data = data.merge(covid,on='FIPS') 

#data[data.columns[3:]] = 1000*data[data.columns[3:]].div(data.POPESTIMATE2019,axis=0)


for col in data.columns[3:]:

    fig,ax = plt.subplots(1,figsize=(24,15.41),num=col)
    ax.axis('off')
   
    vmax = 0.05*data[col].max()
    print(vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap,
                               norm=plt.Normalize(vmin=vmin,vmax=vmax)
                               )
    sm.set_array([])
    
    #cbar = fig.colorbar(sm)
    #cbar.set_ticks([])
    
    data.plot(column=col,cmap=cmap,vmin=vmin,vmax=vmax,
              linewidth=0.25,ax=ax,edgecolor='0.5')
    ax.set_xlim(-128,-66)
    ax.set_ylim(23,50)
    ax.annotate(f'{col[:10]}',xy=(0.5,0.105),xycoords='figure fraction',
               horizontalalignment='center',fontsize=32)

    #plt.suptitle(col[:10],fontsize='x-large')
    plt.savefig(f'plots/maps/{col[:10]}.jpg',bbox_inches='tight')

    plt.close(col)
