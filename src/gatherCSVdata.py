#!/usr/bin/python
"""
DECIDE WHAT THIS PROGRAM DOES:
Does it just gather csv data into 1 JSON file?
Does it filter the JSON file for numbers of interest?
  """
import csv
import os
import sys
import re
import json


def read_list_of_dicts(reader):
    col_names = None
    while True:
        line = reader.next()
        if line:
            # Get Column headings
            col_names = line
            break
    rows = []
    for line in reader:
        row = dict(zip(col_names, line))
        rows.append(row)
    return rows


def process(infile):
    phoneData = []

    reader = csv.reader(infile, delimiter=',', quotechar='"')

    rows = read_list_of_dicts(reader)
    rows = filter(lambda row: row.get('number'), rows)

    #output_json_file = sys.argv[7]
    output_json_file = "phone-output.txt"
    try:
        phoneData = readJsonData(output_json_file)
    except:
        phoneData = []

    for row in rows:
        #print row
        devicename = row.get('number')
        if devicename:
            #if re.search(number, devicename):
            phoneData.append(row)

    print phoneData
    phoneData.sort(key=lambda d: d['number'])
    if phoneData:
        try:
            updateJsonNEW(phoneData, output_json_file)
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
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s To be filed out!\n"
                         % program)
        sys.exit(1)
    input_name = sys.argv[1]

    try:
        with open(input_name, 'rb') as infile:  #format to open csv file
            process(infile)
    except EnvironmentError:
        print('def main(). Error opening file: ' + input_name)
    return

if __name__ == '__main__':
    main()
