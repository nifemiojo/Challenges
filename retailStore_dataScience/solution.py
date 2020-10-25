"""
Please write you name here: Femi
"""
import pandas as pd
import numpy as np
from datetime import time

def formatTimes(x):
    if "PM" in x:
        x = x.replace("PM", "")
        splitTime = x.split("-")
        if "." in x:
            start = int(splitTime[0]) + 12
            end = splitTime[1].replace(splitTime[1][0], f"{int(splitTime[1][0]) + 12}") 
        else:
            start = int(splitTime[0]) + 12
            end = int(splitTime[1]) + 12
    else:
        splitTime = x.split("-")
        if float(splitTime[0]) < 9:
            start = int(splitTime[0]) + 12
            end = int(splitTime[1]) + 12
        else:
            start = splitTime[0].strip()
            end = splitTime[1].strip()
    return [start, end]

def convertToTimeObject(x):
    if type(x) != int and ":" in x:
        splitTime = x.split(":")
        times = time(hour=int(splitTime[0]), minute=int(splitTime[1]))
    elif type(x) != int and "." in x:
        splitTime = x.split(".")
        times = time(hour=int(splitTime[0]), minute=int(splitTime[1]))
    else:
        times = time(hour=int(x))

    return times

def formatTimeString(time):

    newTime = time + ":00"

    return newTime

def process_shifts(path_to_csv):

    #Read CSV File into df
    data = pd.read_csv(path_to_csv)

    #Formulate the dictionary with the times as key and total as value
    startTimes = lambda x: time(hour = int(x.split(":")[0]), minute = int(x.split(":")[1]))

    earliestShiftStart = data.start_time.apply(startTimes).min()

    latestShiftEnd = data.end_time.apply(startTimes).max()

    allWorkingHoursList = list(range(earliestShiftStart.hour,latestShiftEnd.hour,1))

    allWorkingHoursList = list(map(lambda x : f"{x}", allWorkingHoursList))

    labourCostDict = dict.fromkeys(allWorkingHoursList, 0)

    #Handle Break Notes formatting
    breakTimes = list(map(formatTimes, data.break_notes))

    startTimes = []
    endTimes = []

    for breaks in breakTimes:
        startTimes.append(breaks[0])
        endTimes.append(breaks[1])

    #Adding the formatted break times into the original df
    data["break_start"] = startTimes
    data["break_end"] = endTimes

    #Convert times into Time Objects in order to be able to compare using comparison operators
    data["end_time"] = list(map(convertToTimeObject, data.end_time))
    data["start_time"] = list(map(convertToTimeObject, data.start_time))
    data["break_start"] = list(map(convertToTimeObject, data.break_start))
    data["break_end"] = list(map(convertToTimeObject, data.break_end))

    #Taking the hour the shift starts and check if it is a paid hour of work and calculate the total for that hour
    for key, value in labourCostDict.items():
        hourBeginning = time(hour=int(key))

        counter=0
        for index, row in data.iterrows():
            if row['start_time'] <= hourBeginning < row['end_time'] and (row['break_end'] <= hourBeginning or hourBeginning < row['break_start']):
                if hourBeginning.hour == row['end_time'].hour:
                    counter = counter + (row['pay_rate'] * (60 - row['end_time'].minute)/60)
                else:
                    counter = counter + row['pay_rate']
        labourCostDict[key] = counter

    return labourCostDict

def process_sales(path_to_csv):
    #Read CSV File into df
    data = pd.read_csv("C:/Users/Nifemi/Code/vsc/TenzoInt/transactions.csv")

    #Formulate the dictionary with the times as key and total as value
    timeFormat = lambda x: time(hour = int(x.split(":")[0]), minute = int(x.split(":")[1]))

    earliestTransaction = data.time.apply(timeFormat).min()

    latestTransaction = data.time.apply(timeFormat).max()

    allWorkingHoursList = list(range(earliestTransaction.hour - 1,latestTransaction.hour + 2,1))

    allWorkingHoursList = list(map(lambda x : f"{x}", allWorkingHoursList))

    transactionDict = dict.fromkeys(allWorkingHoursList, 0)

    #Convert times into Time Objects in order to be able to compare using comparison operators
    data["time"] = list(map(convertToTimeObject, data.time))

    for key, value in transactionDict.items():
        hourBeginning = time(hour=int(key))

        counter=0
        for index, row in data.iterrows():
            if hourBeginning.hour == row["time"].hour:
                counter = counter + row['amount']
        transactionDict[key] = round(counter, 2)

    return transactionDict

def compute_percentage(shifts, sales):
    data = pd.DataFrame.from_dict(data=shifts, orient='index', columns=["labourCosts"])

    data["transactions"] = sales.values()

    data["labourCostPerSale"] = data.labourCosts/data.transactions

    for index, row in data.iterrows():
        if row["labourCostPerSale"] == np.inf:
            row["labourCostPerSale"] = -row["labourCosts"]
        else:
            row["labourCostPerSale"] = round(row["labourCostPerSale"] * 100, 2)

    percentagesDict = data.labourCostPerSale.to_dict()


    return percentagesDict

def best_and_worst_hour(percentages):

    filteredList = [x for x in percentages.items() if x[1] > 0]

    worstval = min(percentages.items(), key=lambda x: x[1])
    bestval = min(filteredList, key=lambda x: x[1]) 

    bestHour = formatTimeString(bestval[0])
    worstHour = formatTimeString(worstval[0])

    bestAndWorstHour = [bestHour, worstHour]

    return bestAndWorstHour

def main(path_to_shifts, path_to_sales):

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "C:/Users/Nifemi\Code/vsc/TenzoInt/transactions.csv"
    path_to_shifts = "C:/Users/Nifemi/Code/vsc/TenzoInt/work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)


# Please write you name here: Femi Ojo
