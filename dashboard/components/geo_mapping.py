import os
import pandas as pd

os.chdir('/Users/stefanocardinale/Documents/SSI/DATABASES/')

data = pd.read_csv('map_testing_data.csv', sep=";")
data = data.set_index(['Hospital'])

hospitals = data.groupby('Hospital')
cases = [
    {
        "Hospital": "{}".format(k),
        "cases":len(hospitals.groups[k]),
        'lat': data.loc[k]['lat'].values[0],
        'lon': data.loc[k]['lon'].values[0]
    } for k in hospitals.groups
]

#print(new_dict)
test = pd.DataFrame(cases)
print(test['Hospital'])


#test = data.loc['Herlev']
print(data.loc['Herlev']['lat'].values[0])
#print(data.loc[data['Hospital'] == 'Herlev'])
#print(len(hospitals.groups['Herlev']))
