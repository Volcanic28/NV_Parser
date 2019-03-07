import mygeotab
import pprint

# *****************************************************************************
class Location:
    def __init__(self, lon, lat):
        self.x = lon
        self.y = lat
        self.geoLocation = ""


# *****************************************************************************
class Vehicle:
    def __init__(self, api, id):
        data = api.get('Device')
        self.id = id
        self.name = data[0]["name"]
        self.CMVVIN = data[0]["vehicleIdentificationNumber"]
        self.licensePlate = data[0]["licensePlate"]
        trip_data = api.get('Trip')
        dist = 0
        hours = 0
        minutes = 0
        seconds = 0
        for n in trip_data:
            dist += n["distance"]
            seconds += (int(n["workDrivingDuration"][6:7]) + int(n["workStopDuration"][6:7])) % 60
            minutes += (int(n["workDrivingDuration"][3:4]) + int(n["workStopDuration"][3:4])) % 60 + (
                    int(n["workDrivingDuration"][6:7]) + int(n["workStopDuration"][6:7])) / 60
            hours += int(n["workDrivingDuration"][0:1]) + int(n["workStopDuration"][0:1]) + (
                    int(n["workDrivingDuration"][3:4]) + int(n["workStopDuration"][3:4])) / 60
        self.odometer = 0
        self.engineHours = str(round(hours + minutes / 60)) + ':' + str(round(minutes % 60 + seconds / 60)) + ':' + str(
            round(seconds % 60))
        self.vehicleMiles = dist


# *****************************************************************************
class Driver:
    def __init__(self, name, id, lic, state, term):
        self.username = name
        self.id = id
        self.driverLicenseNumber = lic
        self.driverState = state
        self.driverHomeTerminal = term
        self.onDutyTime = 0
        self.offDutyTime = 0
        self.HOSAvailableHours = 0


# *****************************************************************************
class Device:
    def __init__(self,api):
        self.eldIdentifier = api.get('Device')[0]["deviceType"]
        self.eldProvider = "Geotab Inc."
        self.eldRegID = "GEOTAB"

# *****************************************************************************
class User:
    def __init__(self, un, fn, ln):
        self.accountType = ""
        self.username = un
        self.firstName = fn
        self.lastName = ln
        self.Role = ""
        self.timezone = ""
        self.securityClearanceAccess = False
        self.groupAccess = False
        self.exemptDriver = ""


# *****************************************************************************
class Trailer:
    def __init__(self, cmnt, id, name, num):
        self.comment = cmnt
        self.groups = []
        self.id = id
        self.name = name
        self.trailerNum = num


# *****************************************************************************
class DutyStatusLog:
    def __init__(self):
        self.annotations = []
        self.coDrivers = []  # list of User object
        self.dateTime = ""
        self.device = ""  # Device object
        self.driver = ""  # Driver object
        self.dateHT = ""
        self.editDateTime = ""
        self.eventRecord = ""  # event record object
        self.location = ""  # Location object(s)
        self.malfunction = ""  # object?
        self.origin = ""  # DutyStatusOrigin object?
        self.parentID = ""  # id object
        self.sequence = ""
        self.state = ""  # DutyStatusState object?
        self.status = ""  # DutyStatusLogType
        self.verifyDateTime = ""
        self.fileDataCheck = ""
        self.lineDataCheck = ""
        self.multidayBasis = 0
        self.outputFileComment = ""

def testDevice(api):
    dev = Device(api)
    print("Device Object Test:")
    print("eldIdentifier:", dev.eldIdentifier)
    print("eldProvider:", dev.eldProvider)
    print("eldRegID:", dev.eldRegID)
    print("\n")

