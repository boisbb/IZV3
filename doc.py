import pandas as pd
import geopandas
import seaborn as sns
from matplotlib import pyplot as plt
pd.set_option("display.max_rows", None, "display.max_columns", None)

'''
Vyhodnocení nehod pro jednotlivé značky v jednotlivých rocích
'''

def make_df(filename='accidents.pkl.gz'):
    df = pd.read_pickle("accidents.pkl.gz")
    return df

def plot_graph(df):
    #print(df)
    manufacturers = { 2 : 'AUDI', 4 : 'BMW', 15 : 'FERRARI', 17 : 'HYUNDAI',
                      20 : 'JAGUAR', 25 : 'MAZDA' , 26 : 'MERCEDES', 29 : 'NISSAN',
                      32 : 'PEUGEOT', 33 : 'PORSCHE', 38 : 'SEAT', 39 : 'ŠKODA',
                      44 : 'TOYOTA', 47 : 'VOLKSWAGEN'}

    df = df[df['p45a'].isin(manufacturers.keys())]
    df_man = df.copy()
    df_man['manufacturer'] = df_man.apply(lambda row: manufacturers[row['p45a']], axis=1)
    df_man['bin_p12'] = pd.cut(x=df_man['p12'], bins=[0, 200, 300, 400, 500, 600, 615], labels=[ 'nezaviněná řidičem', 'nepříměřená rychlost jízdy', 'nesprávné předjíždění', 'nedání přednosti v jízdě', 'nesprávný způsob jízdy', 'technická závada vozidla'])
    df_man = df_man.groupby(['manufacturer', 'bin_p12'])['manufacturer'].count().reset_index(name='cnt')
    df_sum = df_man.groupby(['manufacturer'])['cnt'].sum().reset_index(name='sum')
    df_man['sum'] = df_man.apply(lambda row: df_sum[df_sum['manufacturer'] == row['manufacturer']].iloc[0]['sum'], axis=1)
    df_man['percentage'] = df_man.apply(lambda row: (row['cnt'] / row['sum']) * 100, axis=1)


    fig, ax = plt.subplots(1, 1, figsize=(15,8))
    fig.patch.set_facecolor("#F0F0F0")
    sns.barplot(x='bin_p12', y='percentage', hue='manufacturer', data=df_man, ax=ax, edgecolor="#F0F0F0", palette='mako')
    ax.set_facecolor("#F0F0F0")
    ax.set_ylabel('Procento nehod')
    ax.set_xlabel('Typ nehody')
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='solid', color='white')
    plt.savefig('fig.png')

    #print(pd.crosstab(df_man.manufacturer, df_man.bin_p12))
    return


if __name__ == '__main__':
    print('main')
    df = make_df()
    plot_graph(df)
