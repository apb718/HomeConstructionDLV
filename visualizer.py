import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import subprocess
import re

# Assuming your script is named 'run_script.sh' and it's executable
command = [
    '/Users/alecbyrd/Documents/Italy2024/dlv-2.1.2-arm64',
    '/Users/alecbyrd/Documents/Italy2024/cse468/HomeConstructionDLV/construction-edb.dlv',
    '/Users/alecbyrd/Documents/Italy2024/cse468/HomeConstructionDLV/construction-idb.dlv',
    '-n', '0'
]
# Run the script and capture the output
result = subprocess.run(command, stdout=subprocess.PIPE, text=True)

# Get the output as a string
output = result.stdout

# Split the output into lines and reverse it to find 'OPTIMUM' from the bottom
lines = output.splitlines()
optimum_index = -1
for i, line in enumerate(reversed(lines)):
    if "OPTIMUM" in line:
        optimum_index = len(lines) - i - 1
        break

pattern = r"usableSchedule\(([^)]+)\)"
matches = re.findall(pattern, output)

input_data = []

for match in matches:
    # Split each match at commas and strip any whitespace, then convert to tuple
    parts = match.split(',')
    entry = (parts[0].strip(), parts[1].strip(), int(parts[2].strip()), int(parts[3].strip()), int(parts[4].strip()))
    input_data.append(entry)

# Print the formatted data
# print("input_data = [")
# for data in input_data:
#     print(f"    {data},")

# Get the data set just above 'OPTIMUM' if found
if optimum_index > 0:
    required_set = lines[optimum_index - 1]
    print("The required set is:", required_set)
else:
    print("No 'OPTIMUM' found in the output")

# Input data parsing
def parse_input(input_data):
    tasks = []
    for item in input_data:
        labor_type, job, order, days, workers = item
        tasks.append((labor_type, job, order, days, workers))
    return tasks


def create_timeline(tasks):
    # Creating a DataFrame from tasks
    df = pd.DataFrame(tasks, columns=['LaborType', 'Job', 'Order', 'DaysOfWork', 'Workers'])
    df.sort_values('Order', inplace=True)

    # Calculate start dates for each order
    start_date = datetime.now()
    order_dates = {}
    last_end_date = start_date

    # Calculate the earliest start date for each order level
    for order in df['Order'].unique():
        order_dates[order] = last_end_date
        max_duration = df[df['Order'] == order]['DaysOfWork'].max()
        last_end_date += timedelta(days=int(max_duration + 1))

    # Plotting
    fig, ax = plt.subplots(figsize=(14, 8))
    y_labels = []

    for _, row in df.iterrows():
        start = order_dates[row['Order']]
        end = start + timedelta(days=row['DaysOfWork'])
        ax.barh(row['Job'], (end - start).days, left=start, height=0.8,
                label=f"{row['LaborType']} - {row['Workers']} workers",
                color=plt.cm.viridis(row['Workers'] / df['Workers'].max()))
        y_labels.append(f"Order {row['Order']}: {row['Job']} ({row['Workers']} workers)")

    ax.set_xlabel('Time')
    ax.set_ylabel('Job')
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_title('Job Schedule by Order')
    plt.gca().invert_yaxis()  # Invert y axis to show order 1 on top
    fig.tight_layout()
    plt.show()



tasks = parse_input(input_data)
create_timeline(tasks)
