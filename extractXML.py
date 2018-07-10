

# Reads the XML file exported by Apple's Health iOS app

import xml.etree.ElementTree

import numpy as np
import pandas as pd
from datetime import datetime
from calendar import monthrange


#xDoc = xml.etree.ElementTree.parse('~/Library/Mobile Documents/com~apple~CloudDocs/HealthData/apple_health_export/Export.xml')
xDoc = xml.etree.ElementTree.parse("Export.xml")

items = list(xDoc.getroot()) # Convert the XML items to a list



# Loop through the XML items, appending samples with the requested identifier
tmp_data = []
item_type_identifier='HKQuantityTypeIdentifierStepCount' # Desired data type
for i,item in enumerate(items):
    if 'type' in item.attrib and item.attrib['type'] == item_type_identifier:
        # Attributes to extract from the current item
        tmp_data.append((item.attrib['creationDate'],
                         item.attrib['startDate'],
                         item.attrib['endDate'],
                         item.attrib['value']))

# Convert to data frame and numpy arrays

data = pd.DataFrame(tmp_data, columns = ['creationDate','startDate','endDate','value'])
all_step_counts = np.array(data.values[:,-1], dtype=int)
all_step_dates  = np.array(data.values[:,0])

data.describe()

steps_per_month, month_labels = [], []
current_month = datetime.strptime(all_step_dates[0][:7], '%Y-%m')
running_step_count = 0

for n, date, step_count in zip(range(len(all_step_dates)), all_step_dates, all_step_counts):
    new_month = datetime.strptime(date[:7], '%Y-%m')

    if new_month > current_month or n == len(all_step_dates) - 1:
        # How many days are in the current month?
        if date == all_step_dates[-1]:
            days_in_month = int(date[8:10])
        else:
            days_in_month = monthrange(current_month.year, current_month.month)[1]

        # Average step count for current month
        steps_per_month.append(running_step_count / days_in_month)
        month_labels.append(current_month.strftime('%b-%Y'))

        # Reset the running step count and current month
        current_month = new_month
        running_step_count = step_count
    else:
        running_step_count += step_count

    # Convert to numpy arrays
steps_per_month = np.array(steps_per_month)
month_labels = np.array(month_labels)

import matplotlib.pyplot as plt

plt.bar(month_labels, steps_per_month)