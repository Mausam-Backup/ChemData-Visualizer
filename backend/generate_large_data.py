import csv
import random

filename = "large_equipment_data.csv"
headers = ["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"]

equipment_types = ["Pump", "Valve", "Tank", "Exchanger", "Mixer", "Pipe", "Reactor", "Separator"]

rows = []
for i in range(1, 201):  # 200 rows
    eq_type = random.choice(equipment_types)
    name = f"{eq_type}-{random.randint(100, 999)}"
    
    # Generate realistic data based on type
    if eq_type == "Pump":
        flow = random.uniform(100, 150)
        press = random.uniform(10, 20)
        temp = random.uniform(50, 80)
    elif eq_type == "Valve":
        flow = 0 if random.random() > 0.3 else random.uniform(50, 100) # Open or closed
        press = random.uniform(2, 8)
        temp = random.uniform(20, 40)
    elif eq_type == "Exchanger":
        flow = random.uniform(200, 400)
        press = random.uniform(8, 12)
        temp = random.uniform(80, 120)
    else:
        flow = random.uniform(0, 100)
        press = random.uniform(0, 5)
        temp = random.uniform(20, 60)

    rows.append([name, eq_type, round(flow, 1), round(press, 1), round(temp, 1)])

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Generated {filename} with 200 rows.")
