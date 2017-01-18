from geopy.geocoders import Nominatim
from geopy.distance import vincenty


def get_address_from_coords(lat, lon):
    geolocator = Nominatim()
    location = geolocator.reverse("{0}, {1}".format(lat, lon))

    return location.address


def get_coords_from_address(address):
    geolocator = Nominatim()
    location = geolocator.geocode(address)

    return location.latitude, location.longitude


def calc_distance_from_coords(coords):
    distance = 0
    for waypoint in coords:
        distance += vincenty(waypoint[0], waypoint[1]).miles

    return distance
