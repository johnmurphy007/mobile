#!usr/bin/python
import os
import sys
import json
import requests
import csv
import datetime
import time
import argparse
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


def writeDateToConfigFile(comparedate, inifile):
    # Initialise variables/settings
    config = ConfigParser(allow_no_value=True)
    config.sections()

    # Read ini file
    try:
        config.read(inifile)
    except EnvironmentError:
        print('def writeDateToConfigFile(). Issue Reading Config File')
        sys.exit(1)

    # Manipulate ini file:
    sections = config.sections()
    for item in sections:  # e.g. 'credentials'
        options = config.options(item)
        for elem in options:  # e.g username, password
            if str(elem) in "last_update":
                config.set(item, elem, comparedate)
    # Write to ini file
    try:
        with open(inifile, 'w') as outfile:
            config.write(outfile)
    except EnvironmentError:
        print('def writeDateToConfigFile(). Error writing to ini file')
        outfile.close()
    outfile.close()
    return


def getPhoneData(date, config_file):
    username, password = getCredentials(config_file)
    count = 100
    gobackfurther = True
    while gobackfurther:
        url = 'https://my.tescomobile.ie/tmi-selfcare-web/rest/usage/csv/1/' + str(count)

        with requests.Session() as s:
            download = s.get(url, auth=(username, password))

            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                print(row)
                if row[1] != 'date':
                    comparedate = datetime.datetime.strptime(row[1], '%a %b %d %H:%M:%S %Z %Y')
                    comparedate = str(comparedate)
                    print comparedate

                    if comparedate < date:
                        gobackfurther = False

        print "Incrementing count by 100"
        count = count + 100
    # Write date to config file
    update_time = time.strftime("%Y-%m-%d %H:%M:%S")
    update_time = str(update_time)
    writeDateToConfigFile(update_time, config_file)

    try:
        r = requests.get(url, auth=(username, password))
        r_row = r.text.split('\n')
        i = datetime.datetime.now()
        filename = 'downloaded/jm_' + str(i.year) + str(i.month) + str(i.day) + '.csv'
        print filename
        with open(filename, 'wb') as outfile:
            for row in r_row:
                outfile.write(str(row) + "\n")
        outfile.close()

    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)


def getCredentials(config_file):
    # Initialise variables/settings
    config = ConfigParser(allow_no_value=True)
    config.sections()
    username = ""
    password = ""
    # Read ini file
    try:
        config.read(config_file)
    except EnvironmentError:
        print('def getCredentials(). Issue Reading Config File')
        sys.exit(1)

    # Manipulate ini file:
    sections = config.sections()

    for item in sections:  # e.g. 'credentials'
        options = config.options(item)
        for elem in options:  # e.g username, password
            if str(elem) in "username":
                username = str(config.get(item, elem))
                username = username[1:len(username)-1]  # Strip ''
            if str(elem) in "password":
                password = str(config.get(item, elem))
                password = password[1:len(password)-1]  # Strip ''
    return username, password


def getDate(inifile):
    #inifile = "config.ini"  # Location of ini file
    config = ConfigParser(allow_no_value=True)
    config.sections()

    # Read ini file
    try:
        config.read(inifile)
    except EnvironmentError:
        print('def getDate(). Issue Reading Config File')
        sys.exit(1)
    lastdate = str(config.get('credentials', 'last_update'))
    return lastdate


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser(description='Get Phone Records.')
    # Define required Arguments
    parser.add_argument('input_name', action='store', help='REQURIED. Name of Output File?')
    # Define Optional arguments
    parser.add_argument('-configinfo', action='store', help='Name of config file')
    parser.add_argument('-test', action='store_true', help='Test mode - does not fetch data')

    # Example usage based on above:
    # python getPhoneRecords.py -configinfo=phone_config.ini phone-output.txt -test

    # Initialise arguments:
    args = parser.parse_args()
    input_name = args.input_name
    configinfo = args.configinfo
    testMode = args.test

    program = sys.argv[0]

    if not configinfo:
        configinfo = "phone_config.ini"

    try:
        date = getDate(configinfo)
        getPhoneData(date, configinfo)
    except EnvironmentError:
        print('def main(). Error opening file: ' + input_name)
    return


if __name__ == '__main__':
    main()
