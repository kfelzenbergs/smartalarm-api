from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from math import radians, cos, sin, asin, sqrt


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
        distance += vincenty(waypoint[0], waypoint[1], miles=False).km

    return distance

def haversine(coords):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """

        km = 0
        for waypoint in coords:
            # convert decimal degrees to radians 
            lon1, lat1, lon2, lat2 = map(radians, [waypoint[0][1], waypoint[0][0], waypoint[1][1], waypoint[1][0]])
            # haversine formula 
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            # Radius of earth in kilometers is 6371
            km += 6371* c
        return km
