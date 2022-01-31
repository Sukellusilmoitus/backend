import shutil
import os
import requests
import geojson
import wget
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from urllib3 import exceptions


def z_to_point(point):
    return Point(point.x, point.y)


def load_and_unpack_zip_file(url, path):
    try:
        shapefiles_zip = wget.download(url, path)
    except exceptions.HTTPError:
        print('connection error when fetching data')
    shutil.unpack_archive(shapefiles_zip, os.path.join(path, 'wrecks_all'))


def filldate(row):
    if row['created_at'] == 'None':
        date = row['luontipvm'].split(' ')[0]
        day_mon_year = date.split('.')
        return f'{day_mon_year[2]}-{day_mon_year[1].zfill(2)}-{day_mon_year[0].zfill(2)}'
    return row['created_at']


def clean_type_string(type_string):
    clean_string = ''
    for type in type_string.split(','):
        if type.strip() != '':
            if clean_string == '':
                clean_string = clean_string + type.strip()
            else:
                clean_string = clean_string + ', ' + type.strip()
    return clean_string


def clean_ancient_data(wrecks_ancient):
    # define which was the orginal coordinate system
    wrecks_ancient = wrecks_ancient.set_crs(epsg=3067)
    # change coordinate system to wgs84 which is usually the deafult in web
    # browsers
    wrecks_ancient = wrecks_ancient.to_crs(epsg=4326)
    # change mjtunnus to id to match the merge
    wrecks_ancient = wrecks_ancient.rename(columns={'mjtunnus': 'id'})
    # mark the ancient and protected wrecks
    wrecks_ancient['is_ancient'] = True

    return wrecks_ancient


def clean_wrecks_all_data(wrecks_all_collection):
    # select only underwater wrecks (marked as 'k' or 'K' in column Vedenalain)
    wrecks_all = wrecks_all_collection.loc[((wrecks_all_collection['Vedenalain'] == 'k') | (
        wrecks_all_collection['Vedenalain'] == 'K'))]

    # change object Z Point to Point
    wrecks_all['geometry'] = wrecks_all['geometry'].apply(z_to_point)

    wrecks_all = wrecks_all.rename(columns={'Mjtunnus': 'id',
                                            'Kunta': 'town',
                                            'Tyyppi': 'type',
                                            'Kohdenimi': 'name',
                                            'Luontipvm': 'created_at',
                                            'Paikannust': 'location_accuracy'})
    wrecks_all_cut = wrecks_all.loc[:, ['id',
                                        'town',
                                        'name',
                                        'created_at',
                                        'type',
                                        'location_accuracy',
                                        'geometry']]

    # set and change coorinate system
    wrecks_all_cut = wrecks_all_cut.set_crs(epsg=3067)
    wrecks_all_cut = wrecks_all_cut.to_crs(epsg=4326)

    return wrecks_all_cut


