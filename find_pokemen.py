#!/usr/bin/env python2

from re import sub
from os import system, environ
from sys import exit, argv
from json import load
from time import time, sleep
from datetime import datetime
from dateutil import relativedelta
from colorama import Fore, Back, Style
from twilio.rest import TwilioRestClient

class PokePanopticon:
    
    def __init__(self, lat, lon):
        self.finder = SquirtleFinder(lat, lon)
        self.lat = lat
        self.lon = lon
        self.search()

    def search(self):
        try:
            while True:
                self.finder.request()
                if environ.get('SQUIRTLE_MAPS_KEY'):
                    for pokemon in self.finder.ranks['god_tier'] + self.finder.ranks['rare']:
                        for data in self.finder.pokemon:
                            if str(data['pokemonId']) == str(pokemon):
                                self.finder.send_txt(self.finder.get_directions(self.lat, self.lon, self.finder.pokemon[self.finder.pokemon.index(data)]))
                else:
                    print Fore.RED + Errors.googleAPIERROR
                    return 1
                sleep(60)

        except KeyboardInterrupt: return 
        

class SquirtleFinder:

    txt_sid = environ['SQUIRTLE_TEXT_SID']
    txt_auth_token = environ['SQUIRTLE_TEXT_TOKEN']
    txt_client = TwilioRestClient(txt_sid, txt_auth_token)

    ranks = {}
    for rank in ['plebian', 'aight', 'rare', 'god_tier']:
        with open('ranks/' +rank + '.csv', 'r') as rank_file:
            ranks[rank] = rank_file.readline().split(',')

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

    def remaining_time(self, pokemon):
        current_time = datetime.fromtimestamp(int(time()))
        expiration_time = datetime.fromtimestamp(int(str(pokemon['expiration_time'])))
        return relativedelta.relativedelta(expiration_time, current_time)

    def print_name_and_time(self, pokemon):
        rarity = str(pokemon['pokemonId'])
        color = Fore.YELLOW
        if rarity in self.ranks['plebian']: color = Fore.GREEN
        elif rarity in self.ranks['aight']: color = Fore.MAGENTA
        elif rarity in self.ranks['rare']:  color = Fore.CYAN
        
        time_remaining = self.remaining_time(pokemon)
        
        print color + str(pokemon['pokemonId']) + ': ' + self.id_lookup[str(pokemon['pokemonId'])], time_remaining.minutes, 'minutes,', time_remaining.seconds, 'seconds' + Style.RESET_ALL
        
        #print color + str(pokemon['pokemonId']) + ': ' + self.id_lookup[str(pokemon['pokemonId'])], datetime.fromtimestamp(int(str(pokemon['expiration_time']))).strftime('%Y-%m-%d %H:%M:%S') + Style.RESET_ALL

    def get_directions(self, lat, lon, pokemon):
        txt = {'pokemon'       : self.id_lookup[str(pokemon['pokemonId'])],
               'time_remaining': self.remaining_time(pokemon)}

        system('curl https://maps.googleapis.com/maps/api/directions/json\?origin\=' + lat + ',' + lon + '\&destination=' + str(pokemon['latitude']) + ',' + str(pokemon['longitude']) + '\&key\=' + environ['SQUIRTLE_MAPS_KEY'] + ' -o ' + 'locations/' + self.id_lookup[str(pokemon['pokemonId'])] + '_directions.json')  

        with open('locations/' + self.id_lookup[str(pokemon['pokemonId'])] + '_directions.json', 'r') as directions: 
            json = load(directions)
            txt['address'] = str(json['routes'][0]['legs'][0]['end_address'])
            txt['instructions'] = [sub('<[^<]+?>', '', str(instruction['html_instructions'])) for instruction in json['routes'][0]['legs'][0]['steps']]

        return txt

    def send_txt(self, txt):
        message = self.txt_client.messages.create(to=environ['MY_PHONE'], from_=environ['SQUIRTLE_PHONE'],
                                                  body=str('There is a ' + txt['pokemon'] + ' nearby!\n' +
                                                       'It will be there for ' + str(txt['time_remaining'].minutes) + ' minutes and ' + str(txt['time_remaining'].seconds) + ' seconds.\n' +
                                                       'It is at ' + txt['address'] )) #+ '\n' +
                                                       #'\n'.join(txt['instructions'])))

def location():
    system("curl freegeoip.net/json/ -o locations/location.json")
    
    with open("locations/location.json", "r") as loc_file:
        loc = load(loc_file)
        return str(loc['latitude']), str(loc['longitude'])

class Errors():
  googleAPIERROR = "SquirtleFinder requires the use of environement variables" \
                   " in order to interact with the google maps API."           \
                   "\nSee the README for more information."

def check_for_text():
    account_sid = environ['SQUIRTLE_TEXT_SID']
    auth_token  = environ['SQUIRTLE_TEXT_TOKEN']
    client = TwilioRestClient(account_sid, auth_token)
    message = client.messages.list()[1]
    print message.body

def main(args):
    if raw_input('Should I find your location? (y/n): ') == 'y': mylat, mylon = location()
    elif (environ.get('SQUIRTLE_MAPS_LAT') and environ.get('SQUIRTLE_MAPS_LON')):
        mylat = environ['SQUIRTLE_MAPS_LAT']
        mylon= environ['SQUIRTLE_MAPS_LON']
    else:
      print Fore.RED + Errors.googleAPIERROR
      return 1
    PokePanopticon(mylat, mylon)
    '''
    try:
        if raw_input('Should I find your location? (y/n): ') == 'y': mylat, mylon = location()
        elif (environ.get('SQUIRTLE_MAPS_LAT') and environ.get('SQUIRTLE_MAPS_LON')):
            mylat = environ['SQUIRTLE_MAPS_LAT']
            mylon= environ['SQUIRTLE_MAPS_LON']
        else:
          print Fore.RED + Errors.googleAPIERROR
          return 1
        
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
                     finder.send_txt(finder.get_directions(mylat, mylon, finder.pokemon[finder.pokemon.index(pokemon)]))
        else:
          print Fore.RED + Errors.googleAPIERROR
          return 1
        
        return 0
    
    except KeyboardInterrupt: return 1 
    '''
    
if __name__=='__main__': exit(main(argv[1:]))
