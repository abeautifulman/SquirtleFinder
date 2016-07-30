#!/usr/bin/env python2

from os import system, environ
from sys import exit, argv
from json import load
from time import time
from datetime import datetime
from colorama import Fore, Back, Style

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
                     --cookie ': __cfduid=d8a92ebe13d807fa8e08fcf0c3f86ce251469297247; app-session=93dvv7u710pm90nbr9c7tv4rf2; cdmu=1469297256589; _ga=GA1.2.1606395141.1469297258; bknx_fa=1469297258354; bknx_ss=1469297258354; cdmblk=0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0' -o locations/resp.json")
        
        with open('locations/resp.json', 'r') as resp:
            pokemon_locations = load(resp)
        
        self.pokemon = pokemon_locations['pokemon']

    def print_name_and_time(self, pokemon):
        rarity = int(pokemon['pokemonId'])
        color = Fore.YELLOW
        if rarity > 120:
          color = Fore.GREEN
        elif rarity > 80:
          color = Fore.MAGENTA
        elif rarity > 40:
          color = Fore.CYAN

        print color + str(pokemon['pokemonId']) + ':', self.id_lookup[str(pokemon['pokemonId'])], datetime.fromtimestamp(int(str(pokemon['expiration_time']))).strftime('%Y-%m-%d %H:%M:%S') + Style.RESET_ALL

    def print_directions(self, lat, lon, pokemon):
        system('curl https://maps.googleapis.com/maps/api/directions/json\?origin\=' + lat + ',' + lon + '\&destination=' + str(pokemon['latitude']) + ',' + str(pokemon['longitude']) + '\&key\=' + environ['SQUIRTLE_MAPS_KEY'] + ' -o ' + 'locations/' + self.id_lookup[str(pokemon['pokemonId'])] + '_directions.json')  

        with open('locations/' + self.id_lookup[str(pokemon['pokemonId'])] + '_directions.json', 'r') as directions: 
            print load(directions)['routes'][0]['legs'][0]['end_address']

def location():
    system("curl freegeoip.net/json/ -o locations/location.json")
    
    with open("locations/location.json", "r") as loc_file:
        loc = load(loc_file)
        return str(loc['latitude']), str(loc['longitude'])

#class errors():

 # def __init__():

class errors():
  googleAPIERROR = "SquirtleFinder requires the use of environement variables" \
                   " in order to interact with the google maps API."           \
                   "\nSee the README for more information."

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
        finder.request()
        map(finder.print_name_and_time, finder.pokemon)
        search = raw_input("Enter the id's of any pokemon you want search for, separated by spaces: ").split('_')

        print 'getting directions...'
        if environ.get('SQUIRTLE_MAPS_KEY'):
          for query in search:
              for pokemon in finder.pokemon:
                  if str(pokemon['pokemonId']) == str(query): 
                     finder.print_directions(mylat, mylon, finder.pokemon[finder.pokemon.index(pokemon)])
        else:
          print Fore.RED + errors.googleAPIERROR
        return 0
    
    except KeyboardInterrupt: return 1 

if __name__=='__main__': exit(main(argv[1:]))
