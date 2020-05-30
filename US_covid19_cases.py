import pandas as pd
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, output_file, show
from datetime import datetime

matplotlib.use('agg')
matplotlib.style.use('ggplot')
plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True
figsize=(12,8)

plotstates = ['Arkansas','California','Indiana','Maryland','New Jersey','New York','Ohio','Texas','Washington']
clist = plt.cm.Accent(np.linspace(0,1,len(plotstates)))



def cases_per_million(statesdata,statepops):

    N_min=1
    capita=100000

    plt.figure(figsize=figsize,num='per_million')

    for i,statename in enumerate(statesdata[plotstates]):

        data = statesdata.loc[lambda df:capita*df[statename]/statepops.loc[statename].values>N_min,statename] 
        data = capita*data/statepops.loc[statename].values

        if data.empty:

            print(f'{statename} has not reached {N_min} cases yet.')

        else:

            plt.plot(data.values,label=statename,marker='o',ms=5,c=clist[i])

    #plt.semilogy()
    plt.legend()

    plt.xlabel(f'Number of days since {N_min} case per {capita:,}',fontsize='large')
    plt.ylabel(f'Number of cases per {capita:,} people',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_per_million_US.png',bbox_inches='tight')
    plt.close(fig='per_million')


def cases_per_million_by_date(statesdata,statepops):

    N_min=1
    capita=100000

    plt.figure(figsize=figsize,num='per_million_by_date')

    for i,statename in enumerate(statesdata[plotstates]):

        data = statesdata.loc[lambda df:capita*df[statename]/statepops.loc[statename].values>N_min,statename] 
        data = capita*data/statepops.loc[statename].values

        if data.empty:

            print(f'{statename} has not reached {N_min} cases yet.')

        else:

            plt.plot(data,label=statename,marker='o',ms=5,c=clist[i])

    #plt.semilogy()
    plt.legend()

    plt.xlabel(f'Date',fontsize='large')
    plt.ylabel(f'Number of cases per {capita:,} people',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_per_million_by_date_US.png',bbox_inches='tight')
    plt.close(fig='per_million_by_date')

def cases_by_date(statesdata):

    plt.figure(figsize=figsize,num='cases_by_date')

    for i,statename in enumerate(statesdata[plotstates]):

        data = statesdata[statename]

        plt.plot(statesdata[statename],label=statename,marker='o',ms=5,c=clist[i])

    #plt.semilogy()
    plt.legend()

    plt.xlabel(f'Date',fontsize='large')
    plt.ylabel(f'Number of cases',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_by_date_US.png',bbox_inches='tight')
    plt.close(fig='cases_by_date')

    return

def getdata():

    filename = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
    a = pd.read_csv(filename,index_col='UID')
    a.drop(columns=['iso2','iso3','code3','FIPS','Admin2','Country_Region','Lat','Long_','Combined_Key'],inplace=True)

    b = a.groupby('Province_State').sum()
    dt_index = pd.to_datetime(b.columns)
    statesdata = b.T
    statesdata = statesdata.reindex(dt_index)

    statepops = pd.read_csv('nst-est2019-01.csv',index_col='State')

    return statesdata,statepops

def updateplots():


    statesdata,statepops = getdata()

    #calls to plot makers
    cases_by_date(statesdata)
    cases_per_million(statesdata,statepops)
    cases_per_million_by_date(statesdata,statepops)


    return 
    


if __name__ == '__main__':

    updateplots()
