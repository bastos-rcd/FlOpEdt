# Imports des modules
from functools import reduce  # Pour le pgcd d'une liste
from math import gcd  # PGCD

from django.db import transaction
from requests import Session  # API HP
from requests.auth import HTTPBasicAuth  # API HP
from tqdm import tqdm  # Affichage de la barre sympa
from zeep import Client  # API HP
from zeep.transports import Transport  # API HP

from base.models import Course, CourseType, GenericGroup, Module, RoomType, Week
from people.models import Tutor


# Functions used to check book content (dictionary extracted from hyperplanning)
def inputBool(message=""):
    """
    Input: The message asking a yes/no question.
    Return: A boolean: True if input yes, False if input no.
    Loop while the answer is not valid.
    """
    while True:
        ans = input("(Boolean) - (y/n) - %s" % message).lower()
        if ans in ["y", "n", "yes", "no", "o", "non", "oui", "true", "false", "t", "f"]:
            if ans in ["y", "yes", "o", "oui", "t", "true"]:
                return True
            else:
                return False
        else:
            print("( Error ) - Only answer with 'y' or 'n'")


def inputInt(message=""):
    """
    Input: The message asking for an integer.
    Return: An integer. If the input is a float, it's converted into an integer.
    Loop while the answer is not valid.
    """
    ans = ""
    while type(ans) != int:
        ans = input("(Integer) - %s" % message)
        try:
            ans = int(float(ans))
        except:
            print("( Error ) - Only answer with a integer (float will be floored)")
    return ans


def inputTime(message=""):
    """
    Input: The message asking for time in HH:mm format.
    Return: An integer representing minutes elapsed from midnight to the specific hour in a day.
    Loop while the answer is not valid.
    """
    ans = ""
    while type(ans) != int:
        inp = input("( Time  ) - (HH:mm) - %s" % message)
        try:
            heure, minute = inp.split(":")
            heure = int(heure)
            minute = int(minute)
            if 0 <= heure <= 24 and 0 <= minute <= 59:
                ans = heure * 60 + minute
            else:
                print(
                    "( Error ) - Hours or minutes out of bounds ( 0<=hours<=24 and 0<=minutes<=59 )"
                )
        except:
            print("( Error ) - Incorrect format (use HH:mm format)")
    return ans


def cleanDictionary(dictionary):
    """
    Input: A dictionary
    Return: The same dictionary without the keys leading to nothing
    """
    keysToDelete = []
    for i in dictionary:
        if dictionary[i] == None:
            keysToDelete.append(i)
    for i in keysToDelete:
        dictionary.pop(i)


def shortenString(string, spliter="-", part=0):
    """
    Input: A string to shorten, the character(s) that split the said string ( "-" by default ), and the index of the substring to choose ( the first one by default )
    Return: The choosed substring
    Used to: Shorten modules name
    """
    if spliter in string:
        newstrings = string.split(spliter)
        if len(newstrings) - 1 < part:
            return newstrings[-1]
        return newstrings[part]
    return string


def getpSvcWDureeToMinutesInDay(pSvcWDuree):
    """
    Input: Time in hyperplanning format
    Return: A List. List[0] is a int representing the time in a day and List[1] is a string representing the day:  ['m','tu','w','th','f','sa','su']
    The hyperplanning API time format define hour in a day in minutes since Monday midnight. Per example, Tuesday 12:00 is defined as 32h*60 min/h = 1920 min
    """
    timeInMinutes = pSvcWDuree * 24 * 60
    listDays = ["m", "tu", "w", "th", "f", "sa", "su"]
    return (round(timeInMinutes % (60 * 24)), listDays[round(pSvcWDuree)])


def PGCDListe(intList):
    """
    Input: A list containing integers
    Return: The greatest common divisor of the list
    Used to: Find the maximal time interval usable in a time table
    """
    return reduce(gcd, intList)


