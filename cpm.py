import copy
from functools import reduce


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

            currentActivity["critical"] = True if currentActivity["tf"] == 0 else False

    def activitySort(self, activities):
        activities.sort(key=lambda x: x.get("lf"))
        return activities

    def run(self):
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
            numeric_keys = ["min_duration", "ml_duration", "max_duration", "duration", "es", "ef", "ls", "lf", "tf", "ff"]
            for key in numeric_keys:
                if key in activity and activity[key] != None:
                    activity[key] = round(activity[key], 2)
