import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys

matplotlib.style.use('dark_background')


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


def state_plot(state,data):

    fig = plt.figure(figsize=(6,4))

    plt.bar(data.index,data[state].diff())
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate(rotation=0,ha='center')

    plt.ylabel('Daily new cases')
    plt.suptitle(state,fontsize='x-large')

    plt.savefig(f'{state}_new_cases.png',bbox_index='tight')


def grid_plot(data):

    fig,axes = plt.subplots(10,5,figsize=(10,12),sharex=True)
    plt.subplots_adjust(wspace=0.3)

    stateslist = ['Alabama','Alaska','Arizona','Arkansas','California',
                  'Colorado','Connecticut','Delaware','Florida',
                  'Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa',
                  'Kansas','Kentucky','Louisiana','Maine','Maryland',
                  'Massachusetts','Michigan','Minnesota','Mississippi',
                  'Missouri','Montana','Nebraska','Nevada','New Hampshire',
                  'New Jersey','New Mexico','New York','North Carolina',
                  'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania',
                  'Rhode Island','South Carolina','South Dakota','Tennessee',
                  'Texas','Utah','Vermont','Virginia','Washington',
                  'West Virginia','Wisconsin','Wyoming']

    dailydata = data.diff()

    for i,ax in enumerate(axes.flatten()):

        ax.bar(dailydata.index,dailydata[stateslist[i]])
        ax.plot(dailydata[stateslist[i]].rolling(5,center=True,min_periods=2).mean(),
                c='gold',lw=0.75)
        ax.set_ylim(bottom=0)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gcf().autofmt_xdate(rotation=70)

        ax.tick_params('both',labelsize='xx-small')
        ax.text(0.025,0.8,stateslist[i],fontsize='small',transform=ax.transAxes)


    plt.suptitle(f'New daily cases\n{dailydata.index[-1]:%B %d, %Y}',fontsize='large')
    plt.savefig(f'states_new_cases.pdf',bbox_inches='tight')


if __name__ == "__main__":

    data,pops = getdata()

    grid_plot(data)

    #state_plot()