def testStatuLog(api):
    data = api.get("DutyStatusLog", resultsLimit=10)
    DSLogs = []
    ds_log = DutyStatusLog()
    for i in data:
        if "annotations" in i.keys():
            for n in i["annotations"]:
                ds_log.annotations.append(n["id"])
        ds_log.dateTime = i["dateTime"]
        ds_log.device = i["device"]
        ds_log.driver = i["driver"]
        ds_log.dateHT = ""
        if "editDateTime" in i.keys():
            ds_log.editDateTime = i["editDateTime"]
        ds_log.eventRecord = ""
        ds_log.location = ""
        ds_log.malfunction = i["malfunction"]
        ds_log.origin = i["origin"]
        ds_log.parentID = ""
        ds_log.sequence = i["sequence"]
        ds_log.state = i["state"]
        ds_log.status = i["status"]
        if "verifyDateTime" in i.keys():
            ds_log.verifyDateTime = i["verifyDateTime"]
        ds_log.fileDataCheck = ""
        ds_log.lineDataCheck = ""
        ds_log.multidayBasis = 0
        ds_log.outputFileComment = ""
        DSLogs.append(ds_log)
    print("DutyStatusLog Object Test:")
    for k in DSLogs:
        print("Log datetime:", k.dateTime)
        print("Driver:", k.driver)
    print("\n")


def testDriver(api):
    data = api.get("User")
    Drivers = []
    for i in data:
        if "isDriver" in i.keys() and i["isDriver"]:
            drvr = Driver(i["name"], i["id"], i["licenseNumber"], i["licenseProvince"], i["authorityName"])
            Drivers.append(drvr)
    print("Driver Object Test:")
    for n in Drivers:
        print("Driver:", n.username)
        print("ID:", n.id)
        print("\n")


def testLocation(api):
    locationList = []
    loc_data = api.get('LogRecord', resultsLimit=3)
    for n in loc_data:
        loc = Location(n["longitude"], n["latitude"])
        print("lon = ", loc.x)
        print("lat = ", loc.y)
        geoLoc = api.call("GetAddresses", search={"x": loc.y, "y": loc.x})
        print(geoLoc)
        loc.geoLocation = geoLoc
        locationList.append(loc)
    print("Location Object Test:")
    for n in locationList:
        print("Location:", n.geoLocation)


def testVehicle(api):
    dan_car = Vehicle(api, "b1")
    print("Vehicle Object Test:")
    print("ID:", dan_car.id)
    print("NAME:", dan_car.name)
    print("VIN:", dan_car.CMVVIN)
    print("LICENSE PLATE:", dan_car.licensePlate)
    print("ODOMETER:", dan_car.odometer)
    print("ENGINE HOURS:", dan_car.engineHours)
    print("VEHICLE MILES:", dan_car.vehicleMiles)
    print("\n")


def testTrailer(api):
    data = api.get("Trailer")
    Trailers = []
    for i in data:
        tlr = Trailer(i["comment"], i["id"], i["name"], i["version"])
        for n in i["groups"]:
            tlr.groups.append(n["id"])
        Trailers.append(tlr)
    print("Trailer Object Test:")
    for k in Trailers:
        print("Name:", k.name)
        print("ID:", k.id)
        print("Version:", k.trailerNum)
        print("Comment:", k.comment)
        print("Groups:", k.groups)
        print("\n")


def testUser(api):
    data = api.get("User")
    Users = []

    for i in data:
        user = User(i["name"], i["firstName"], i["lastName"])
        if "isDriver" in i.keys():
            if i["isDriver"]:
                user.accountType = "Driver"
            else:
                user.accountType = "Non-Driver"
        else:
            user.accountType = "Undefined"
        user.Role = i["designation"]
        user.timezone = i["timeZoneId"]
        Users.append(user)
    print("User Object Test:\n")

    for n in Users:
        print("Username:", n.username)
        print("First Name:", n.firstName)
        print("Last Name:", n.lastName)
        print("Timezone:", n.timezone)
        print("Account Type:", n.accountType)
        print("\n")


def testBlock():
    api = mygeotab.API(username='lescanic@gmail.com', password='1qaz!QAZ2wsx@WSX', database='NV_Dan')
    api.authenticate()
    pp = pprint.PrettyPrinter(indent=4)
    xxx=api.get('Device')
    for i in xxx:
        pp.pprint(i);
        print('-'*80)
        print('\n')
    testDevice(api)
    testDriver(api)
    testLocation(api)
    testVehicle(api)
    testTrailer(api)
    testStatuLog(api)


if __name__ == '__main__':
    testBlock()
