import mygeotab
import pprint
import sys

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
        try:
            self.driver = Driver(api, data["driver"]["id"])
        except:
            print("Driver not found")

# *****************************************************************************
class Location:
    def __init__(self, lon, lat):
        self.x = lon
        self.y = lat
        self.geoLocation = ""

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
class TrailerAttachment:
    def __init__(self, api, id):
        data = api.get("TrailerAttachment", search={'id':id})[0]
        self.activeFrom = data["activeFrom"]
        self.activeTo = data["activeTo"]
        self.device = Device(api, data["device"]["id"])
        self.trailer = Trailer(api, data["trailer"]["id"])
        self.id = data["id"]

# *****************************************************************************
class ShipmentLog:
    def __init__(self, api, id):
        data = api.get("ShipmentLog", search={'id':id})[0]
        self.activeFrom = data["activeFrom"]
        self.activeTo = data["activeTo"]
        self.commodity = data["commodity"]
        self.dateTime = data["dateTime"]
        self.device = Device(api, data["device"]["id"])
        self.documentNumber = data["documentNumber"]
        self.driver = Driver(api, data["driver"]["id"])
        self.shipperName = data["shipperName"]
        self.id = data["id"]

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

# class VehicleLocation:
#     def __init__(self, api, vin):
#         self.CMVVIN = 
#         self.location = 
#         self.distanceLastValid = 
#         self.driverLocation = 
#         self.driectionality = 
#         self.discontinuity = 
#         self.speed = 
#         self.odometer =

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
# class Company:
#     def __init__(self, api, name):
#         self.name = name
#         self.legalName = 
#         self.DBAName = 
#         self.USDOTNumber = 
#         self.authorityAddress = 

# *****************************************************************************
class HomeTerminal:
    def __init__(self, api, id):
        data = api.get("User", search={'id':id})[0]
        self.id = data["companyGroups"][0]["id"]
        self.name = data["companyName"]
        self.address = data["companyAddress"]
        self.companyID = data["companyGroups"][0]["id"]
        tz_data = api.call("GetTimeZones")
        for i in tz_data:
            if i["id"] == data["timeZoneId"]:
                self.timezoneOffset = i["offsetFromUtc"]

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
        self.driverHomeTerminal = HomeTerminal(api, id)
        self.onDutyTime = 0
        self.offDutyTime = 0
        self.HOSAvailableHours = 0

# *****************************************************************************
class DVIRLogDefect:
    def __init__(self, api, log_id, def_id, user_id, dt, id):
        self.DVIRLogId = log_id
        self.defect = def_id
        self.repairUser = User(api, user_id)
        self.repairDateTime = dt
        self.id = id

# *****************************************************************************
class Remark:
    def __init__(self, api, msg, dt, user, type):
        self.remarkMessage = msg
        self.dateTime = dt
        self.user = User(api, user)
        self.type = type

# *****************************************************************************
class DVIRLog:
    def __init__(self, api, id):
        data = api.get("DVIRLog", search={"id":id})[0]
        self.driver = Driver(api, data["driver"]["id"])
        self.id = id
        try:
            self.device = Device(api, data["device"]["id"])
        except:
            self.device = "N/A"
        self.DVIRLogDefect = []
        try:
            for i in data["dVIRDefects"]:
                def_log = DVIRLogDefect(api, i["dVIRLog"]["id"], i["defect"]["id"], data["repairedBy"]["id"], data["repairDate"], i["id"])
                self.DVIRLogDefect.append(def_log)
        except:
            self.DVIRLogDefect = []
        try:
            self.isSafeToOperate = data["isSafeToOperate"]
        except:
            self.isSafeToOperate = "N/A"
        self.remarks = []
        try:
            self.remarks.append(Remark(api, data["certifyRemark"], data["certifyDate"], data["certifiedBy"]["id"], "Certify"))
        except:
            print("No certify remark")
        self.remarks.append(Remark(api, data["driverRemark"], data["dateTime"], data["driver"]["id"], "Driver"))
        try:
            self.remarks.append(Remark(api, data["repairRemark"], data["repairDate"], data["repairedBy"]["id"], "Repair"))
        except:
            print("No repair remark")
        try:
            self.trailer = Trailer(api, data["trailer"]["id"])
        except:
            self.trailer = "None"
        self.dateTime = data["dateTime"]

# *****************************************************************************
class Device:
    def __init__(self, api, id):
        self.id = id
        self.eldIdentifier = api.get('Device', search={'id':id})[0]["deviceType"]
        self.eldProvider = "Geotab Inc."
        self.eldRegID = "GEOTAB"

# *****************************************************************************
class ELDEvent:
    def __init__(self, api, id):
        data = api.get("DutyStatusLog", search={'id':id})[0]
        self.sequence = data["sequence"]
        self.eventRecordStatus = data["eventRecordStatus"]
        self.recordOrigin = data["origin"]
        self.eventType = data["eventType"]
        try:
            self.eventCode = data["eventCode"]
        except:
            self.eventCode = "None"
        self.dateHT = str(data["dateTime"])[:10]
        self.timeHT = str(data["dateTime"])[11:-1]
        self.vehicleMiles = ""
        self.engineHours = ""
        try:
            self.y = data["location"]["location"]["x"]
            self.x = data["location"]["location"]["y"]
        except:
            self.y = "None"
            self.x = "None"
        self.distanceLastValid = ""
        self.malfunctionIndicatorStatus = data["malfunction"]
        self.diagnosticIndicatorStatus = ""
        self.eventComment = ""
        self.driverLocation = ""
        self.orderNum = ""
        self.eventDataCheck = ""


