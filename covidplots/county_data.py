import pandas as pd
import geopandas as gpd
import numpy as np

def get_data():

    path = 'Covid19scripts/covidplots/data'
    #Reading in government tables.
    allpop = pd.read_csv(f'{path}/county_pop.csv')
    map_df = gpd.read_file(f'{path}/cb_2019_us_county_500k.shp')


    #Extracting population information
    allpop['FIPS'] = [f'{st:0>2d}{cty:0>3d}' for st,cty in np.array(allpop[['STATE','COUNTY']].values,dtype=int)]
    allpop['countyname'] = [f'{cty}, {st}' for cty,st in np.array(allpop[['CTYNAME','STNAME']].values)]


    pop = allpop[['FIPS','countyname','POPESTIMATE2019']]


    #Extracting map information
    map_df['FIPS'] = [f'{st:0>2d}{cty:0>3d}' for st,cty in np.array(map_df[['STATEFP','COUNTYFP']].values,dtype=int)]

    maps = map_df[['FIPS','geometry','ALAND']]

    data = maps.merge(pop,on='FIPS')
    #data.FIPS = data.FIPS.astype('float')


    ##Reading in the COVID data
    #covid = pd.read_csv('data/time_series_covid19_confirmed_US.csv',
    #                    index_col='FIPS')
    #countynames = covid.Combined_Key
    #covid.drop(columns=['UID','iso2','iso3','code3','Combined_Key',
    #                    'Admin2','Province_State','Country_Region',
    #                    'Lat','Long_'],
    #           inplace=True)

    #covid = covid.diff(axis=1)


    #dt_idx = pd.to_datetime(covid.columns)
    #covid = covid.T
    #covid = covid.reindex(dt_idx)
    #covid = covid.iloc[5:].resample('W',label='right',closed='right').sum()
    ##covid = covid.diff()
    #covid.rename(index=str,inplace=True)
    #covid = covid.T
    #covid = pd.concat([countynames,covid],axis=1,ignore_index=False)

    #data = data.merge(covid,on='FIPS')

    #data[data.columns[4:]] = 1000*data[data.columns[4:]].div(data.POPESTIMATE2019,axis=0)

    return data

if __name__ == "__main__":

    a = get_data()