def clean_union_data(wrecks_union, crs):
    # combine geometries, primary geo from wrecks_all, if missing, taking it
    # from wrecks_ancient
    wrecks_union['geometry'] = wrecks_union.apply(
        lambda row: row['geometry_y'] if (
            row['geometry_x'] is None) else row['geometry_x'], axis=1)
    # fill in url to kyppi info page by wreck_ancient or create url by id
    wrecks_union['url'] = wrecks_union['url'].fillna('None')
    # pylint: disable=line-too-long
    wrecks_union['url'] = wrecks_union.apply(lambda row: f'www.kyppi.fi/to.aspx?id=112.{row["id"]}'
                                             if (row['url'] == 'None') else row['url'], axis=1)
    wrecks_union['url'] = 'https://' + wrecks_union['url']
    # fill in missing creation dates, names, towns, location_accuracys etc
    wrecks_union['created_at'] = wrecks_union['created_at'].fillna('None')
    wrecks_union['created_at'] = wrecks_union.apply(filldate, axis=1)
    wrecks_union['name'] = wrecks_union['name'].fillna('None')
    wrecks_union['name'] = wrecks_union.apply(
        lambda row: f'{row["Kohdenimi"].strip()}' if (
            row['name'] == 'None') else row['name'], axis=1)
    wrecks_union['town'] = wrecks_union['town'].fillna('None')
    wrecks_union['town'] = wrecks_union.apply(lambda row: f'{row["Kunta"].strip()}'
                                              if (row['town'] == 'None')
                                              else row['town'], axis=1)
    wrecks_union['town'] = wrecks_union.apply(lambda row: np.nan
                                              if (row['town'] == 'ei kuntatietoa')
                                              else row['town'], axis=1)
    wrecks_union['is_ancient'] = wrecks_union['is_ancient'].fillna(False)
    wrecks_union['type'] = wrecks_union['type'].fillna(wrecks_union['tyyppi'])
    wrecks_union['type'] = wrecks_union['type'].apply(clean_type_string)
    wrecks_union['location_accuracy'] = wrecks_union['paikannustarkkuus']
    wrecks_union['location_accuracy'] = wrecks_union.apply(
        lambda row: np.nan if (
            (row['location_accuracy'] == 'null') | (
                row['location_accuracy'] == 'Ei tiedossa')) else row['location_accuracy'],
        axis=1)

    # changing DataFrame to GeoDataFrame and dropping unuseful columns
    wrecks_union = gpd.GeoDataFrame(wrecks_union, geometry='geometry', crs=crs)
    wrecks_union = wrecks_union.drop(['geometry_x',
                                      'geometry_y',
                                      'OBJECTID',
                                      'inspireID',
                                      'Kohdenimi',
                                      'Kunta',
                                      'Laji',
                                      'tyyppi',
                                      'alatyyppi',
                                      'ajoitus',
                                      'vedenalainen',
                                      'luontipvm',
                                      'muutospvm',
                                      'paikannustapa',
                                      'paikannustarkkuus',
                                      'selite',
                                      'x',
                                      'y'], axis=1)
    wrecks_union['source'] = 'museovirasto'

    return wrecks_union


def load_and_clean_data(path):
    """ Load wreck data from two sources:
        - protected ancient wrecks (about 733 pcs) from Meritietoportaali
        - all underwater ruins and wrecks or other cultural items (about 2281 pcs)
          from Museovirasto - Kulttuuriympäristön paikkatietoaineistot """

    url_ancient = 'https://kartta.nba.fi/arcgis/services/WFS/MV_HylytMeritietoportaali/' \
        'MapServer/WFSServer?service=WFS&request=GetFeature&' \
        'typeName=WFS_MV_HylytMeritietoportaali:Alusten_hylyt&outputFormat=GEOJSON'

    # fetch data from WFS-server
    try:
        req = requests.get(url_ancient)
    except requests.exceptions.RequestException:
        print('connection error when fetching from kartta.nba.fi')

    # create GeoDataFrame from fetched geojson-data
    wrecks_ancient = gpd.GeoDataFrame.from_features(geojson.loads(req.content))

    # fetch data of all wrecks and ruins as ShapeFile collection to
    # data/wrecks_all folder
    load_and_unpack_zip_file(
        'https://paikkatieto.nba.fi/aineistot/tutkija.zip', path)

    # read in data of all remains (underwater and not underwater)
    wrecks_all_collection = gpd.read_file(os.path.join(
        path,
        'wrecks_all/Muinaisjaannospisteet_t_point.shp'))

    # clean both datas before merging
    wrecks_ancient = clean_ancient_data(wrecks_ancient)
    wrecks_all_cut = clean_wrecks_all_data(wrecks_all_collection)

    # merge ancient wrecks to others by id
    wrecks_union = wrecks_all_cut.merge(wrecks_ancient, on='id', how='outer')

    # clean merged data
    wrecks_union = clean_union_data(wrecks_union, wrecks_ancient.crs)

    return wrecks_union


def delete_temp_folder(path):
    try:
        shutil.rmtree(os.path.join(path, 'wrecks_all'))
        os.remove(os.path.join(path, 'tutkija.zip'))
    except OSError as exp:
        print(
            f'Error when removing temporary files: {exp.filename} - {exp.strerror}.')


def get_wrecks_geojson(path):
    """ Get wreckdata loaded and returned as GeoJSON """
    wrecks_union = load_and_clean_data(path)
    delete_temp_folder(path)
    return wrecks_union.to_json()


def save_wrecks_geojson(path):
    """ Get wreckdata loaded and saved as wreckdata.json to a given path """
    wrecks_union = load_and_clean_data(path)
    wrecks_union.to_file(f'{path}/wreckdata.json', driver='GeoJSON')
    delete_temp_folder(path)
