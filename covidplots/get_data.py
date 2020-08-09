import pandas as pd
import wget
import os
import time

JHU_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"

def download_data(region, deaths=False, url=JHU_URL, outdir="data"):
    """
    Download CSV files from JHU.
    Args:
        region (str): Country of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
        deaths (Bool): If True, download data on deaths.
        url (str): URL of JHU repository+directory that houses CSV files.
        outdir (str): Name of directory to download data to.
    Returns:
        outfilename (str): Path of downloaded CSV file.
    """

    if region in ["usa", "us", "worst_usa"]:
        if deaths is True:
            filename = "time_series_covid19_deaths_US.csv"
        else:
            filename = "time_series_covid19_confirmed_US.csv"
    else:
        if deaths is True:
            filename = "time_series_covid19_deaths_global.csv"
        else:
            filename = "time_series_covid19_confirmed_global.csv"
   
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
    """
    Read data from JHU CSV files and format into a pandas DataFrame.
    Args:
        outfilename (str): Path of downloaded CSV file.
        region (str): Country of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
    Returns:
        data (:obj:`pandas.DataFrame`): Covid statistics on region of interest.
        pops (:obj:`pandas.DataFrame`): Population statistics on region of interst.
    """
    if region in ["usa", "us", "worst_usa"]:
        a = pd.read_csv(filename, index_col='UID')
        a.drop(columns=['iso2', 'iso3', 'code3', 'FIPS', 'Admin2', 
                    'Country_Region','Lat','Long_','Combined_Key'], 
                    inplace=True)
        b = a.groupby('Province_State').sum()
        pops0 = pd.read_csv('nst-est2019-01.csv',index_col='State')
        pops = pops0.T
    else:
        a = pd.read_csv(filename)
        b = a.groupby('Country/Region').sum()
        b.drop(columns=['Lat','Long'], inplace=True)
        pops0 = pd.read_csv("Census_data_20200726.csv", skiprows=1)
        pops0.drop_duplicates(subset="Country", inplace=True) 
        pops0.drop(columns=['Region', 'Year', 'Area (sq. km.)',
               'Density (persons per sq. km.)'], inplace=True)
        pops0.set_index("Country", inplace=True)
        pops = pops0.T
    try:
        b.drop(columns="Population", inplace=True)
    except KeyError:
        pass
    dt_index = pd.to_datetime(b.columns)
    data = b.T
    data = data.reindex(dt_index)

    return data, pops

def get_data(region, deaths=False):
    """
    Convenience function to download and read JHU CSV files.
    Args:
        region (str): Country of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
        deaths (Bool): If True, download data on deaths.
    Returns:
        data (:obj:`pandas.DataFrame`): Covid statistics on region of interest.
        pops (:obj:`pandas.DataFrame`): Population statistics on region of interst.
    """
    
    filename = download_data(region, deaths=deaths)
    data, pops = read_data(filename, region)
    return data, pops
