import mygeotab
import pprint
import sys

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
    def __init__(self, api, id):
        data = api.get("User", search={'id':id})[0]
        self.username = data["name"]
        self.id = data["id"]
        try:
            self.driverLicenseNumber = data["licenseNumber"]
        except:
            self.driverLicenseNumber = "Not On File"
        try:
            self.driverState = data["licenseProvince"]
        except:
            self.driverState = "Not On File"
        self.driverHomeTerminal = data["authorityName"]
        self.onDutyTime = 0
        self.offDutyTime = 0
        self.HOSAvailableHours = 0


# *****************************************************************************
class Device:
    def __init__(self, api, id):
        self.id = id
        self.eldIdentifier = api.get('Device', search={'id':id})[0]["deviceType"]
        self.eldProvider = "Geotab Inc."
        self.eldRegID = "GEOTAB"

# *****************************************************************************
class User:
    def __init__(self, api, id):
        data = api.get("User", search={'id':id})[0]
        if "isDriver" in data: 
            if data["isDriver"]:
                self.accountType = "Driver"
            else:
                self.accountType = "Non-Driver"
        else:
            self.accountType = "Undefined"
        self.username = data["name"]
        self.firstName = data["firstName"]
        self.lastName = data["lastName"]
        self.Role = data["designation"]
        self.timezone = data["timeZoneId"]
        self.securityClearanceAccess = False
        self.groupAccess = False
        self.exemptDriver = ""


# *****************************************************************************
class Trailer:
    def __init__(self, api, id):
        data = api.get("Trailer", search={'id':id})[0]
        self.comment = data["comment"]
        self.groups = []
        for n in data["groups"]:
            self.groups.append(n['id'])
        self.id = id
        self.name = data["name"]
        self.trailerNum = data["version"]


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


# *****************************************************************************
class AnnotationLog:
    def __init__(self, api, id):
        data = api.get("AnnotationLog", search={'id':id})[0]
        self.comment = data["comment"]
        self.dateTime = data["dateTime"]
        self.driver = Driver(api, data["driver"]["id"])


# *****************************************************************************
class TrailerAttachment:
    def __init__(self, api, id):
        data = api.get("TrailerAttachment", search={'id':id})[0]
        self.activeFrom = data["activeFrom"]
        self.activeTo = data["activeTo"]
        self.device = Device(api, data["device"]["id"])
        self.trailer = Trailer(api, data["trailer"]["id"])
        self.id = data["id"]


# *****************************************************************************
# TEST FUNCTIONS:
# *****************************************************************************


def testTrailerAttachment(api):
    data = api.get("TrailerAttachment")
    trlr_atts = []
    for i in data:
        trlr_att = TrailerAttachment(api, i['id'])
        trlr_atts.append(trlr_att)
        print("Trailer Attachment Test:")
        print("activeFrom:",trlr_att.activeFrom)
        print("activeTo:",trlr_att.activeTo)
        print("device:",trlr_att.device.id)
        print("trailer:",trlr_att.trailer.id)
        print("id:",trlr_att.id)
        print("\n")


def testAnnotationLog(api):
    data = api.get("AnnotationLog", resultsLimit=10)
    ALogs = []
    for i in data:
        ALogs.append(AnnotationLog(api, i["id"]))

    print("Annotation Log Test:")
    for k in ALogs:
        print("comment: ", k.comment)
        print("dateTime: ", k.dateTime)
        print("driver: ", k.driver.id)
        print("\n")


def testDevice(api):
    dev = Device(api, 'b1')
    print("Device Object Test:")
    print("eldIdentifier:", dev.eldIdentifier)
    print("eldProvider:", dev.eldProvider)
    print("eldRegID:", dev.eldRegID)
    print("\n")


def testDutyStatusLog(api):
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
            drvr = Driver(api, i["id"])
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
        tlr = Trailer(api, i["id"])
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
        Users.append(User(api, i["id"]))
    
    print("User Object Test:\n")
    for n in Users:
        print("Username:", n.username)
        print("First Name:", n.firstName)
        print("Last Name:", n.lastName)
        print("Timezone:", n.timezone)
        print("Account Type:", n.accountType)
        print("\n")


def fullDataDump(api):
    pp = pprint.PrettyPrinter(indent=4)
    keywords=['Device','User','Trailer','LogRecord','DutyStatusLog']

    for ky in keywords:
        xxx=api.get(ky)
        print('------------------%s-------------------\n'%ky)
        for i in xxx:
            pp.pprint(i);
            print('-'*80)
            print('\n')


def testBlock():
    try:
        api = mygeotab.API(username='lescanic@gmail.com', password='1qaz!QAZ2wsx@WSX', database='NV_Dan')
    except MyGeotabException:
        type, value, traceback = sys.exc_info()
        print('Geotab Exception:  %s %s: %s\n' % (type, value.filename, value.strerror))
        print (traceback);
        sys.exit(-1)
    except TimeoutException:
        print ('Geotab Timeout \n')
        sys.exit(-1)

    api.authenticate()

    testDevice(api)
    testDriver(api)
    testLocation(api)
    testVehicle(api)
    testTrailer(api)
    testDutyStatusLog(api)
    testAnnotationLog(api)
    testTrailerAttachment(api)
    testUser(api)
    # fullDataDump(api)

if __name__ == '__main__':
    testBlock()