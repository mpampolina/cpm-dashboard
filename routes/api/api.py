import sys, json
from cpm import *


def read_input():
    lines = sys.stdin.readlines()
    return json.loads(lines[0])


def getActivitiesAPI(activities):
    cpm = Cpm(activities)
    cpm.run()
    return cpm.activities


def getPCriticalAPI(activities):
    PCritical, activityIDs = getPCritical(activities)
    return {"PCritical": PCritical, "activityIDs": activityIDs}


def main():
    request = sys.argv[1]

    options = {
        "CDF": getCDF,
        "PCritical": getPCriticalAPI,
        "Activities": getActivitiesAPI,
    }

    activities = read_input()
    answer = options[request](activities)
    answer_json = json.dumps(answer, indent=2)
    print(answer_json)


if __name__ == "__main__":
    main()