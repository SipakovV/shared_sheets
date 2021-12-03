import threading
import csv
import sys


filename = 'data.csv'
data = []
with open(filename, newline='') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
            #print(row)
            data.append(row)
    except csv.Error as e:
        sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

print(data)

