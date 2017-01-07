#!/bin/bash

#python getPhoneRecords.py
python getPhoneRecords.py -configinfo=phone_config.ini phone-output.txt
for filename in $(find ./ -name '*.csv')
do
    echo "Processing: $filename"
    python  gatherCSVdata.py $filename
done
