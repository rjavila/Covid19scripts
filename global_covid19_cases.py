
import pandas as pd
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime

matplotlib.use('agg')
matplotlib.style.use('ggplot')
plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True
figsize=(12,8)

countrieslist = ['China','El Salvador','Iran','Italy','Japan','Korea, South','Spain','Taiwan*','US']
clist = plt.cm.Accent(np.linspace(0,1,len(countrieslist)))

countriespop = {'US':331002651,
                'Italy':60461826,
                'El Salvador':6486205,
                'Korea, South':51269185,
                'Taiwan*':23816775,
                'Iran':83992949,
                'Japan':126476461,
                'Spain':46754778,
                'China':1439323776}


def cases_since_first_case(countriesdata):

    N_min = 100

    plt.figure(figsize=figsize,num='cases_since_first_case')

    for i,country in enumerate(countriesdata.columns):
        
        data = countriesdata.loc[lambda df:df[country]>N_min,country]  

        if data.empty:

            print(f'{country} has not reached {N_min} cases yet.')

        else:

            label = f'{country}:{data.values[-1]}'
            plt.plot(data.values,label=label,marker='o',ms=5,c=clist[i])


    #plt.semilogy()
    plt.legend()

    plt.xlabel(f'Number of days since {N_min} cases',fontsize='large')
    plt.ylabel(f'Number of cases',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_since_first_case.png',bbox_inches='tight')
    plt.close(fig='cases_since_first_case')


def cases_per_million(countriesdata):

    N_min=1
    capita=1000000

    plt.figure(figsize=figsize,num='per_million')

    for i,country in enumerate(countriesdata.columns):

        data = countriesdata.loc[lambda df:capita*df[country]/countriespop[country]>N_min,country] 
        data = capita*data/countriespop[country]

        if data.empty:

            print(f'{country} has not reached {N_min} cases yet.')

        else:

            label = f'{country}: {data.values[-1]:6,.0f}'
            plt.plot(data.values,label=label,marker='o',ms=5,c=clist[i])

    #plt.semilogy()
    plt.legend()

    plt.xlabel(f'Number of days since {N_min} case per {capita:,}',fontsize='large')
    plt.ylabel(f'Number of cases per {capita:,} people',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_per_million.png',bbox_inches='tight')
    plt.close(fig='per_million')

def cases_per_million_by_date(countriesdata):

    N_min=1
    capita=1000000

    plt.figure(figsize=figsize,num='per_million_by_date')

    for i,country in enumerate(countriesdata.columns):

        data = countriesdata.loc[lambda df:capita*df[country]/countriespop[country]>N_min,country] 
        data = capita*data/countriespop[country]

        if data.empty:

            print(f'{country} has not reached {N_min} cases yet.')

        else:

            label = f'{country}: {data.values[-1]:6,.0f}'
            plt.plot(data,label=label,marker='o',ms=5,c=clist[i])

    #plt.semilogy()
    plt.legend()

    plt.xlabel(f'Date',fontsize='large')
    plt.ylabel(f'Number of cases per {capita:,} people',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_per_million_by_date.png',bbox_inches='tight')
    plt.close(fig='per_million_by_date')

def cases_by_date(countriesdata):

    plt.figure(figsize=figsize,num='cases_by_date')

    for i,countryname in enumerate(countriesdata.columns):

        data = countriesdata[countryname]
    
        label = f'{countryname}: {countriesdata[countryname].values[-1]:8,d}'
        plt.plot(countriesdata[countryname],
                 label=label,
                 marker='o',
                 ms=5,
                 c=clist[i]
                 )

    plt.semilogy()
    plt.legend()

    plt.xlabel(f'Date',fontsize='large')
    plt.ylabel(f'Number of cases',fontsize='large')
    plt.suptitle(f'Cases curves',fontsize='xx-large')
    plt.savefig(f'cases_by_date.png',bbox_inches='tight')
    plt.close(fig='cases_by_date')


def updateplots():

    #initialization stuff

    filename = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    a = pd.read_csv(filename)
    b = a.groupby('Country/Region').sum()
    b.drop(columns=['Lat','Long'],inplace=True)

    dt_index = pd.to_datetime(b.columns)
    countriesdata = b.T
    countriesdata = countriesdata.reindex(dt_index)
    countriesdata = countriesdata[countrieslist]

    #calls to plot makers
    cases_by_date(countriesdata)
    #cases_since_first_case(countriesdata) 
    cases_per_million(countriesdata)
    cases_per_million_by_date(countriesdata)




if __name__ == '__main__':

    updateplots()
