#!/usr/bin/env python3

import argparse
import webbrowser
import subprocess
import sys

import PIL.Image

def stderr(string):
    subprocess.call(["notify-send", "Error", string])
    sys.stderr.write(f"{string}\n")

def gmaps_url(lat, lon):
    z = 15
    return f"https://maps.google.com/maps?ll={lat},{lon}&q={lat},{lon}&hl=en&t=h&z={z}"

def wiki_url(lat, lon):
    z = 15
    return f"http://wikimapia.org/#lat={lat}&lon={lon}&z={z}"

def yandex_url(lat, lon):
    z = 12
    return f'https://yandex.ru/maps/?ll={lon}%2C{lat}&mode=whatshere&whatshere%5Bpoint%5D={lon}%2C{lat}&whatshere%5Bzoom%5D={z}&z={z}'

def coords(exif):
    latHmspr = None
    latData = None
    lonHmspr = None
    lonData = None

    try:
        gpsData = exif[34853]
        latHmspr = gpsData[1]
        latData = gpsData[2]
        lonHmspr = gpsData[3]
        lonData = gpsData[4]
    except KeyError:
        raise Exception('No GPS data in EXIF')

    latSign = 1 if latHmspr == 'N' else -1
    latDeg = float(latData[0])
    latMin = float(latData[1])
    latSec = float(latData[2])
    lat = latSign * (latDeg + (latMin + latSec / 60) / 60)

    lonSign = 1 if lonHmspr == 'E' else -1
    lonDeg = float(lonData[0])
    lonMin = float(lonData[1])
    lonSec = float(lonData[2])
    lon = lonSign * (lonDeg + (lonMin + lonSec / 60) / 60)

    return lat, lon

def main():
    parser = argparse.ArgumentParser(description='Show image on maps')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--google',    action='store_true',
            help='Google maps')
    group.add_argument('-w', '--wikimapia', action='store_true',
            help='Wikimapia')
    group.add_argument('-y', '--yandex',    action='store_true',
            help='Yandex maps')
    parser.add_argument('filename', help='Image file path')
    args = parser.parse_args()


    filename = args.filename

    img = None
    try:
        img = PIL.Image.open(filename)
    except IOError:
        raise Exception(f"Can't open file {filename}")
        
    exif = img._getexif()
    lat, lon = coords(exif)
    url = gmaps_url(lat, lon) if args.google\
            else wiki_url(lat, lon) if args.wikimapia\
            else yandex_url(lat, lon)
    print(url)
    webbrowser.open(url)
    return 0

if __name__== "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        stderr(str(e))
        sys.exit(1)