# *****************************************************************************
# TEST FUNCTIONS:
# *****************************************************************************


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
    return DSLogs

def testAnnotationLog(api):
    data = api.get("AnnotationLog", resultsLimit=10)
    ALogs = []
    for i in data:
        # print(i["id"])
        ALogs.append(AnnotationLog(api, i["id"]))

    print("Annotation Log Test:")
    for k in ALogs:
        print("comment: ", k.comment)
        print("dateTime: ", k.dateTime)
        try:
            print("driver: ", k.driver.id)
        except:
            print("driver:","Not Found")
        print("\n")
    return ALogs

def testLocation(api):
    locationList = []
    loc_data = api.get('LogRecord', resultsLimit=3)
    for n in loc_data:
        loc = Location(n["longitude"], n["latitude"])
        # print("lon = ", loc.x)
        # print("lat = ", loc.y)
        coords = {"coordinates":[{"x":loc.x, "y":loc.y}]}
        geoLoc = api.call("GetAddresses", **coords)[0]
        loc.geoLocation = geoLoc["formattedAddress"]
        locationList.append(loc)
    print("Location Object Test:")
    for n in locationList:
        print("Location:", n.geoLocation)
    return locationList

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
    return Trailers

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
    return trlr_atts

def testShipmentLog(api):
    data = api.get("ShipmentLog")
    ship_logs = []
    for i in data:
        ship_log = ShipmentLog(api, i["id"])
        ship_logs.append(ship_log)
        print("Shipment Log Test:")
        print("activeFrom:",ship_log.activeFrom)
        print("activeTo:",ship_log.activeTo)
        print("commodity:",ship_log.commodity)
        print("dateTime:",ship_log.dateTime)
        print("device:",ship_log.device.id)
        print("documentNumber:",ship_log.documentNumber)
        print("driver:",ship_log.driver.id)
        print("shipperName:",ship_log.shipperName)
        print("id:",ship_log.id)
        print("\n")
    return ship_logs

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
    return Users

def testHomeTerminal(api):
    data = api.get("User")[0]
    ht = HomeTerminal(api, data["id"])
    print("HomeTerminal Object Test:\n")
    print("id:",ht.id)
    print("name:",ht.name)
    print("address:",ht.address)
    print("companyID:",ht.companyID)
    print("timezoneOffset:",ht.timezoneOffset)

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
    return Drivers

def testDVIRLog(api):
    data = api.get("DVIRLog")
    dvir_logs = []
    for i in data:
        dvir_log = DVIRLog(api, i["id"])
        dvir_logs.append(dvir_log)
        print("driver:",dvir_log.driver.username)
        print("id:",dvir_log.id)
        try:
            print("device:",dvir_log.device.id)
        except:
            print("device:","None")
        print("Defects:\n")
        for n in dvir_log.DVIRLogDefect:
            print("DVIRLogId:",n.DVIRLogId)
            print("defect:",n.defect)
            print("repairUser:",n.repairUser.username)
            print("repairDateTime:",n.repairDateTime)
            print("id:",n.id)
        print("isSafeToOperate:",dvir_log.isSafeToOperate)
        print("Remarks:\n")
        for k in dvir_log.remarks:
            print("remarkMessage:",k.remarkMessage)
            print("dateTime:",k.dateTime)
            print("user:",k.user.username)
            print("type:",k.type)
        try:
            print("trailer:",dvir_log.trailer.name)
        except:
            print("trailer:","None")
        print("dateTime:",dvir_log.dateTime)

def testDevice(api):
    dev = Device(api, 'b1')
    print("Device Object Test:")
    print("eldIdentifier:", dev.eldIdentifier)
    print("eldProvider:", dev.eldProvider)
    print("eldRegID:", dev.eldRegID)
    print("\n")
    return dev

def testELDEvent(api):
    data = api.get("DutyStatusLog", resultsLimit=10)
    eld_events = []
    print("ELD Event Object Test:\n")
    for i in range(len(data)):
        eld_event = ELDEvent(api, data[i]["id"])
        eld_events.append(eld_event)
        print("sequence:",eld_event.sequence)
        print("eventRecordStatus:",eld_event.eventRecordStatus)
        print("recordOrigin:",eld_event.recordOrigin)
        print("eventType:",eld_event.eventType)
        print("dateHT:",eld_event.dateHT)
        print("timeHT:",eld_event.timeHT)
        print("y:",eld_event.y)
        print("x:",eld_event.x)
        print("malfunctionIndicatorStatus:",eld_event.malfunctionIndicatorStatus)

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
        api = mygeotab.API(username='', password='', database='NV_Dan')
    except MyGeotabException:
        type, value, traceback = sys.exc_info()
        print('Geotab Exception:  %s %s: %s\n' % (type, value.filename, value.strerror))
        print (traceback);
        sys.exit(-1)
    except TimeoutException:
        print ('Geotab Timeout \n')
        sys.exit(-1)

    api.authenticate()

    testDutyStatusLog(api)
    testAnnotationLog(api)
    testLocation(api)
    testTrailer(api)
    testTrailerAttachment(api)
    testShipmentLog(api)
    testVehicle(api)
    testUser(api)
    testHomeTerminal(api)
    testDriver(api)
    testDVIRLog(api)
    testDevice(api)
    testELDEvent(api)
    # fullDataDump(api)

if __name__ == '__main__':
    testBlock()