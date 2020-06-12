import pandas as pd
import wget
import os

JHU_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"

def get_data(world=False, usa=False, deaths=False, url=JHU_URL):
    assert world==True or usa==True, "Must specify either USA or global numbers"
    if world is True:
        if deaths is True:
            filename = "time_series_covid19_deaths_global.csv"
        else:
            filename = "time_series_covid19_confirmed_global.csv"
    else:
        if deaths is True:
            filename = "time_series_covid19_deaths_US.csv"
        else:
            filename = "time_series_covid19_confirmed_US.csv"
    
    wget.download(os.path.join(url, filename), filename)
    print(f"\nDownloaded file {filename}")

    return filename

def read_data(filename, world=False, usa=False):
    assert world==True or usa==True, "Must specify either USA or global numbers"
    if world is True:
        a = pd.read_csv(filename)
        b = a.groupby('Country/Region').sum()
        b.drop(columns=['Lat','Long'], inplace=True)
        statepops = None
    else:
        a = pd.read_csv(filename, index_col='UID')
        a.drop(columns=['iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 
                    'Country_Region','Lat','Long_','Combined_Key'], 
                    inplace=True)
        b = a.groupby('Province_State').sum()
        statepops = pd.read_csv('nst-est2019-01.csv',index_col='State')
    dt_index = pd.to_datetime(b.columns)
    data = b.T
    data = data.reindex(dt_index)

    return data, statepops

