import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys

matplotlib.style.use('dark_background')


def getdata():

    filename = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    a = pd.read_csv(filename)

    b = a.groupby('Country/Region').sum()
    b.drop(columns=['Lat','Long'],inplace=True)

    dt_index = pd.to_datetime(b.columns)
    countriesdata = b.T
    countriesdata = countriesdata.reindex(dt_index)

    countriepops = pd.read_csv('nst-est2019-01.csv',index_col='State')

    return countriesdata,countriepops


def country_plot(country,data):

    fig = plt.figure(figsize=(6,3))

    plt.bar(data.index,data[country].diff())
    plt.plot(data[country].diff().rolling(5,center=True,min_periods=2).mean(),
             c='gold',lw=0.75)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate(rotation=0,ha='center')

    plt.ylabel('Daily new cases')
    plt.suptitle(country,fontsize='x-large')

    plt.savefig(f'{country}_new_cases.png',bbox_index='tight')


def grid_plot(data):

    fig,axes = plt.subplots(3,4,figsize=(12,6),sharex=True)
    plt.subplots_adjust(wspace=0.3)

    countrieslist = ['Brazil','Costa Rica','El Salvador','Germany','Iran','Italy','Korea, South','Mexico','Russia','Spain','Sweden','US']

    dailydata = data.diff()

    ax = axes.flatten()

    for i in range(len(countrieslist)):

        #tds_corr = tds_rawmeans.rolling(window=5,min_periods=2,center=True).mean()
        ax[i].bar(dailydata.index,dailydata[countrieslist[i]])
        ax[i].plot(dailydata[countrieslist[i]].rolling(5,center=True,min_periods=2).mean(),
                   c='gold',lw=1.25)
        ax[i].set_ylim(bottom=0)
        
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gcf().autofmt_xdate(rotation=70)

        ax[i].tick_params('both',labelsize='small')
        ax[i].text(0.025,0.85,countrieslist[i],fontsize='medium',transform=ax[i].transAxes)


    plt.suptitle(f'New daily cases\n{dailydata.index[-1]:%B %d, %Y}',fontsize='large')
    plt.savefig(f'global_new_cases.pdf',bbox_inches='tight')


def latin_america(data):

    fig,axes = plt.subplots(4,5,figsize=(15,9))
    plt.subplots_adjust(wspace=0.3)

    countrieslist = ['Mexico','Guatemala','Belize','El Salvador','Honduras','Nicaragua',
                     'Costa Rica','Panama','Colombia','Venezuela','Ecuador','Peru','Brazil',
                     'Bolivia','Paraguay','Uruguay','Argentina','Chile','Cuba',
                     'Dominican Republic']

    countrieslist = sorted(countrieslist)

    dailydata = data.diff()

    ax = axes.flatten()

    for i in range(len(countrieslist)):

        #tds_corr = tds_rawmeans.rolling(window=5,min_periods=2,center=True).mean()
        ax[i].bar(dailydata.index,dailydata[countrieslist[i]])
        ax[i].plot(dailydata[countrieslist[i]].rolling(5,center=True,min_periods=2).mean(),
                   c='gold',lw=1.25)
        ax[i].set_ylim(bottom=0)
        
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gcf().autofmt_xdate(rotation=70)

        ax[i].tick_params('both',labelsize='small')

        ax[i].text(0.025,0.85,countrieslist[i],fontsize='medium',transform=ax[i].transAxes)


    plt.suptitle(f'New daily cases\n{dailydata.index[-1]:%B %d, %Y}',fontsize='large')
    plt.savefig(f'latin_america.pdf',bbox_inches='tight')


def eu_vs_usa_plot(data):

    fig,ax = plt.subplots(2,1,figsize=(6,6),sharex=True)
    #plt.subplots_adjust(wspa)

    dailydata = data.diff()


    eulist = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czechia','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden']

    eudf = dailydata[eulist].sum(axis=1)


    ax[0].bar(dailydata.index,dailydata['US'])
    ax[0].plot(dailydata['US'].rolling(5,center=True,min_periods=2).mean(),
               c='gold',lw=1.5)
    ax[0].set_ylim(bottom=0)
    ax[0].text(0.05,0.8,'United States',fontsize='large',transform=ax[0].transAxes)

    ax[1].bar(dailydata.index,eudf)
    ax[1].plot(dailydata.index,eudf.rolling(5,center=True,min_periods=2).mean(),
               c='gold',lw=1.5)
    ax[1].set_ylim(bottom=0)
    ax[1].text(0.05,0.8,'European Union',fontsize='large',transform=ax[1].transAxes)
    
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate(rotation=70)

    ax[1].tick_params('both',labelsize='small')

    plt.suptitle(f'New daily cases\n{dailydata.index[-1]:%B %d, %Y}',fontsize='large')
    plt.savefig(f'EU_vs_USA.pdf',bbox_inches='tight')


if __name__ == "__main__":

    data,pops = getdata()
    eu_vs_usa_plot(data)
    grid_plot(data)
    latin_america(data)

    #state_plot()
