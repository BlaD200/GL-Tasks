import json
import math

from os import getenv


def geolocation_calc(request):
    """
    request.args must include origins and destinations coordinates formed
    origins='latitude, longitude', destinations='latitude, longitude'
    If request.args contains 'use_api"=True distance will be calculated via GMaps API.
    The default function is based on math.

    :param request: Flask Request object
    :return: str object formed from JSON
    """
    if list(request.args.keys()):
        parameters = request.args
    else:
        parameters = request.get_json()

    origins = parameters.get('origins')
    destinations = parameters.get('destinations')
    mode = parameters.get('mode', 'driving')
    use_api = False if "False" in parameters.get('use_api', "False") else True

    if all([origins, destinations]):
        if use_api:
            return geolocation_calc_api(origins, destinations, mode)
        else:
            return geolocation_calc_math(origins, destinations)
    else:
        return 'Bad request'


def geolocation_calc_api(origins, destinations, mode):
    """
    Uses google maps api to get distance between two coordinates

    :param origins: str, formatted 'latitude, longitude'
    :param destinations: str, formatted 'latitude, longitude'
    :param mode: go to https://developers.google.com/maps/documentation/distance-matrix/intro#travel_modes for more info
    :return: json, formatted
    {'coordinates': {'origin': 'latitude, longitude', 'destination': 'latitude, longitude'},
     'route_information': {'distance': travel_dist, 'time': travel_dur}}
    """
    response = requests.get(f'https://maps.googleapis.com/maps/api/distancematrix/json?'
                            f'origins={origins}'
                            f'&destinations={destinations}'
                            f'&key={getenv("API_KEY")}'
                            f'&mode={mode}').json()
    travel_dist = response['rows'][0]['elements'][0]['distance']['value']
    travel_dur = response['rows'][0]['elements'][0]['duration']['value']
    return json.dumps({'coordinates': {'origin': origins, 'destination': destinations},
                       'route_information': {'distance': travel_dist, 'time': travel_dur}}), {
               'content-type': 'application/json'}


def geolocation_calc_math(origins, destinations):
    """
    Calculates the distance between two coordinates used math

    :param origins: str, formatted 'latitude, longitude'
    :param destinations: str, formatted 'latitude, longitude'
    :return: json, formatted
    {'coordinates': {'origin': 'latitude, longitude', 'destination': 'latitude, longitude'},
     'route_information': {'distance': travel_dist, 'time': travel_dur}}
    """
    lat_from, long_from = [float(x) for x in origins.split(', ')]
    lat_to, long_to = [float(x) for x in destinations.split(', ')]

    earth_radius = 6371
    f1 = math.radians(lat_from)
    f2 = math.radians(lat_to)
    df = f2 - f1
    dl = math.radians(long_from - long_to)
    a = math.sin(df / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = c * earth_radius
    return json.dumps({'coordinates': {'origin': origins, 'destination': destinations},
                       'route_information': {'distance': distance, 'time': "None"}}), {
               'content-type': 'application/json'}
