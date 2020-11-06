import pandas as pd

# These are the entries in JHU data that do not have matches in census    
#diff = ['West Bank and Gaza',
#         'US',
#         'Taiwan*',
#         'Diamond Princess',
#         'Bahamas',
#         'Holy See',
#         'MS Zaandam',
#         'Gambia']

def fix_census_df(census_df):
    """
    Fix the Census data to match JHU country names, and remove countries 
    that have no Covid data.
    Args:
        census_df (:obj:`pandas.DataFrame`): Census dataframe to fix.
    Returns:
        census_df (:obj:`pandas.DataFrame`): Rectified census dataframe.
    """

    jhu = jhu_countries()
    census_df["West Bank and Gaza"] = census_df["Gaza Strip"] + census_df["West Bank"]
    census_df.rename({"United States": "US", "Bahamas, The": "Bahamas",
                      "Gambia, The": "Gambia"}, axis="columns", inplace=True)
    census_countries = census_df.columns.to_list()
    to_remove = list(set(census_countries) - set(jhu))
    census_df.drop(columns=to_remove, inplace=True)
    return census_df


def fix_jhu_df(jhu_df):
    """
    Fix the JHU data to remove cruise ships and fix country names.
    Args:
        jhu_df (:obj:`pandas.DataFrame`): JHU dataframe to fix.
    Returns:
        jhu_df (:obj:`pandas.DataFrame`): Rectified JHU dataframe.
    """
    
    jhu_df.drop(columns=["Diamond Princess", "MS Zaandam", "Holy See"],
                inplace=True)
    jhu_df.rename({"Taiwan*": "Taiwan"}, axis="columns", inplace=True)
    return jhu_df


def census_continents(filename="Census_data_2020_world_regions.csv"):
    """
    Determine continents for each country that has JHU Covid data.
    Args:
        filename (str): Name of census CSV file.
    Returns:
        by_cont (:obj:`pandas.Series`): Pandas series, each key is the
            continent and the value is a list of countries.
    """

    # Census CSV From here
    # https://www.census.gov/data-tools/demo/idb/region.php?T=6&RT=0&A=separate&Y=2020&C=&R=110,120,130,141,142,143,150,160
    df = pd.read_csv(filename, skiprows=1)
    df.drop(columns=['Year', 'Area (sq. km.)', 'Density (persons per sq. km.)',
                     'Population'], inplace=True)
    df.Country[df["Country"] == "United States"] = "US"
    df.Country[df["Country"] == "Bahamas, The"] = "Bahamas"
    df.Country[df["Country"] == "Gambia, The"] = "Gambia"
    df2 = pd.DataFrame({"Region": ["Asia"], "Country": ["West Bank and Gaza"]})
    df = df.append(df2) 
    jhu = jhu_countries()
    census_countries = df["Country"].to_list()
    to_remove = list(set(census_countries) - set(jhu))
    df = df[df["Country"].apply(lambda x: x not in to_remove)]
    by_cont = df.groupby("Region")["Country"].apply(list) 
    allcountries = pd.Series({"All": jhu})
    by_cont = by_cont.append(allcountries)

    return by_cont    


def jhu_countries():
    """
    List of sanitized countries that JHU tracks (e.g. cruise ships removed).
    Returns:
        countries (list): JHU countries.
    """
    # This is the sanitized list (e.g. Taiwan* is now Taiawn)
    countries = [
 'Afghanistan',
 'Albania',
 'Algeria',
 'Andorra',
 'Angola',
 'Antigua and Barbuda',
 'Argentina',
 'Armenia',
 'Australia',
 'Austria',
 'Azerbaijan',
 'Bahamas',
 'Bahrain',
 'Bangladesh',
 'Barbados',
 'Belarus',
 'Belgium',
 'Belize',
 'Benin',
 'Bhutan',
 'Bolivia',
 'Bosnia and Herzegovina',
 'Botswana',
 'Brazil',
 'Brunei',
 'Bulgaria',
 'Burkina Faso',
 'Burma',
 'Burundi',
 'Cabo Verde',
 'Cambodia',
 'Cameroon',
 'Canada',
 'Central African Republic',
 'Chad',
 'Chile',
 'China',
 'Colombia',
 'Comoros',
 'Congo (Brazzaville)',
 'Congo (Kinshasa)',
 'Costa Rica',
 "Cote d'Ivoire",
 'Croatia',
 'Cuba',
 'Cyprus',
 'Czechia',
 'Denmark',
 'Djibouti',
 'Dominica',
 'Dominican Republic',
 'Ecuador',
 'Egypt',
 'El Salvador',
 'Equatorial Guinea',
 'Eritrea',
 'Estonia',
 'Eswatini',
 'Ethiopia',
 'Fiji',
 'Finland',
 'France',
 'Gabon',
 'Gambia',
 'Georgia',
 'Germany',
 'Ghana',
 'Greece',
 'Grenada',
 'Guatemala',
 'Guinea',
 'Guinea-Bissau',
 'Guyana',
 'Haiti',
 'Honduras',
 'Hungary',
 'Iceland',
 'India',
 'Indonesia',
 'Iran',
 'Iraq',
 'Ireland',
 'Israel',
 'Italy',
 'Jamaica',
 'Japan',
 'Jordan',
 'Kazakhstan',
 'Kenya',
 'Korea, South',
 'Kosovo',
 'Kuwait',
 'Kyrgyzstan',
 'Laos',
 'Latvia',
 'Lebanon',
 'Lesotho',
 'Liberia',
 'Libya',
 'Liechtenstein',
 'Lithuania',
 'Luxembourg',
 'Madagascar',
 'Malawi',
 'Malaysia',
 'Maldives',
 'Mali',
 'Malta',
 'Mauritania',
 'Mauritius',
 'Mexico',
 'Moldova',
 'Monaco',
 'Mongolia',
 'Montenegro',
 'Morocco',
 'Mozambique',
 'Namibia',
 'Nepal',
 'Netherlands',
 'New Zealand',
 'Nicaragua',
 'Niger',
 'Nigeria',
 'North Macedonia',
 'Norway',
 'Oman',
 'Pakistan',
 'Panama',
 'Papua New Guinea',
 'Paraguay',
 'Peru',
 'Philippines',
 'Poland',
 'Portugal',
 'Qatar',
 'Romania',
 'Russia',
 'Rwanda',
 'Saint Kitts and Nevis',
 'Saint Lucia',
 'Saint Vincent and the Grenadines',
 'San Marino',
 'Sao Tome and Principe',
 'Saudi Arabia',
 'Senegal',
 'Serbia',
 'Seychelles',
 'Sierra Leone',
 'Singapore',
 'Slovakia',
 'Slovenia',
 'Somalia',
 'South Africa',
 'South Sudan',
 'Spain',
 'Sri Lanka',
 'Sudan',
 'Suriname',
 'Sweden',
 'Switzerland',
 'Syria',
 'Taiwan',
 'Tajikistan',
 'Tanzania',
 'Thailand',
 'Timor-Leste',
 'Togo',
 'Trinidad and Tobago',
 'Tunisia',
 'Turkey',
 'US',
 'Uganda',
 'Ukraine',
 'United Arab Emirates',
 'United Kingdom',
 'Uruguay',
 'Uzbekistan',
 'Venezuela',
 'Vietnam',
 'West Bank and Gaza',
 'Western Sahara',
 'Yemen',
 'Zambia',
 'Zimbabwe']
    return countries
