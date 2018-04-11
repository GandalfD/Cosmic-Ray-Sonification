import matplotlib.pyplot as plt
import numpy as np
import time

with open("raw_data/raw/0201.out", "r") as raw_file:
    lines = raw_file.readlines()

event_list = [0]
time_list = [0]

first_date_check = True
last_event_time = 0
event_counter = 0  # this counts multiple # of events in a second

for line in lines:
    if first_date_check:
        print("Getting first date")
        first_date = line[line.find(" ", 50) + 1: line.find(" ", 53)]
        print(first_date)
        first_date_check = False

    trigger_code = bin(int(line[line.find(" ", 7) + 1: line.find(" ", 9)], 16))

    # check if its a new event
    if len(trigger_code) >= 7 and trigger_code[7]:
        event_time = time.strptime(
            line[line.find(" ", 40) + 1: line.find(".", 43)], "%H%M%S")

        if event_time != last_event_time:
            time_list.append((event_time.tm_hour * 3600) +
                             (event_time.tm_min * 60) + event_time.tm_sec)

            event_list.append(event_list[-1] + event_counter)
            event_counter = 0
        else:  # another event within same timeframe
            event_counter += 1

        last_event_time = event_time


def create_plot():
    plt.plot(time_list, event_list)
    plt.xlabel("Time Past " +
               time.strftime("%m/%d/%Y", time.strptime(first_date, "%d%m%y")) +
               " Seconds")

    plt.ylabel("Raw Number of Events")

    plt.show()


create_plot()
