#!/usr/bin/env python2

from os import system, environ
from sys import exit, argv
from json import load
from time import time
from datetime import datetime

class SquirtleFinder:

    with open('PokemonDictionary.json', 'r') as pokemon_dict:
        id_lookup = load(pokemon_dict)

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.pokemon = None

    def request(self):
        system("curl --request GET \
                     --url https://pokevision.com/map/data/" + self.lat + "/" + self.lon + " \
                     --header ': authority: pokevision.com' \
                     --header 'cache-control: no-cache' \
                     --header 'cookie: : __cfduid=d8a92ebe13d807fa8e08fcf0c3f86ce251469297247; app-session=93dvv7u710pm90nbr9c7tv4rf2; cdmu=1469297256589; _ga=GA1.2.1606395141.1469297258; bknx_fa=1469297258354; bknx_ss=1469297258354; cdmblk=0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0' \
                     --header 'postman-token: c65c0be4-67d7-a79d-5600-d' \
                     --header 'referer: https://pokevision.com/' \
                     --cookie ': __cfduid=d8a92ebe13d807fa8e08fcf0c3f86ce251469297247; app-session=93dvv7u710pm90nbr9c7tv4rf2; cdmu=1469297256589; _ga=GA1.2.1606395141.1469297258; bknx_fa=1469297258354; bknx_ss=1469297258354; cdmblk=0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0' -o resp.json")
        
        with open('resp.json', 'r') as resp:
            pokemon_locations = load(resp)
        
        return pokemon_locations['pokemon']

    def print_name_and_time(self, pokemon):
        print self.id_lookup[pokemon['pokemonId']], datetime.fromtimestamp(int(str(pokemon['expiration_time']))).strftime('%Y-%m-%d %H:%M:%S')

    def print_directions(lat, lon, pokemon):
        system('curl https://maps.googleapis.com/maps/api/directions/json\?origin\=' + lat + ',' + lon + '\&destination=' + str(pokemon['latitude']) + ',' + str(pokemon['longitude']) + '\&key\=' + environ['SQUIRTLE_MAPS_KEY'] + ' -o ' + self.id_lookup[pokemon['pokemonId']] + '_directions.json')  

        with open(self.id_lookup[pokemon['pokemonId']] + '_directions.json', 'r') as directions: 
            print load(directions)[0][u'routes'][u'legs'][u'end_address']

def location():
    system("curl freegeoip.net/json/ -o location.json")
    
    with open("location.json", "r") as loc_file:
        loc = load(loc_file)
        return str(loc['latitude']), str(loc['longitude'])

def main(args):
    try:
        if raw_input('Should I find your location? (y/n): ') == 'y': mylat, mylon = location()
        else:
            print 'You can also set the SQUIRTLE_MAPS_LAT and SQUIRTLE_MAPS_LON shell variables.' 
            # TODO: what happens when this breaks return 1
            mylat = environ['SQUIRTLE_MAPS_LAT']
            mylon= environ['SQUIRTLE_MAPS_LON']
        
        finder = SquirtleFinder(mylat, mylon) 
        print 'finding some pokemon...'
        t1 = time()
        finder.request()
        t2 = time()
        print str(t2-t1), 'ms for request'
        
        map(finder.print_name_and_time, finder.pokemon)
        
        print 'getting directions...'
        t3 = time()
        print_directions(mylat, mylon, finder.pokemon[0])
        t4 = time()
        print str(t4-t3), 'ms for request'
        
        return 0
    
    except Exception as e: return e

if __name__=='__main__': exit(main(argv[1:]))
