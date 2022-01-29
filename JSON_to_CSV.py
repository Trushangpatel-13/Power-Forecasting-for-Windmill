import json
import csv
from datetime import datetime

# Opening JSON file and loading the data
# into the variable data
with open('data-logger.json') as json_file:
    data = json.load(json_file)

days = list(data.keys())
for key in days:
    date = list(data[key].values())
    hmn_data = datetime.utcfromtimestamp(date[0]).strftime('%d-%m-%Y %H:%M')
    print(hmn_data)
    data[key]['Date'] = hmn_data
print(data)

# now we will open a file for writing
data_file = open('data_file.csv', 'w')

# create the csv writer object
csv_writer = csv.writer(data_file)

# Counter variable used for writing
# headers to the CSV file

count = 0
for key in days:
    if count == 0:
        # Writing headers of CSV file
        header = data[key].keys()
        csv_writer.writerow(header)
        count += 1
    # Writing data of CSV file
    csv_writer.writerow(data[key].values())

data_file.close()


