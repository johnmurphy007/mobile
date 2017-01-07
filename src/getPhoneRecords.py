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


# Step 1: Open 'phone_output.txt' and get newest date in this file:
def readJsonData(inputfile):
    with open(inputfile, 'r') as json_data:
        existingPhoneData = json.load(json_data)
    json_data.close()
    return existingPhoneData


def process(phonejson):
    phoneData = []
    # date = "Fri Aug 19 09:18:25 IST 2016"
    date = datetime.datetime.strptime("Fri Aug 19 09:18:25 IST 2016", '%a %b %d %H:%M:%S %Z %Y')
    date = str(date)
    for row in phonejson:
        #print row
        comparedate = datetime.datetime.strptime(row['date'], '%a %b %d %H:%M:%S %Z %Y')
        #print comparedate
        comparedate = str(comparedate)
        if date <= comparedate:
            phoneData.append(row)
            date = datetime.datetime.strptime(row['date'], '%a %b %d %H:%M:%S %Z %Y')
            date = str(date)
    print "Returning date:" + str(date)
    return date


def writeDateToConfigFile(comparedate, inifile):
    # Initialise variables/settings
    config = ConfigParser(allow_no_value=True)
    config.sections()

    # Read ini file
    try:
        config.read(inifile)
    except EnvironmentError:
        print('def process(). Issue Reading Config File')
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
        print('def process(). Error writing to ini file')
        outfile.close()
    outfile.close()
    return


def getPhoneData(date, config_file):
    #"date": "Fri Aug 19 09:18:25 IST 2016",
    #phonejson.sort(key=lambda d: datetime.datetime.strptime(d['date'], '%a %b %d %H:%M:%S %Z %Y'), reverse=True)
    #phoneData.sort(key=lambda d: d['date'])
    username, password = getCredentials(config_file)
    count = 100
    gobackfurther = True
    #curl -O -u 0868761340:AEJPZF https://my.tescomobile.ie/tmi-selfcare-web/rest/usage/csv/1/10
    #"date": "Tue Aug 09 16:47:20 IST 2016"
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
        filename = './downloaded/jm_' + str(i.year) + str(i.month) + str(i.day) + '.csv'
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
        print('def process(). Issue Reading Config File')
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
        phonejson = readJsonData(input_name) #format to open csv file
        date = process(phonejson)
        getPhoneData(date, configinfo)
    except EnvironmentError:
        print('def main(). Error opening file: ' + input_name)
    return

if __name__ == '__main__':
    main()


"""
DECIDE WHAT THIS PROGRAM DOES:
Does it just gather csv data into 1 JSON file?
Does it filter the JSON file for numbers of interest?
"""

"""
import csv
import os
import sys
import re
import json
import datetime


def process(phonejson):
    phoneData = []
    number = sys.argv[2]
    call = 0
    text = 0

    #output_json_file = sys.argv[7]
    output_json_file = number + ".txt"

    for row in phonejson:
        #print row
        if re.search(number, row['number']):
            #if re.search(number, devicename):
            if row not in phoneData:
                #row.pop('roaming')
                #row.pop('charge')

                phoneData.append(row)

    for item in phoneData:
        item.pop('roaming')
        item.pop('charge')
        if item['service type'] == "CALL":
            call = call + 1
        if item['service type'] == "TEXT":
            text = text + 1

    #"date": "Fri Aug 19 09:18:25 IST 2016",
    phoneData.sort(key=lambda d: datetime.datetime.strptime(d['date'], '%a %b %d %H:%M:%S %Z %Y'))
    #phoneData.sort(key=lambda d: d['date'])
    if phoneData:
        try:
            updateJsonNEW(phoneData, output_json_file)
            print "Calls: " + str(call) + ", Texts: " + str(text)
        except EnvironmentError:
            print('def process(). Error writing file')
    return


def readJsonData(inputfile):
    with open(inputfile, 'r') as json_data:
        existingPhoneData = json.load(json_data)
    json_data.close()
    return existingPhoneData


def updateJsonNEW(phoneData, output_json_file):
    # This method will print al the metadata results to the runbooks json file
    with open(output_json_file, mode='w') as out:
        res = json.dump(
            phoneData,
            out,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ': '))
    out.close()
    return


def main():
    program = sys.argv[0]
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s To be filed out!\n"
                         % program)
        sys.exit(1)
    input_name = sys.argv[1]

    try:
        phonejson = readJsonData(input_name) #format to open csv file
        process(phonejson)
    except EnvironmentError:
        print('def main(). Error opening file: ' + input_name)
    return

if __name__ == '__main__':
    main()


"""
