# pylint: disable-msg=line-too-long
import shutil
import os
from urllib import error
from urllib3 import exceptions
from fiona.errors import DataIOError
import requests
import geojson
import wget
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

error_msgs = []

def z_to_point(point):
    return Point(point.x, point.y)


def load_and_unpack_zip_file(url, path):
    try:
        shapefiles_zip = wget.download(url, path)
    except (error.URLError, exceptions.HTTPError):
        error_msgs.append(f'connection error when fetching data from {url}')
        return False
    shutil.unpack_archive(shapefiles_zip, os.path.join(path, 'targets_all'))
    return True


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


def clean_ancient_data(targets_ancient):
    # define which was the orginal coordinate system
    targets_ancient = targets_ancient.set_crs(epsg=3067)
    # change coordinate system to wgs84 which is usually the deafult in web
    # browsers
    targets_ancient = targets_ancient.to_crs(epsg=4326)
    # change mjtunnus to id to match the merge
    targets_ancient = targets_ancient.rename(columns={'mjtunnus': 'id'})
    # mark the ancient and protected targets
    targets_ancient['is_ancient'] = True

    return targets_ancient


def clean_targets_all_data(targets_all_collection):
    # select only underwater targets (marked as 'k' or 'K' in column Vedenalain)
    targets_all = targets_all_collection.loc[((targets_all_collection['Vedenalain'] == 'k') | (
        targets_all_collection['Vedenalain'] == 'K'))]

    # change object Z Point to Point
    targets_all['geometry'] = targets_all['geometry'].apply(z_to_point)

    targets_all = targets_all.rename(columns={'Mjtunnus': 'id',
                                            'Kunta': 'town',
                                            'Tyyppi': 'type',
                                            'Kohdenimi': 'name',
                                            'Luontipvm': 'created_at',
                                            'Paikannust': 'location_accuracy'})
    targets_all_cut = targets_all.loc[:, ['id',
                                        'town',
                                        'name',
                                        'created_at',
                                        'type',
                                        'location_accuracy',
                                        'geometry']]

    # set and change coorinate system
    targets_all_cut = targets_all_cut.set_crs(epsg=3067)
    targets_all_cut = targets_all_cut.to_crs(epsg=4326)

    return targets_all_cut


def clean_union_data(targets_union, crs):
    # combine geometries, primary geo from targets_all, if missing, taking it
    # from targets_ancient
    targets_union['geometry'] = targets_union.apply(
        lambda row: row['geometry_y'] if (
            row['geometry_x'] is None) else row['geometry_x'], axis=1)
    # fill in url to kyppi info page by target_ancient or create url by id
    targets_union['url'] = targets_union['url'].fillna('None')
    # pylint: disable=line-too-long
    targets_union['url'] = targets_union.apply(lambda row: f'www.kyppi.fi/to.aspx?id=112.{row["id"]}'
                                             if (row['url'] == 'None') else row['url'], axis=1)
    targets_union['url'] = 'https://' + targets_union['url']
    # fill in missing creation dates, names, towns, location_accuracys etc
    targets_union['created_at'] = targets_union['created_at'].fillna('None')
    targets_union['created_at'] = targets_union.apply(filldate, axis=1)
    targets_union['name'] = targets_union['name'].fillna('None')
    targets_union['name'] = targets_union.apply(
        lambda row: f'{row["Kohdenimi"].strip()}' if (
            row['name'] == 'None') else row['name'], axis=1)
    targets_union['town'] = targets_union['town'].fillna('None')
    targets_union['town'] = targets_union.apply(lambda row: f'{row["Kunta"].strip()}'
                                              if (row['town'] == 'None')
                                              else row['town'], axis=1)
    targets_union['town'] = targets_union.apply(lambda row: np.nan
                                              if (row['town'] == 'ei kuntatietoa')
                                              else row['town'], axis=1)
    targets_union['is_ancient'] = targets_union['is_ancient'].fillna(False)
    targets_union['type'] = targets_union['type'].fillna(targets_union['tyyppi'])
    targets_union['type'] = targets_union['type'].apply(clean_type_string)
    targets_union['location_accuracy'] = targets_union['paikannustarkkuus']
    targets_union['location_accuracy'] = targets_union.apply(
        lambda row: np.nan if (
            (row['location_accuracy'] == 'null') | (
                row['location_accuracy'] == 'Ei tiedossa')) else row['location_accuracy'],
        axis=1)

    # changing DataFrame to GeoDataFrame and dropping unuseful columns
    targets_union = gpd.GeoDataFrame(targets_union, geometry='geometry', crs=crs)
    targets_union = targets_union.drop(['geometry_x',
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
    targets_union['source'] = 'museovirasto'

    return targets_union


def load_and_clean_data(path):
    """ Load target data from two sources:
        - protected ancient targets (about 733 pcs) from Meritietoportaali
        - all underwater ruins and wrecks or other cultural items (about 2281 pcs)
          from Museovirasto - Kulttuuriympäristön paikkatietoaineistot """

    url_ancient = 'https://kartta.nba.fi/arcgis/services/WFS/MV_HylytMeritietoportaali/' \
        'MapServer/WFSServer?service=WFS&request=GetFeature&' \
        'typeName=WFS_MV_HylytMeritietoportaali:Alusten_hylyt&outputFormat=GEOJSON'

    # fetch data from WFS-server
    try:
        req = requests.get(url_ancient)
    except requests.exceptions.RequestException:
        error_msgs.append(f'connection error when fetching from {url_ancient}')
        return

    # create GeoDataFrame from fetched geojson-data
    targets_ancient = gpd.GeoDataFrame.from_features(geojson.loads(req.content))

    # fetch data of all targets and ruins as ShapeFile collection to
    # data/targets_all folder
    if not load_and_unpack_zip_file(
            'https://paikkatieto.nba.fi/aineistot/tutkija.zip', path):
        return

    # read in data of all remains (underwater and not underwater)
    try:
        targets_all_collection = gpd.read_file(os.path.join(
            path,
            'targets_all/Muinaisjaannospisteet_t_point.shp'))
    except DataIOError:
        error_msgs.append(f'not found the extracted file {os.path.join(path,"targets_all/Muinaisjaannospisteet_t_point.shp")}')
        return

    # clean both datas before merging
    targets_ancient = clean_ancient_data(targets_ancient)
    targets_all_cut = clean_targets_all_data(targets_all_collection)

    # merge ancient targets to others by id
    targets_union = targets_all_cut.merge(targets_ancient, on='id', how='outer')

    # clean merged data
    targets_union = clean_union_data(targets_union, targets_ancient.crs)

    return targets_union


def delete_temp_folder(path):
    try:
        shutil.rmtree(os.path.join(path, 'targets_all'))
        os.remove(os.path.join(path, 'tutkija.zip'))
    except OSError as exp:
        print(
            f'Error when removing temporary files: {exp.filename} - {exp.strerror}.')


def get_targets_geojson(path):
    """ Get targetdata loaded and returned as GeoJSON """
    targets_union = load_and_clean_data(path)
    if len(error_msgs) > 0:
        return error_msgs
    delete_temp_folder(path)
    return targets_union.to_json()


def save_targets_geojson(path):
    """ Get targetdata loaded and saved as targetdata.json to a given path """
    targets_union = load_and_clean_data(path)
    if len(error_msgs) > 0:
        delete_temp_folder(path)
        return {'errors': error_msgs}
    targets_union.to_file(f'{path}/targetdata.json', driver='GeoJSON')
    delete_temp_folder(path)
    return {'errors': error_msgs}
