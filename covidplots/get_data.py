import pandas as pd
import wget
import os
import time

from covidplots.continents import fix_jhu_df, fix_census_df, fix_owid_df

JHU_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"
OWID_URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations"

def download_vaccine_data(region, url=OWID_URL, outdir="covid_data"):
    """
    Download CSV file from Our World In Data.
    Args:
        region (str): Country of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
        url (str): URL of OWID repository+directory that houses CSV files.
        outdir (str): Name of directory to download data to.
    Returns:
        outfilename (str): Path of downloaded file.
    """

    if region in ["usa", "us", "worst_usa"]:
        filename = "us_state_vaccinations.csv"
    else:
        filename = "vaccinations.csv"
   
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
    print(f"\n ⬇️  Downloaded {outfilename}")

    return outfilename

def download_data(region, deaths=False, url=JHU_URL, outdir="covid_data"):
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
    print(f"\n ⬇️  Downloaded {outfilename}")

    return outfilename

def read_vaccine_data(filename, region):
    """
    Read data from OWID CSV files and format into a pandas DataFrame.
    Global populations from here:
    https://www.census.gov/data-tools/demo/idb/region.php?T=6&RT=0&A=separate&Y=2020&C=&R=1
    Args:
        filename (str): Path of downloaded CSV file.
        region (str): Country of interest. Acceptable values are 'world', 
            'usa', 'latin', 'eu_vs_usa', 'worst_usa', 'worst_global'.
    Returns:
        data (:obj:`pandas.DataFrame`): Vaccine statistics on region of interest.
        pops (:obj:`pandas.DataFrame`): Population statistics on region of interst.
    """
    if region in ["usa", "us", "worst_usa"]:
        data = pd.read_csv(filename)
        data = fix_owid_df(data, world=False)
        data.drop(data.loc[data["location"] == "United States"].index, inplace=True)
        pops0 = pd.read_csv('geo_pop_data/nst-est2019-01.csv',index_col='State')
        pops = pops0.T
    else:
        data = pd.read_csv(filename)
        data = fix_owid_df(data)
        regions = ["Africa", "Asia", "European Union", "Europe", "North America", "Oceania", "South America", "World", "United Kingdom"]
        data.drop(data.loc[data["location"].isin(regions)].index, inplace=True)
        pops0 = pd.read_csv("geo_pop_data/Census_data_2020_world_regions.csv", skiprows=1)
        pops0.drop_duplicates(subset="Country", inplace=True) 
        pops0.drop(columns=['Region', 'Year', 'Area (sq. km.)',
               'Density (persons per sq. km.)'], inplace=True)
        pops0.set_index("Country", inplace=True)
        pops = pops0.T
        pops = fix_census_df(pops)

    data["date"] = pd.to_datetime(data["date"])

    return data, pops

def vax_by_region(data):
    """
    Convert the OWID vaccination dataframe so that each column is a country/state,
    and the index is the date. Create a DF for number of people fully vaccinated
    and number of people partially vaccinated.

    Args:
        data (:obj:`pandas.DataFrame`): Vaccine statistics.
    Returns:
        partial (:obj:`pandas.DataFrame`): Number of partially vaccinated people
            for each country/state.
        fully (:obj:`pandas.DataFrame`): Number of fully vaccinated people for 
            each country/state.
    """
    
    partial = data[['date', 'location', 'people_vaccinated']].copy()
    fully = data[['date', 'location', 'people_fully_vaccinated']].copy()
    fully = fully.pivot(index='date', 
        columns=[x for x in fully.columns if x not in ['date', 'people_fully_vaccinated']],
        values='people_fully_vaccinated').reset_index()
    partial = partial.pivot(index='date', 
        columns=[x for x in partial.columns if x not in ['date', 'people_vaccinated']],
        values='people_vaccinated').reset_index()
    partial.set_index('date', inplace=True)
    fully.set_index('date', inplace=True)
    partial = partial.fillna(method='ffill')
    partial = partial.fillna(0)
    fully = fully.fillna(method='ffill')
    fully = fully.fillna(0)
    return partial, fully

def read_data(filename, region):
    """
    Read data from JHU CSV files and format into a pandas DataFrame.
    Global populations from here:
    https://www.census.gov/data-tools/demo/idb/region.php?T=6&RT=0&A=separate&Y=2020&C=&R=1
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
        pops0 = pd.read_csv('geo_pop_data/nst-est2019-01.csv',index_col='State')
        pops = pops0.T
    else:
        a = pd.read_csv(filename)
        b = a.groupby('Country/Region').sum()
        b.drop(columns=['Lat','Long'], inplace=True)
        
        pops0 = pd.read_csv("geo_pop_data/Census_data_2020_world_regions.csv", skiprows=1)
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
    data.index = dt_index

    # There are few countries that need reformatting
    if region not in ["usa", "us", "worst_usa"]:
        data = fix_jhu_df(data)
        pops = fix_census_df(pops)

    return data, pops

def get_data(region, deaths=False, vax=False):
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
    
    if vax is True:
        filename = download_vaccine_data(region)
        data, pops = read_vaccine_data(filename, region)
    else:
        filename = download_data(region, deaths=deaths)
        data, pops = read_data(filename, region)
    return data, pops
