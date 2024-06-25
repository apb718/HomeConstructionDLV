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
try:
    optimum_index = lines.index('OPTIMUM')  # Find the exact line with 'OPTIMUM'
except ValueError:
    optimum_index = None

# Check if we found 'OPTIMUM' and ensure there is a line before it to process
if optimum_index and optimum_index > 0:
    required_line = lines[optimum_index - 1]  # Get the second to last line before 'OPTIMUM'

    # Use regular expression to extract usableSchedule entries
    pattern = r"usableSchedule\(([^)]+)\)"
    matches = re.findall(pattern, required_line)

    # Convert matches into a list of tuples
    input_data = []
    for match in matches:
        # Split each match at commas and strip any whitespace, then convert to tuple
        parts = match.split(',')
        entry = (parts[0].strip(), parts[1].strip(), int(parts[2].strip()), int(parts[3].strip()), int(parts[4].strip()))
        input_data.append(entry)

    # Print the formatted data
    print("input_data = [")
    for data in input_data:
        print(f"    {data},")
    print("]")

else:
    print("No 'OPTIMUM' found or no line before 'OPTIMUM' to process.")

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
        duration = row['DaysOfWork']
        end = start + timedelta(days=duration)
        bar = ax.barh(row['Job'], duration, left=start, height=0.8,
                      color=plt.cm.viridis(row['Workers'] / df['Workers'].max()))

        y_labels.append(f"Order {row['Order']}: {row['Job']} ({row['Workers']} workers)")

        # Annotate each bar with the number of days
        ax.annotate(f"{duration} day(s)", xy=(start + timedelta(days=duration / 2), row['Job']),
                    xytext=(0, 0), textcoords="offset points", va='center', ha='center')

    ax.set_xlabel('Days')
    ax.set_ylabel('Job')
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_title('Job Schedule by Order')
    plt.gca().invert_yaxis()  # Invert y axis to show order 1 on top
    fig.tight_layout()
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.show()



tasks = parse_input(input_data)
create_timeline(tasks)
