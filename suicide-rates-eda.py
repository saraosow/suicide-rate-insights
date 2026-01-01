import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import geonamescache

suicides_data = pd.read_csv(r'/Users/saraosowski/Documents/GitHub/suicide-rate-insights/master.csv')
suicides_data.head()



#DATA CLEANING
#remove HDI column due to missing data
data = suicides_data.drop(['HDI for year'], axis = 1)

#remove countries with <10 years of data
by_countryYear = data.groupby('country')['year'].nunique().reset_index()
countries = list(by_countryYear[by_countryYear['year'] >= 10]['country'])
data = data[data['country'].isin(countries)]

#map continent to countries
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
mapping = pd.DataFrame(countries).T.reset_index()[['name','continentcode']]
mapping.rename(columns = {'name':'country'}, inplace = True)
mapping['country'] = mapping['country'].replace({'Macao':'Macau',
                                   'Czechia':'Czech Republic',
                                   'South Korea':'Republic of Korea',
                                   'Russia':'Russian Federation',
                                   'Saint Vincent and the Grenadines':'Saint Vincent and Grenadines'})
data = pd.merge(data,mapping, on='country', how = 'left')
data['continentcode'] = data['continentcode'].replace({'EU':'Europe',
                                   'AS':'Asia',
                                   'NA':'North America',
                                   'SA':'South America',
                                   'AF':'Africa',
                                   'OC':'Oceania'})

#convert columns to catgegory data type
data['continentcode'] = pd.Categorical(data['continentcode'])
data['age'] = pd.Categorical(data['age'])
data['age'] = data['age'].cat.reorder_categories(
    ['5-14 years','15-24 years','25-34 years','35-54 years','55-74 years','75+ years'],
    ordered=True
)
data['generation'] = pd.Categorical(data['generation'])
data['generation'] = data['generation'].cat.reorder_categories(
    ['G.I. Generation','Silent','Boomers','Generation X','Millenials','Generation Z'],
    ordered=True
)
data['country'] = pd.Categorical(data['country'])
data['sex'] = pd.Categorical(data['sex'])
data.rename(columns = {'continentcode':'continent'},inplace = True)

#remove 2016 data; incomplete
data = data[data['year'] != 2016]

#edit gdp to remove commas & change to num
data[' gdp_for_year ($) '] = data[' gdp_for_year ($) '].str.replace(',', '')
data[' gdp_for_year ($) '] = pd.to_numeric(data[' gdp_for_year ($) '])

#save cleaned data as csv
filename = r'/Users/saraosowski/Documents/pythonFinal.csv'
data.to_csv(filename)





#EDA & GRAPHING
data.describe()
data.info()

#evidence men are 3x more likely
data.groupby('sex').suicides_no.sum()
men = data.groupby('sex').suicides_no.sum().male/data.groupby('sex').suicides_no.sum().female 
print(men)

#top 15 total suicides per country
totalSui = data.groupby('country')['suicides_no'].sum()
tot15 = totalSui.nlargest(15)
print(tot15)


class plotting: 
    
    #men v women for a specific country
    def gender(country):
        country = data[data['country'] == country]
        sex_sums = country.groupby('sex')['suicides_no'].sum()
        men = sex_sums['male'] / sex_sums['female']
        print(men)
    
    #top 15 countries with highest suicides/100k pop for an age group
    age_groups = data.age.unique().tolist()
    def top15(age_group):
        print('Top 15 countries with highest suicides/100k pop. for', age_group)
        print(pd.DataFrame(data.groupby(['country','age'])['suicides/100k pop'].mean()).reset_index().\
        sort_values(['age','suicides/100k pop']).groupby('age').get_group(age_group).\
        sort_values('suicides/100k pop', ascending = False).head(15))
            
       
    #plot gender and age for a specific country
    def forCountry(country):
        country = data[data['country']  == country]
        #by age
        plt.figure(figsize = (12,7))
        by_year = country.groupby(['year','age'])[['population','suicides_no']].sum().reset_index()
        by_year['suicide_rate'] = by_year['suicides_no']*100000/by_year['population']
        ax = sns.lineplot(x = 'year', y = 'suicide_rate',hue = 'age',data = by_year,legend = 'full')
        ax.set(ylabel = 'Suicide Rate (# suicides/100k people)', xlabel = 'Year', title = 'Suicide Rates by Age Across a Country (1985-2015)')
        plt.show()
        #by gender
        plt.figure(figsize=(12,7))
        by_year = country.groupby(['year','sex'])[['population','suicides_no']].sum().reset_index()
        by_year['suicide_rate'] = by_year['suicides_no']*100000/by_year['population']
        ax = sns.lineplot(x = 'year', y = 'suicide_rate',hue = 'sex',data = by_year,legend = 'full')
        ax.set(ylabel = 'Suicide Rate (# suicides/100k people)', xlabel = 'Year', title = 'Suicide Rates by Gender Across a Country (1985-2015)')
        plt.show()

plotting.top15('15-24 years')
plotting.forCountry('United States')
plotting.gender('United States')


#total suicides per age group
plt.figure(figsize = (10,5))
age_group_sum = data.groupby('age')['suicides_no'].sum().reset_index()
age = age_group_sum['age']
suicides_gen = age_group_sum['suicides_no']
sns.barplot(x = age,y = suicides_gen)
plt.xlabel('Age')
plt.title('Number of Total Suicides by Age Group (in millions)')


#by age
plt.figure(figsize = (12,7))
by_year = data.groupby(['year','age'])[['population','suicides_no']].sum().reset_index()
by_year['suicide_rate'] = by_year['suicides_no']*100000/by_year['population']
ax = sns.lineplot(x = 'year', y = 'suicide_rate',hue = 'age',data = by_year,legend = 'full')
ax.set(ylabel = 'Suicide Rate (# suicides/100k people)', xlabel = 'Year', title = 'Suicide Rates by Age (1985-2015)')
plt.show()

