#!/usr/bin/env python2

from os import system
from sys import exit, argv
from json import load

def request(list_of_pokemon):
    system("curl --request GET \
                   --url https://pokevision.com/map/data/40.01828105867467/-105.28247594833373 \
                   --header ': authority: pokevision.com' \
                   --header 'cache-control: no-cache' \
                   --header 'cookie: : __cfduid=d8a92ebe13d807fa8e08fcf0c3f86ce251469297247; app-session=93dvv7u710pm90nbr9c7tv4rf2; cdmu=1469297256589; _ga=GA1.2.1606395141.1469297258; bknx_fa=1469297258354; bknx_ss=1469297258354; cdmblk=0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0' \
                   --header 'postman-token: c65c0be4-67d7-a79d-5600-1f4be3bdc681' \
                   --header 'referer: https://pokevision.com/' \
                   --cookie ': __cfduid=d8a92ebe13d807fa8e08fcf0c3f86ce251469297247; app-session=93dvv7u710pm90nbr9c7tv4rf2; cdmu=1469297256589; _ga=GA1.2.1606395141.1469297258; bknx_fa=1469297258354; bknx_ss=1469297258354; cdmblk=0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0,0:0:0:0:0:0:0:0:0:0:0:0' -o resp.json")
    with open('resp.json', 'r') as resp:
        pokemon_locations = load(resp)
    print pokemon_locations

def main(args):
    if args: pokemon = args
    else: pokemon = None
    try:
        pokemon = request(pokemon)
        return 0
    except: return 1

if __name__=='__main__': exit(main(argv[1:]))
