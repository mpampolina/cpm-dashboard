import copy
import numpy as np
from math import ceil
from collections import Counter
from functools import reduce


def sample(activities, iterations=1000):
    if "duration" in activities[0]:
        raise Exception(
            "Cannot sample activities for which a duration has already been defined."
        )

    # setup counter with all critical
    # activity counts set to zero
    cnt = Counter()
    for activity in activities:
        cnt[activity["id"]] = 0

    # run 1000 samples
    sampled_durations = []
    for _ in range(iterations):
        cpm = Cpm(activities)
        cpm.run()
        sampled_durations.append(cpm.earlyFinish)
        for activity in cpm.activities:
            if activity["critical"]:
                cnt[activity["id"]] += 1

    return sampled_durations, cnt


# return the probability as a decimal that a
# given activity is on the critical path
def getPCritical(activities, iterations=1000):
    _, cnt = sample(activities, iterations)

    activityIDs = list(cnt.keys())
    # generate array of probabilities that each
    # activity is critical
    PCritical = [int(value) / iterations for value in cnt.values()]

    return PCritical, activityIDs


def getCDF(activities, iterations=1000, stepped=False):
    sampled_durations, _ = sample(activities, iterations)

    sampled_durations.sort()
    prob = [i * 0.001 for i in range(iterations)]
    dataset = []

    if stepped:
        sampled_durations = [ceil(duration) for duration in sampled_durations]

    # generate CDF plot coordinates, where x is a
    # duration/deadline and y is the probability that that
    # the project will be completed at or before that duration
    for index, duration in enumerate(sampled_durations):
        dataset.append({"x": duration, "y": prob[index]})

    return dataset


class Cpm:
    def __init__(self, activities):
        self.activities = copy.deepcopy(activities)

    def forwardPass(self, root, activities):
        if len(root["predecessor"]) == 0 and "ef" in root:
            return root["ef"]

        if len(root["predecessor"]) == 0:
            root["es"] = 0
            root["ef"] = root["es"] + root["duration"]
            return root["ef"]

        earliestStart = 0

        for id in root["predecessor"]:
            currentStart = self.forwardPass(
                [activity for activity in self.activities if activity["id"] == id][0],
                activities,
            )
            if currentStart > earliestStart:
                earliestStart = currentStart

        root["es"] = earliestStart
        root["ef"] = root["es"] + root["duration"]

        return root["ef"]

    def backwardPass(self, root, activities, duration):
        if "ls" not in root or root["ls"] > duration - root["duration"]:
            root["ls"] = duration - root["duration"]
        if "lf" not in root or root["lf"] > duration:
            root["lf"] = duration
        if len(root["predecessor"]) == 0:
            return

        for id in root["predecessor"]:
            self.backwardPass(
                [activity for activity in self.activities if activity["id"] == id][0],
                activities,
                root["ls"],
            )

        return

    def getRoot(self):
        def getUniquePredecessor(accumulator, activity):
            for predecessor in activity["predecessor"]:
                accumulator.add(predecessor)
            return accumulator

        uniquePredecessor = reduce(getUniquePredecessor, self.activities, set())

        for activity in self.activities:
            if activity["id"] not in uniquePredecessor:
                root = activity

        return root

    def retrieveImmediateSuccessors(self, root, activities, successorID=None):
        if "successor" not in root:
            root["successor"] = []
        if successorID and successorID not in root["successor"]:
            root["successor"].append(successorID)
        if len(root["predecessor"]) == 0:
            return

        for id in root["predecessor"]:
            self.retrieveImmediateSuccessors(
                [activity for activity in self.activities if activity["id"] == id][0],
                self.activities,
                root["id"],
            )

        return

    def calculateFloat(self):
        for currentActivity in self.activities:
            currentActivity["tf"] = currentActivity["lf"] - currentActivity["ef"]
            try:
                aSuccessorID = currentActivity["successor"][0]
                aSuccessor = [
                    activity
                    for activity in self.activities
                    if activity["id"] == aSuccessorID
                ][0]
            except IndexError:
                pass

            if currentActivity == self.root:
                currentActivity["ff"] = self.earlyFinish - currentActivity["ef"]
            else:
                destNodeES = aSuccessor["es"]
                currentActivity["ff"] = destNodeES - currentActivity["ef"]

            # recognize activities with tf values within four decimal places of
            # zero as critical activities to account for floating point errors
            currentActivity["critical"] = (
                True if round(currentActivity["tf"], 4) == 0 else False
            )

    def activitySort(self, activities):
        activities.sort(key=lambda x: x.get("lf"))
        return activities

    def run(self):
        self.simulateDuration()
        self.root = self.getRoot()
        self.earlyFinish = self.forwardPass(self.root, self.activities)
        self.backwardPass(self.root, self.activities, self.earlyFinish)
        self.activitySort(self.activities)
        self.retrieveImmediateSuccessors(self.root, self.activities)
        self.calculateFloat()
        self.roundActivities()
        return self.activities

    def roundActivities(self):
        for activity in self.activities:
            numeric_keys = [
                "min_duration",
                "ml_duration",
                "max_duration",
                "duration",
                "es",
                "ef",
                "ls",
                "lf",
                "tf",
                "ff",
            ]
            for key in numeric_keys:
                if key in activity and activity[key] != None:
                    activity[key] = round(activity[key], 2)

    def simulateDuration(self):
        # assumes that schema is equivalent throughout
        # the data structure
        if "duration" not in self.activities[0]:
            for activity in self.activities:
                if activity["ml_duration"] == None:
                    activity["duration"] = np.random.uniform(
                        activity["min_duration"], activity["max_duration"]
                    )
                else:
                    activity["duration"] = np.random.triangular(
                        activity["min_duration"],
                        activity["ml_duration"],
                        activity["max_duration"],
                    )
