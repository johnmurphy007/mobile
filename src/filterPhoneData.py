#!/usr/bin/python
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
