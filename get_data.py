import pandas as pd
import wget
import os
import time

JHU_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"

def download_data(region, deaths=False, url=JHU_URL, outdir="data"):
    if region in ["world", "global", "latin", "eu_vs_usa"]:
        if deaths is True:
            filename = "time_series_covid19_deaths_global.csv"
        else:
            filename = "time_series_covid19_confirmed_global.csv"
    else:
        if deaths is True:
            filename = "time_series_covid19_deaths_US.csv"
        else:
            filename = "time_series_covid19_confirmed_US.csv"
   
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    outfilename = os.path.join(outdir, filename)
    if os.path.exists(outfilename):
        filetime = os.path.getmtime(outfilename)
        now = time.time()
        if now - filetime <= 43200: #43200s = 12 hours
            print(f"File {outfilename} already up to date")
            return outfilename
        else:
            os.remove(outfilename)

    wget.download(os.path.join(url, filename), outfilename)
    print(f"\nDownloaded {outfilename}")

    return outfilename

def read_data(filename, region):
    if region in ["world", "global", "latin", "eu_vs_usa"]:
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
        statepops0 = pd.read_csv('nst-est2019-01.csv',index_col='State')
        statepops = statepops0.T
    try:
        b.drop(columns="Population", inplace=True)
    except KeyError:
        pass
    dt_index = pd.to_datetime(b.columns)
    data = b.T
    data = data.reindex(dt_index)

    return data, statepops

def get_data(region, deaths=False):
    filename = download_data(region, deaths=deaths)
    data, statepops = read_data(filename, region)
    return data, statepops
