import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import json

# use correct plt interpreter
matplotlib.use("TkAgg")

# load data
with open("data_eval/arrivals.json") as arr:
    arrivals = np.array(json.load(arr)["bus_arrivals"])

# remove entries without known delay
listDelays = np.array([a["delay"] for a in arrivals])
arrivals = arrivals[np.where(listDelays != None)]

# preprocess data
dtype = [("plannedWhen", datetime), ("delay", float), ("direction", "U25")]
timeFormat = "%Y-%m-%dT%H:%M:%S+02:00"
arrivals = np.array(
    [
        (
            datetime.strptime(arr["plannedWhen"], timeFormat),
            arr["delay"] / 60,
            arr["direction"],
        )
        for arr in arrivals
    ],
    dtype=dtype,
)

# sort by destination
# directionName = "S+U Pankow"
directionName = "S+U Jungfernheide"
arrivals = arrivals[np.where(arrivals["direction"] == directionName)]


# basic evaluation
mean = np.mean(arrivals["delay"])
std_dev = np.std(arrivals["delay"])
three_sigma = 3 * std_dev
print(f"Mean: {mean}")
print(f"Std: {std_dev}")
print(f"3-sigma: {three_sigma}")


# plot histogram
binwidth = 1
binPositions = np.arange(
    min(arrivals["delay"]) - binwidth / 2,
    max(arrivals["delay"]) + 1.5 * binwidth,
    binwidth,
)
plt.figure()
plt.hist(arrivals["delay"], bins=binPositions, rwidth=0.8)
plt.grid(axis="y", alpha=0.5)
plt.xlabel("Delay [min]")
plt.ylabel("Count")
plt.title("Histogram of delays")

# prepare autocorrelation
corrData = np.copy(arrivals)
corrData["delay"] = corrData["delay"] - np.mean(corrData["delay"])  # remove mean
acorr = np.correlate(corrData["delay"], corrData["delay"], mode="full")
acorr = acorr[acorr.size // 2 :]
acorr = acorr / acorr[0]

# plot autocorrelation
lenCorr = 200
plt.figure()
plt.stem(acorr[:lenCorr])
plt.grid(axis="y", alpha=0.5)
plt.xlabel("Lag")
plt.ylabel("Autocorrelation")
plt.title("Autocorrelation of delays")


# prepare plot over time of day
boxData = [[] for i in range(24)]
for dt, delay in zip(arrivals["plannedWhen"], arrivals["delay"]):
    boxData[int(dt.hour)].append(delay)

# plot delay over time of day
plt.figure()
plt.violinplot(boxData)
plt.grid(axis="y", alpha=0.5)
plt.xlabel("Hour")
plt.ylabel("Delay")
plt.title("Boxplot of delays over the day")
plt.show()