def createPeriods():
    """
    Input: Nothing
    Return: A dictionary with the name of periods (usually semestrer) as a key and that lead to its start week number and finish week number
    Used to: Define semester
    """
    periodDictionary = dict()
    numberOfPeriods = inputInt("Number of periods? (semesters, trimesters, ...): ")
    for i in range(numberOfPeriods):
        periodName = input(
            "(String ) - Period "
            + str(1 + i)
            + "/"
            + str(numberOfPeriods)
            + ". Name this period: "
        )
        periodStartWeek = inputInt(
            "First week number of the period " + periodName + ": "
        )
        periodFinishWeek = inputInt(
            "Last week number of the period " + periodName + ": "
        )
        periodDictionary[periodName] = (periodStartWeek, periodFinishWeek)
    print("")
    return periodDictionary


def createSchoolDays():
    """
    Input: Nothing
    Return: A list containing day where courses can be placed
    """
    weekDays = ["m", "tu", "w", "th", "f", "sa", "su"]
    daysName = [
        "monday",
        "tuesdays",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    ans = []
    for i in range(len(weekDays)):
        possibleDay = inputBool("Can courses be placed on " + daysName[i] + "? : ")
        if possibleDay:
            ans.append(weekDays[i])
    return ans


def createLunchBreak():
    """
    Input: Nothing
    Return: Integers representing the start time and finish time of the lunch-break
    """
    print(
        "( Hint  ) - Set the beginning of the lunch-break and the end of the lunch-break at 1 a.m if you don't want a lunch break"
    )
    startTime = inputTime("At what time should the lunch break start? : ")
    finishTime = inputTime("At what time should the lunch break end? : ")
    while startTime > finishTime:
        print("( Error ) - The lunch-break ends before starting")
        startTime = inputTime("At what time should the lunch break start? : ")
        finishTime = inputTime("At what time should the lunch break end? : ")
    return startTime, finishTime


def switchStructuralToTransversal(dico):
    """
    Input: The hyperplanning dictionary
    Return: Nothing but alter the hyperplanning dictionary with some structural groups switched to transversal groups according to user choices
    """
    keys_to_remove = []
    for i in dico["groups"].keys():
        if inputBool(
            "Is the group "
            + i[1]
            + " from the prom "
            + i[0]
            + " is a transversal group? : "
        ):
            keys_to_remove.append(i)
            dico["transversal_groups"][i] = {
                "transversal_to": None,
                "parallel_to": None,
            }
    for i in keys_to_remove:
        dico["groups"].pop(i)


def getValidCourseKeys(IHpSvcWCours, alertList, breakLevel=-1):
    """
    Input: The Hyperplanning-API thing that deals with courses, and an Integer that define the max number of courses to take into account
    Return: Valid courses keys usable for other applications
    Note: Can be optimized unfortunatly some API functions don't work properly, or I just use them very badly
    """
    listCoursesKeys = IHpSvcWCours.service.TousLesCours()
    if len(listCoursesKeys) > breakLevel:
        listCoursesKeys = listCoursesKeys[0:breakLevel]

    validCourseKeys = []
    numberOfDiscardedCoursesKeys = 0
    nodcDueToNotPlaced = 0
    nodcDueToNotChildrenOrSimple = 0

    for i in tqdm(
        listCoursesKeys,
        "(Extract) - Crs keys : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        if IHpSvcWCours.service.CoursEstUnCoursFils(
            i
        ) or IHpSvcWCours.service.CoursEstUnCoursSimple(i):
            if not IHpSvcWCours.service.EstCoursNonPlace(i):
                validCourseKeys.append(i)
            else:
                numberOfDiscardedCoursesKeys += 1
                nodcDueToNotPlaced += 1
        else:
            numberOfDiscardedCoursesKeys += 1
            nodcDueToNotChildrenOrSimple += 1

    if numberOfDiscardedCoursesKeys != 0:
        alertList.append(
            "( Alert ) - %s courses have been discarded" % numberOfDiscardedCoursesKeys
        )
        alertList.append(
            "( Alert ) - %s of them is because they were not placed and %s of them were not children or simple courses"
            % (nodcDueToNotPlaced, nodcDueToNotChildrenOrSimple)
        )

    return validCourseKeys


def extractRooms(IHpSvcWSalles):
    """
    Input: The Hyperplanning-API thing that deals with rooms
    Return: Rooms defined in the Hyperplanning database
    """
    listRoomKeys = IHpSvcWSalles.service.ToutesLesSalles()
    listRoomNames = []
    for i in tqdm(
        listRoomKeys,
        "(Extract) - Rooms    : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        listRoomNames.append(IHpSvcWSalles.service.NomSalle(i))
    return set(listRoomNames)


def extractPeople(IHpSvcWEnseignants, alertList):
    """
    Input: The Hyperplanning-API thing that deals with teachers and the alertList
    Return: A dictionary containing teachers: First_name, last_name, email, status and employer. Can be access using the teacherID defined in the hyperplanning database
    Note: If the teacher don't have an email adress, it will be fake@flopedt.org
    """
    listTeachersKeys = IHpSvcWEnseignants.service.TousLesEnseignants()
    teacherDictionary = {}
    for i in tqdm(
        listTeachersKeys,
        "(Extract) - Teachers : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        teacherSubDictionary = {}
        teacherSubDictionary[
            "first_name"
        ] = IHpSvcWEnseignants.service.PrenomEnseignant(i)
        teacherSubDictionary["last_name"] = IHpSvcWEnseignants.service.NomEnseignant(i)
        email = IHpSvcWEnseignants.service.EMailEnseignant(i)
        if email is None:
            teacherSubDictionary["email"] = "fake@flopedt.org"
            if (
                teacherSubDictionary["first_name"] != None
                and teacherSubDictionary["last_name"] != None
            ):
                alertList.append(
                    "( Alert ) - Teacher "
                    + teacherSubDictionary["first_name"]
                    + " "
                    + teacherSubDictionary["last_name"]
                    + " does not have a valid email!"
                )
        else:
            teacherSubDictionary["email"] = email
        teacherSubDictionary["status"] = "temp"  # Does not affect FlOp anyhow
        teacherSubDictionary["employer"] = "temp"  # Same
        teacherID = IHpSvcWEnseignants.service.IdentifiantCASEnseignant(i)
        if teacherID != None:
            teacherDictionary[teacherID] = teacherSubDictionary
        else:
            if (
                teacherSubDictionary["first_name"] != None
                and teacherSubDictionary["last_name"] != None
            ):
                alertList.append(
                    "( Alert ) - Teacher "
                    + teacherSubDictionary["first_name"]
                    + " "
                    + teacherSubDictionary["last_name"]
                    + " does not have a valid ID!"
                )
    return teacherDictionary


def extractModules(
    IHpSvcWMatieres,
    IHpSvcWCours,
    IHpSvcWTDOption,
    IHpSvcWPromotions,
    validCourseKeys,
    firstPeriod,
):
    """
    Input: The Hyperplanning-API things that deals with modules, courses, groups and proms, valid course keys (from getValidCoursesKeys function) and the period
    Return: A dictionary containing modules: the name of the module, the short name of the module, the course promotion and the owner
    Note: code PPN is useless
    """
    listCoursesKeys = validCourseKeys
    tempDictNameOfModules = {}  # Cle -> Nom
    moduleDictionary = {}

    for i in tqdm(
        listCoursesKeys,
        "(Extract) - Modules  : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        moduleKey = IHpSvcWCours.service.MatiereCours(i)
        if moduleKey not in tempDictNameOfModules.keys():
            moduleName = IHpSvcWMatieres.service.LibelleMatiere(moduleKey)
            tempDictNameOfModules[moduleKey] = moduleName
        else:
            moduleName = tempDictNameOfModules[moduleKey]

        courseTDOpt = IHpSvcWCours.service.TDOptionsDuCours(i)
        courseProm = IHpSvcWCours.service.PromotionsDuCours(i)
        courseOwner = None  # IHpSvcWMatieres.service.ProprietaireMatiere(IHpSvcWCours.service.MatiereCours(i)) <- renvoi nom+prenom au lieu de l'identifiant cas

        for j in courseTDOpt:
            promOfTDOpt = IHpSvcWTDOption.service.PromotionTDOption(j)
            if promOfTDOpt not in courseProm:
                courseProm.append(promOfTDOpt)
        for j in courseProm:
            promName = IHpSvcWPromotions.service.NomPromotion(j)
            if moduleName in moduleDictionary.keys():
                if moduleDictionary[moduleName] == None:
                    advancedModuleName = moduleName + "_" + promName
                    moduleDictionary[advancedModuleName] = {
                        "short": shortenString(moduleName),
                        "PPN": "Code PPN",
                        "name": moduleName,
                        "promotion": promName,
                        "period": firstPeriod,
                        "responsable": courseOwner,
                    }
                elif moduleDictionary[moduleName]["promotion"] != promName:
                    advancedModuleName = moduleName + "_" + promName
                    moduleDictionary[advancedModuleName] = {
                        "short": shortenString(moduleName),
                        "PPN": "Code PPN",
                        "name": moduleName,
                        "promotion": promName,
                        "period": firstPeriod,
                        "responsable": courseOwner,
                    }
                    advancedOldModuleName = (
                        moduleName + "_" + moduleDictionary[moduleName]["promotion"]
                    )
                    moduleDictionary[advancedOldModuleName] = moduleDictionary.pop(
                        moduleName
                    )
                    moduleDictionary[moduleName] = None
            else:
                moduleDictionary[moduleName] = {
                    "short": shortenString(moduleName),
                    "PPN": "Code PPN",
                    "name": moduleName,
                    "promotion": promName,
                    "period": firstPeriod,
                    "responsable": courseOwner,
                }
    cleanDictionary(moduleDictionary)
    return moduleDictionary


def extractCoursesSettings(IHpSvcWCours, validCourseKeys):
    """
    Input: The Hyperplanning-API thing that deals with courses and valid course keys (from getValidCoursesKeys function)
    Return: A dictionary containing courses settings: Course type, course length, course start time and group types. The key of a course_type is its type + "_" + duration in minutes
    """
    coursesSettingsDictionary = {}
    for i in tqdm(
        validCourseKeys,
        "(Extract) - Crs sett : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):  # for i in validCourseKeys:
        courseType = IHpSvcWCours.service.TypeCours(i)
        courseLength = getpSvcWDureeToMinutesInDay(IHpSvcWCours.service.DureeCours(i))[
            0
        ]
        courseStartTime, courseDay = getpSvcWDureeToMinutesInDay(
            IHpSvcWCours.service.PlaceCours(i)
        )
        courseKey = courseType + "_" + str(courseLength) + "m"
        if courseKey not in coursesSettingsDictionary.keys():
            coursesSettingsDictionary[courseKey] = {
                "duration": courseLength,
                "group_types": set(),
                "start_times": set(),
            }
            coursesSettingsDictionary[courseKey]["group_types"].add(courseType)
        if courseStartTime not in coursesSettingsDictionary[courseKey]["start_times"]:
            coursesSettingsDictionary[courseKey]["start_times"].add(courseStartTime)
    return coursesSettingsDictionary


def extractSettings(IHpSvcWCours, validCourseKeys):
    """
    Input: The Hyperplanning-API thing that deals with courses and valid course keys (from getValidCoursesKeys function)
    Return: A dictionary containing the generation setting: lunch break start & finish time, day start & finish time,  days where courses can be placed and the time resolution to place courses
    """
    settingsDictionary = {
        "lunch_break_start_time": 12 * 60,
        "lunch_break_finish_time": 12 * 60,
    }
    startTimes = set()
    finishTimes = set()
    days = set()
    for i in tqdm(
        validCourseKeys,
        "(Extract) - Settings : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        courseLength = getpSvcWDureeToMinutesInDay(IHpSvcWCours.service.DureeCours(i))[
            0
        ]
        courseStartTime, courseDay = getpSvcWDureeToMinutesInDay(
            IHpSvcWCours.service.PlaceCours(i)
        )
        courseFinishTime = courseStartTime + courseLength
        startTimes.add(courseStartTime)
        finishTimes.add(courseFinishTime)
        days.add(courseDay)

    settingsDictionary["day_start_time"] = min(startTimes)
    settingsDictionary["day_finish_time"] = max(finishTimes)
    settingsDictionary["days"] = list(days)
    settingsDictionary["default_preference_duration"] = PGCDListe(list(startTimes))
    return settingsDictionary


def extractPromotions(IHpSvcWPromotions):
    """
    Input: The Hyperplanning-API thing that deals with proms
    Return: A dictionary containing every proms: key is promName and return promName
    """
    promKeys = IHpSvcWPromotions.service.ToutesLesPromotions()
    promotionDictionary = {}
    for i in tqdm(
        promKeys,
        "(Extract) - Proms    : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        promName = IHpSvcWPromotions.service.NomPromotion(i)
        promotionDictionary[promName] = promName
    return promotionDictionary


def extractGroupTypes(coursesSettingsDict):
    """
    Input: The previously extracted coursesSettings dictionary
    Return: A set containing every group types
    """
    groupTypesSet = set()
    for i in tqdm(
        coursesSettingsDict,
        "(Extract) - Gr.type  : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        for j in coursesSettingsDict[i]["group_types"]:
            groupTypesSet.add(j)
    return groupTypesSet


def extractGroups(IHpSvcWPromotions, IHpSvcWTDOptions):
    """
    Input: API things that deals with proms and groups (TDOptions)
    Return: A dictionary containing every groups: key is a tuple (promName, groupName) and return its group type and the parent group
    Note: This function is not optimal
    """
    groupDictionary = dict()
    tdOptionsKeys = IHpSvcWTDOptions.service.TousLesTDOptions()
    promKeys = IHpSvcWPromotions.service.ToutesLesPromotions()

    # Groups 1 are proms groups, representing the root of the tree
    for i in tqdm(
        promKeys,
        "(Extract) - Groups1  : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        promName = IHpSvcWPromotions.service.NomPromotion(i)
        groupID = (promName, promName)
        groupDictionary[groupID] = {"group_type": None, "parent": set()}

    # Groups 2 are the childrens of the first groups
    for i in tqdm(
        tdOptionsKeys,
        "(Extract) - Groups2  : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        tdOptionName = IHpSvcWTDOptions.service.NomTDOption(i)
        belongTo = set()
        belongTo.add(
            IHpSvcWPromotions.service.NomPromotion(
                IHpSvcWTDOptions.service.PromotionTDOption(i)
            )
        )
        groupID = (
            IHpSvcWPromotions.service.NomPromotion(
                IHpSvcWTDOptions.service.PromotionTDOption(i)
            ),
            tdOptionName,
        )

        groupDictionary[groupID] = {"group_type": None, "parent": belongTo}

    return groupDictionary


# Primary functions
def verifyAndEdit(dico):
    print("\n")

    if inputBool(
        "Do you wish to look through some extracted information and modify them if needed? : "
    ):
        if inputBool(
            "Courses will start as soon as: %sH%s. Edit? : "
            % (
                dico["settings"]["day_start_time"] // 60,
                dico["settings"]["day_start_time"] % 60,
            )
        ):
            dico["settings"]["day_start_time"] = inputTime(
                "Courses should not start before what time? : "
            )

        if inputBool(
            "Courses will end no latter than: %sH%s. Edit? : "
            % (
                dico["settings"]["day_finish_time"] // 60,
                dico["settings"]["day_finish_time"] % 60,
            )
        ):
            dico["settings"]["day_finish_time"] = inputTime(
                "What time should the courses finish time not exceed? : "
            )

        print("\n")
        if inputBool("There is currently no defined lunch break. Define one? : "):
            lunch_break_start_time, lunch_break_finish_time = createLunchBreak()
            dico["settings"]["lunch_break_start_time"] = lunch_break_start_time
            dico["settings"]["lunch_break_finish_time"] = lunch_break_finish_time

        print("\n")
        if inputBool(
            "The current course placement granularity is: %s minutes. Edit? : "
            % dico["settings"]["default_preference_duration"]
        ):
            dico["settings"]["default_preference_duration"] = inputInt(
                "What course placement granularity do you want? (in minutes) : "
            )

        dayMessage = "The current school days are :"
        dayDictionary = {
            "m": "Monday",
            "tu": "Tuesday",
            "w": "Wednesday",
            "th": "Thursday",
            "f": "Friday",
            "sa": "Saturday",
            "su": "Sunday",
        }
        for i in dayDictionary:
            if i in dico["settings"]["days"]:
                dayMessage = dayMessage + " " + dayDictionary[i]
        dayMessage = dayMessage + ". Edit? : "

        if inputBool(dayMessage):
            dico["settings"]["days"] = createSchoolDays()

        print("\n")
        if inputBool(
            "There is currently no defined transversal groups. Do you want to turn some structural groups into transversal groups? : "
        ):
            switchStructuralToTransversal(dico)

    return dico


# Main function
def create_db_dictionary_from_hyperplanning(username, password, lPrefixeWsdl):
    # Connection
    session = Session()
    session.auth = HTTPBasicAuth(username, password)

    # Initializing dictionary
    rooms = set()
    room_groups = dict()
    room_categories = dict()
    people = dict()
    modules = dict()
    courses = dict()
    settings = dict()
    promotions = dict()
    group_types = set()
    groups = dict()

    # Initializing services
    adminService = Client(
        lPrefixeWsdl + "IHpSvcWAdmin", transport=Transport(session=session)
    )
    roomService = Client(
        lPrefixeWsdl + "IHpSvcWSalles", transport=Transport(session=session)
    )
    peopleService = Client(
        lPrefixeWsdl + "IHpSvcWEnseignants", transport=Transport(session=session)
    )
    moduleService = Client(
        lPrefixeWsdl + "IHpSvcWMatieres", transport=Transport(session=session)
    )
    courseService = Client(
        lPrefixeWsdl + "IHpSvcWCours", transport=Transport(session=session)
    )
    tdOptionService = Client(
        lPrefixeWsdl + "IHpSvcWTDOptions", transport=Transport(session=session)
    )
    promService = Client(
        lPrefixeWsdl + "IHpSvcWPromotions", transport=Transport(session=session)
    )

    # Authentication
    try:
        print("Connected to: " + adminService.service.Version() + "\n")
    except:
        print(
            "Connection failed: either your username/password combination is wrong or your connection is down. Maybe both"
        )
        return None

    # Creating periods (user prompt)
    periods = createPeriods()

    # Core
    alertList = []

    MAX_NUMBER_OF_COURSES = inputInt(
        "How many courses do you want to look through? Enter -1 to look through every courses (may take a lot of time!) : "
    )
    validCoursesKeys = getValidCourseKeys(
        courseService, alertList, MAX_NUMBER_OF_COURSES
    )

    rooms = extractRooms(roomService)
    room_groups = {}
    room_categories = {"all": rooms.copy()}

    people = extractPeople(peopleService, alertList)

    modules = extractModules(
        moduleService,
        courseService,
        tdOptionService,
        promService,
        validCoursesKeys,
        list(periods.keys())[0],
    )  # Pas beau

    courses = extractCoursesSettings(courseService, validCoursesKeys)

    settings = extractSettings(courseService, validCoursesKeys)
    settings["periods"] = periods

    promotions = extractPromotions(promService)

    group_types = extractGroupTypes(courses)

    groups = extractGroups(promService, tdOptionService)

    book = {
        "rooms": rooms,
        "room_groups": room_groups,
        "room_categories": room_categories,
        "people": people,
        "modules": modules,
        "courses": courses,
        "settings": settings,
        "promotions": promotions,
        "group_types": group_types,
        "groups": groups,
        "transversal_groups": {},
    }

    for i in alertList:
        print(i)

    book = verifyAndEdit(book)

    return book


def create_course_list_from_hp(
    username, password, lPrefixeWsdl, remove_courses_with_no_group=True
):
    # Connection
    session = Session()
    session.auth = HTTPBasicAuth(username, password)

    adminService = Client(
        lPrefixeWsdl + "IHpSvcWAdmin", transport=Transport(session=session)
    )
    courseService = Client(
        lPrefixeWsdl + "IHpSvcWCours", transport=Transport(session=session)
    )
    peopleService = Client(
        lPrefixeWsdl + "IHpSvcWEnseignants", transport=Transport(session=session)
    )
    promService = Client(
        lPrefixeWsdl + "IHpSvcWPromotions", transport=Transport(session=session)
    )
    tdOptService = Client(
        lPrefixeWsdl + "IHpSvcWTDOptions", transport=Transport(session=session)
    )
    moduleService = Client(
        lPrefixeWsdl + "IHpSvcWMatieres", transport=Transport(session=session)
    )

    # Authentication
    try:
        print("Connected to: " + adminService.service.Version() + "\n")
    except:
        print(
            "Connection failed: either your username/password combination is wrong or your connection is down. Maybe both"
        )
        return None

    # Core
    MAX_NUMBER_OF_COURSES = inputInt(
        "How many courses do you want to look through? Enter -1 to look through every courses (may take a lot of time!) : "
    )

    validCoursesKeys = getValidCourseKeys(courseService, MAX_NUMBER_OF_COURSES)

    coursesList = []

    for i in tqdm(
        validCourseKeys,
        "Courses - Extracting : ",
        bar_format="{l_bar}{bar:15}{r_bar}{bar:-10b}",
    ):
        # courseType
        courseType = (
            courseService.service.TypeCours(i)
            + "_"
            + str(round(courseService.service.DureeCours(i) * 24 * 60))
            + "m"
        )

        # roomType (not supported)
        roomType = "all"

        # courseNumber (not supported aswell)
        courseNumber = 0

        # tutor and supp_tutor
        listOfTutors = courseService.service.EnseignantsDuCours(i)
        courseTutor = None
        courseSuppTutor = set()
        if len(listOfTutors) == 1:
            courseTutor = peopleService.service.IdentifiantCASEnseignant(
                listOfTutors[0]
            )
        elif len(listOfTutors) > 1:
            for j in listOfTutors:
                courseSuppTutor.add(peopleService.service.IdentifiantCASEnseignant(j))

        # groups
        listOfCourseProms = courseService.service.PromotionsDuCours(i)
        listOfCourseTDOpt = courseService.service.TDOptionsDuCours(i)
        courseGroups = set()
        for j in listOfCourseProms:
            courseGroups.add(promService.service.NomPromotion(j))
        for j in listOfCourseTDOpt:
            courseGroups.add(tdOptService.service.NomTDOption(j))

        # module
        courseModule = moduleService.service.LibelleMatiere(
            courseService.service.MatiereCours(i)
        )

        # week and year
        courseWeek = None
        hpWeek = courseService.service.DomaineCours(i)
        if len(hpWeek) > 0:
            hpWeek = hpWeek[0]
            courseWeek = courseService.service.SemaineEnSemaineCalendaire(hpWeek)
            courseYear = str(courseService.service.SemaineEnDate(hpWeek))[0:4]

        course = {
            "type": courseType,
            "room_type": roomType,
            "no": courseNumber,
            "tutor": courseTutor,
            "supp_tutor": courseSuppTutor,
            "groups": courseGroups,
            "transversal_groups": {},
            "module": courseModule,
            "week": courseWeek,
            "year": courseYear,
        }

        if courseWeek != None:
            coursesList.append(course)

    if remove_courses_with_no_group:
        coursesList = remove_courses_without_group(coursesList)

    return coursesList


def remove_courses_without_group(listOfCourses):
    numberOfCourses = len(listOfCourses)
    for i in range(numberOfCourses - 1, -1, -1):
        if listOfCourses[i]["groups"] == set():
            listOfCourses.pop(i)
    return listOfCourses


@transaction.atomic
def extract_courses_from_book(courses_book, department):
    for c in courses_book:
        if not c["groups"]:
            continue
        groups = GenericGroup.objects.filter(
            name__in=c["groups"], train_prog__department=department
        )
        ct = CourseType.objects.get(name=c["type"], department=department)
        rt = RoomType.objects.get(name=c["room_type"], department=department)
        if c["tutor"]:
            tut = Tutor.objects.get(username=c["tutor"])
        else:
            tut = None
        supp_tuts = Tutor.objects.filter(username__in=c["supp_tutor"])
        mod = Module.objects.get(name=c["module"], train_prog=groups[0].train_prog)
        week = Week.objects.get(nb=c["week"], year=c["year"])
        new_course = Course(type=ct, room_type=rt, tutor=tut, module=mod, week=week)
        new_course.save()
        for g in groups:
            new_course.groups.add(g)
        for t in supp_tuts:
            new_course.supp_tutor.add(t)
    print("Course extraction done")
