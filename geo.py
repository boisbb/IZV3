#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
import os
# muzeze pridat vlastni knihovny



def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani"""

    df = df[(df['e'].isnull() == False) | (df['d'].isnull() == False)]
    gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df['d'], df['e']), crs="EPSG:5514")

    return gdf

def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """

    gdf = gdf[(gdf['region'] == 'JHM')]

    gdf_1 = gdf[gdf['p5a'] == 1].to_crs("epsg:3857")
    gdf_2 = gdf[gdf['p5a'] == 2].to_crs("epsg:3857")

    fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(15,8), sharex=True, sharey=True)
    gdf_1.plot(ax=ax[0], markersize=0.5, color='red')
    ctx.add_basemap(ax[0], crs=gdf_1.crs.to_string(), source=ctx.providers.Stamen.TonerLite, zoom=10, alpha=0.9)
    ax[0].title.set_text('Nehody v JHM kraji: v obci')

    gdf_2.plot(ax=ax[1], markersize=0.5, color='green')
    ctx.add_basemap(ax[1], crs=gdf_2.crs.to_string(), source=ctx.providers.Stamen.TonerLite, zoom=10, alpha=0.9)
    ax[1].title.set_text('Nehody v JHM kraji: mimo obec')

    for i in range(2):
        ax[i].set_xticks([])
        ax[i].set_yticks([])


    fig.subplots_adjust(wspace=0.01, left=0.01, right=0.99)
    #fig.tight_layout()
    if fig_location is not None:
        if len(fig_location.rsplit('/', 1)) != 1:
            if os.path.isdir(fig_location.rsplit('/', 1)[0]) == False:
                try:
                    os.makedirs(fig_location.rsplit('/', 1)[0])
                except OSError:
                    print ("Creation of the directory %s failed" % fig_location)
        plt.savefig(fig_location)

    # If show_figure is set, show the figure
    if show_figure:
        plt.show()



def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """

    gdf1 = gdf[(gdf['region'] == 'JHM')].copy()
    gdf1 = gdf1.to_crs("epsg:3857")
    cds = np.dstack([gdf1.geometry.x, gdf1.geometry.y]).reshape(-1, 2)

    db = sklearn.cluster.MiniBatchKMeans(n_clusters=20).fit(cds)

    gdf_clus = gdf1.copy()
    gdf_clus["cluster"] = db.labels_
    gdf_clus = gdf_clus.dissolve(by="cluster", aggfunc={"region": "count"}).rename(columns=dict(region="cnt"))

    gdf_cds = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(db.cluster_centers_[:, 0], db.cluster_centers_[:, 1]))
    gdf_clus1 = gdf_clus.merge(gdf_cds, left_on='cluster', right_index=True).set_geometry("geometry_y")

    plt.figure(figsize=(10,7))
    ax = plt.gca()
    gdf1.plot(ax=ax, markersize=0.1, color='grey')
    gdf_clus1.plot(ax=ax, markersize=gdf_clus1['cnt'] / 10, column='cnt', legend=True, alpha=0.6)
    ctx.add_basemap(ax, crs=gdf1.crs.to_string(), source=ctx.providers.Stamen.TonerLite, zoom=10, alpha=0.9)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.title.set_text('Nehody v JHM kraji')

    if fig_location is not None:
        if len(fig_location.rsplit('/', 1)) != 1:
            if os.path.isdir(fig_location.rsplit('/', 1)[0]) == False:
                try:
                    os.makedirs(fig_location.rsplit('/', 1)[0])
                except OSError:
                    print ("Creation of the directory %s failed" % fig_location)
        plt.savefig(fig_location)

    # If show_figure is set, show the figure
    if show_figure:
        plt.show()




if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    #plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
