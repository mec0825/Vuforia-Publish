import requests
import re
import json
import time
import datetime
import os



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Classes
# ///////////////////////////////////////////////////////////////////////////////////////////////////

class User:
    def __init__(self, userName, userID, token):
        self.userName = userName
        self.userID = userID
        self.token = token

    def __repr__(self):
        return '\
        \n---------------------------------------------\
        \nUser Name: %s\
        \nUser ID: %s\
        \nUser Token: %s\
        \n---------------------------------------------' %(
            self.userName,
            self.userID,
            self.token
        )


class License:
    def __init__(self, appName, productName, licenseID):
        self.appName = appName
        self.productName = productName
        self.licenseID = licenseID

    def __repr__(self):
        return '\
        \n---------------------------------------------\
        \nApp Name: %s\
        \nProduct Name: %s\
        \nLicense ID: %s\
        \n---------------------------------------------' %(
            self.appName,
            self.productName,
            self.licenseID
        )

class Database:
    def __init__(self, databaseName, databaseID, appName, targetCount):
        self.databaseName = databaseName
        self.databaseID = databaseID
        self.appName = appName 
        self.targetCount = targetCount

    def __repr__(self):
        return '\
        \n---------------------------------------------\
        \nDatabase Name: %s\
        \nDatabase ID: %s\
        \nApp Name: %s\
        \nTarget Count:%s\
        \n---------------------------------------------' %(
            self.databaseName,
            self.databaseID,
            self.appName,
            self.targetCount
        )


class ImageTarget:
    def __init__(self, targetName, targetID, targetRating):
        self.targetName = targetName
        self.targetID = targetID
        self.targetRating = targetRating

    def __repr__(self):
        return '\
        \n---------------------------------------------\
        \nImageTarget Name: %s\
        \nImageTarget ID: %s\
        \nImageTarget Rating: %d\
        \n---------------------------------------------' %(
            self.targetName,
            self.targetID,
            self.targetRating
        )



userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
requestTimeOut = 30



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Login & Check
# ///////////////////////////////////////////////////////////////////////////////////////////////////

# LOGIN_URL = 'https://developer.vuforia.com/siteminderagent/forms/login.fcc'

def QCAR_Login(username, password):

    file_object = open('log_a.txt', 'w+')

    print '>>> start login'
    file_object.write('>>> start login \n')
    LOGIN_URL = 'https://developer.vuforia.com/?destination=node'
    session = requests.Session()

    loginData = {
        'form_id': 'user_login',
        'SMENC': 'ISO-8859-1',
        'saf': '',
        'form_build_id': 'form-bf6df4b228bffe89dc4f32ef4baff935', 
        'SMRETRIES': '1',
        'name': username, 
        'smauthreason': '', 
        'smquerydata': '', 
        'pass': password,
        'TARGET': '/node',
        'target': '/target-manager-login?destination=https://developer.vuforia.com/user/confirm',
        'smagentname': '',
        'SMLOCALE': 'US-EN',
        'op': 'Log in'
    }

    headers = {
        'User-Agent': userAgent
    }

    r = session.post(LOGIN_URL, headers=headers, data=loginData, verify='./G3', timeout=requestTimeOut)

    if r.text.find('Hello') != -1:
        print '>>> login success'
        file_object.write('>>> login success \n')

        # Get user id
        result = re.findall('<a href="/user/(.*?)">', r.text, re.S)
        print '>>> user id: %s' %(result[0])
        file_object.write('>>> user id: %s' %(result[0]) + '\n')
        userID = result[0]
        #result = re.findall('<i class="icon-user"></i>(.*?)<span class="caret"></span>', r.text, re.S)
        result = re.findall('>Hello (.*?)<', r.text, re.S)
        userName = result[0]
        print '>>> user name: %s' %(result[0])
        file_object.write('>>> user name: %s' %(result[0]) + '\n')

        result = session.get(TOKEN_URL)

        token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
        #token = re.findall('id="edit-search-theme-form-form-token" value="(.*?)"', result.text, re.S)[0]
        print '>>> token: %s' %(token)
        file_object.write('>>> token: %s' %(token) + '\n')

        file_object.close()

        return session, User(userName, userID, token)
    else:
        f = open('login.html', 'w')
        f.write(r.text)
        f.close()
        print '>>> login failed'
        file_object.write('>>> login failed' + '\n')

        file_object.close()

        return None, None, None



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Get License List
# ///////////////////////////////////////////////////////////////////////////////////////////////////

LICENSE_URL = 'https://developer.vuforia.com/targetmanager/licenseManager/userLicenseDisplayListing'

LICENSES_MAX = 1000

def QCAR_Get_Licenses(session, user):

    print session

    licenseList = []

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
    print '>>> token: %s' %(token)
    '''

    licenseData = '\
    {\
    "sEcho":1,\
    "iColumns":5,\
    "sColumns":"",\
    "iDisplayStart":0,\
    "iDisplayLength":%d,\
    "amDataProp":[0,1,2,3,4],\
    "sSearch":"",\
    "bRegex":false,\
    "asSearch":["","","","",""],\
    "abRegex":[false,false,false,false,false],\
    "abSearchable":[true,true,true,true,true],\
    "aiSortCol":[0],\
    "asSortDir":["asc"],\
    "iSortingCols":1,\
    "abSortable":[true,true,true,true,true],\
    "dataToBeShownForUser":"%s"\
    }' %(LICENSES_MAX,user.userID)

    headers = {
        'CSRFToken': user.token,
        'content-type': 'application/json;charset=UTF-8',
        'Host': 'developer.vuforia.com',
        'Origin': 'https://developer.vuforia.com',
        'Referer': 'https://developer.vuforia.com/targetmanager/licenseManager/licenseListing',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': userAgent
    }

    result = session.post(LICENSE_URL, data=licenseData, headers=headers, timeout=requestTimeOut)
    jsonRes = json.loads(result.text)
    licenseRes = jsonRes['aaData']

    '''
    for group in dataBaseRes:
        for element in group.keys():

            if(group[element] != None and group[element]['project'] != None):
                ndataBase = Database(
                    group[element]['project']['projectName'],
                    group[element]['project']['projectId'],
                    group[element]['parentTargetId'],
                    group[element]['targetCount']
                )

                databaseList.append(ndataBase)
    '''
    for element in licenseRes:
        nLicense = License(
            element['app_name'],
            element['product_name'],
            element['license_id']
        )
        licenseList.append(nLicense)
    
    file_object = open('log_a.txt', 'a+')
    print licenseList
    file_object.write(('%s'%(licenseList)) + '\n')
    file_object.close()
    return licenseList



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Create Database
# ///////////////////////////////////////////////////////////////////////////////////////////////////

'''
CREATEDB_URL = 'https://developer.vuforia.com/targetmanager/project/deviceProjects'

def QCAR_Create_Databases(session, user, databaseName):

    headers = {
        'CSRFToken': user.token,
        'User-Agent': userAgent,
        'Content-Type': 'application/json'
    }

    jsonData = {
        "dataToBeShownForUser":"14247",
        "sEcho":5,
        "iColumns":1,
        "sColumns":"",
        "iDisplayStart":0,
        "iDisplayLength":1,
        "amDataProp":[0],
        "iSortingCols":0,
        "abSortable":["true"],
        "createProject":"true",
        "projectNameForCreation":databaseName
    }

    result = session.post(CREATEDB_URL, data=json.dumps(jsonData), headers=headers)

    file_object = open('log_a.txt', 'a+')
    print result.text
    file_object.write(result.text + '\n')
    file_object.close()
    return result
'''

CREATEDB_LICENSE_URL = 'https://developer.vuforia.com/targetmanager/project/createDatabaseWithLicense'

def QCAR_Create_License_Databases(session, user, databaseName, licenseID):

    print licenseID

    jsonData = {
        "dbtype":"device",
        "databaseTypeForLicenseFeature":"device",
        "databaseType":"tms",
        "applicationID":licenseID,
        "project_name":databaseName,
        'CSRFToken': user.token
    }

    headers = {
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2",
        "Connection":"keep-alive",
        "Content-Length":"188",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Host":"developer.vuforia.com",
        "Origin":"https://developer.vuforia.com",
        "Referer":"https://developer.vuforia.com/targetmanager/project/checkDeviceProjectsCreated?dataRequestedForUserId=",
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36",
        "X-Requested-With":"XMLHttpRequest"
    }

    result = session.post(CREATEDB_LICENSE_URL, data=jsonData, headers=headers)
    jsonRes = json.loads(result.text)

    if jsonRes['status'] == 'failed':
        print jsonRes['message']
        return False
    else:
        file_object = open('log_a.txt', 'a+')
        print result.text
        file_object.write(result.text + '\n')
        file_object.close()
        return True

# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Validate Database
# ///////////////////////////////////////////////////////////////////////////////////////////////////

VALIDATE_URL = 'https://developer.vuforia.com/targetmanager/project/validateProjectName'

def QCAR_Validate_Databases(session, user, databaseName, licenseID):

    createData = {
        "dbtype":"device",
        "databaseTypeForLicenseFeature":"device",
        "databaseType":"tms",
        "applicationID":licenseID,
        "project_name":databaseName,
        'CSRFToken': user.token
    }

    headers = {
        'CSRFToken': user.token,
        'User-Agent': userAgent
    }

    result = session.post(VALIDATE_URL, data=createData, headers=headers)

    file_object = open('log_a.txt', 'a+')
    print result.text
    file_object.write(result.text + '\n')
    file_object.close()
    return result



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Get Databases List
# ///////////////////////////////////////////////////////////////////////////////////////////////////

TOKEN_URL = 'https://developer.vuforia.com/targetmanager/project/checkDeviceProjectsCreated?dataRequestedForUserId='
DATABASES_URL = 'https://developer.vuforia.com/targetmanager/project/deviceProjects'

DATABASES_MAX = 1000

def QCAR_Get_Databases(session, user):

    print session

    databaseList = []

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
    print '>>> token: %s' %(token)
    '''

    databaseData = '\
    {\
    "dataToBeShownForUser":"%s",\
    "sEcho":2,\
    "iColumns":1,\
    "sColumns":"",\
    "iDisplayStart":0,\
    "iDisplayLength":%d,\
    "amDataProp":[0],\
    "iSortingCols":0,\
    "abSortable":[true]\
    }' %(user.userID,DATABASES_MAX)

    headers = {
        'CSRFToken': user.token,
        'content-type': 'application/json;charset=UTF-8',
        'Host': 'developer.vuforia.com',
        'Origin': 'https://developer.vuforia.com',
        'Referer': 'https://developer.vuforia.com/targetmanager/project/checkDeviceProjectsCreated?dataRequestedForUserId=',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': userAgent
    }

    result = session.post(DATABASES_URL, data=databaseData, headers=headers, timeout=requestTimeOut)
    print result.text
    jsonRes = json.loads(result.text)
    dataBaseRes = jsonRes['aaData']

    '''
    for group in dataBaseRes:
        for element in group.keys():

            if(group[element] != None and group[element]['project'] != None):
                ndataBase = Database(
                    group[element]['project']['projectName'],
                    group[element]['project']['projectId'],
                    group[element]['parentTargetId'],
                    group[element]['targetCount']
                )

                databaseList.append(ndataBase)
    '''
    for element in dataBaseRes:
        ndataBase = Database(
            element['project_name'],
            element['project_id'],
            element['app_name'],
            element['target_count']
        )
        databaseList.append(ndataBase)
    
    file_object = open('log_a.txt', 'a+')
    print databaseList
    file_object.write(('%s'%(databaseList)) + '\n')
    file_object.close()
    return databaseList



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Get Target List
# ///////////////////////////////////////////////////////////////////////////////////////////////////

#TOKEN_URL_2 = 'https://developer.vuforia.com/targetmanager/deviceTarget/deviceTargetListing'
IMAGETARGET_URL = 'https://developer.vuforia.com/targetmanager/project/userDeviceTargetDisplayListing'

IMAGETARGET_MAX = 1000


def QCAR_Get_Targets(session, user, database):

    imageTargetList = []

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
    '''
    print database.databaseID

    imageTargetData = '\
    {\
    "dataToBeShownForUser":"%s",\
    "sEcho":1,\
    "iColumns":6,\
    "sColumns":"",\
    "iDisplayStart":0,\
    "iDisplayLength":%d,\
    "amDataProp":[0,1,2,3,4,5],\
    "sSearch":"",\
    "bRegex":false,\
    "asSearch":["","","","","",""],\
    "abRegex":[false,false,false,false,false,false],\
    "abSearchable":[true,true,true,true,true,true],\
    "aiSortCol":[5],\
    "asSortDir":["desc"],\
    "iSortingCols":1,\
    "abSortable":[true,true,true,true,true,true],\
    "synch":false,\
    "projectId":"%s",\
    "projectIds":[1,2,3],\
    "isLegacyProject":"false",\
    "dbListingType":"device"\
    }' %(user.userID,IMAGETARGET_MAX,database.databaseID)

    headers = {
        'CSRFToken': user.token,
        'content-type': 'application/json;charset=UTF-8',
        'User-Agent': userAgent
    }

    
    result = session.post(IMAGETARGET_URL, data=imageTargetData, headers=headers, timeout=requestTimeOut)
    print result.text

    jsonRes = json.loads(result.text)
    dataBaseRes = jsonRes['aaData']

    '''
    for group in dataBaseRes:
        for element in group.keys():
            
            if(group[element] != None and group[element]['targetName'] != None):
                nImageTarget = ImageTarget(
                    group[element]['targetName'],
                    group[element]['targetId'],
                    group[element]['parentTargetId'],
                    group[element]['augmentableRating']
                )

                imageTargetList.append(nImageTarget)
    '''
    for element in dataBaseRes:
        nImageTarget = ImageTarget(
            element['target_name'],
            element['target_id'],
            element['augmentable_rating']
        )
        imageTargetList.append(nImageTarget)
                
    file_object = open('log_a.txt', 'a+')
    print imageTargetList
    file_object.write(('%s'%imageTargetList) + '\n')
    file_object.close()
    
    return imageTargetList



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Add New Target
# ///////////////////////////////////////////////////////////////////////////////////////////////////

#ADDTARGET_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/createNonCloudTarget'
ADDTARGET_URL = 'https://developer.vuforia.com/targetmanager/singleDeviceTarget/createNonCloudTarget'
DEFAULT_TARGET_WIDTH = 500

def QCAR_Add_Target(session, user, database, targetName, targetPath):

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
    '''

    addTargetData = {

        'targetName': targetName,
        'width': DEFAULT_TARGET_WIDTH,
        'TARGET_TYPE': 'singleDevice', 
        'PROJECT_ID': database.databaseID, 
        'projectName': database.databaseName, 
        'dataRequestedForUserId': user.userID, 
        'dataRequestedForUsername': user.userName, 
        'CSRFToken': user.token,
        'showAdminBreadCrumb': '',
        'CUBE_WIDTH': '',
        'CUBOID_WIDTH': '',
        'CUBOID_HEIGHT': '',
        'CUBOID_LENGTH': '',
        'BOTTOM_DIAMETER': '',
        'topDiameter': '',
        'CYLINDER_HEIGHT': '',
        'cubeWidth': '',
        'cuboidWidth': '',
        'cuboidHeight': '',
        'cuboidLength': '',
        'top_Diameter': '',
        'cylinderHeight': '',
        'bottomDiameter': ''

    }

    headers = {
        'CSRFToken': user.token,
        'User-Agent': userAgent
    }

    files = {'fileData[0]': open(targetPath, 'rb')}

    result = session.post(ADDTARGET_URL, data=addTargetData, files=files, headers=headers, timeout=requestTimeOut)

    file_object = open('log_a.txt', 'a+')
    print '>>> Add Target %s Result: %s' %(targetName, result.text)
    file_object.write('>>> Add Target %s Result: %s' %(targetName, result.text) + '\n')
    file_object.close()



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Delete Target
# ///////////////////////////////////////////////////////////////////////////////////////////////////

#DELETETARGET_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/deviceSingleDeleteTarget'
DELETETARGET_URL = 'https://developer.vuforia.com/targetmanager/singleDeviceTarget/deviceSingleDeleteTarget'

def QCAR_Delete_Target(session, user, target, database):

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
    '''

    deleteData = {
        'targetId': target.targetID,
        'projectId': database.databaseID
    }

    headers = {
        'CSRFToken': user.token,
        'User-Agent': userAgent
    }

    result = session.post(DELETETARGET_URL, data=deleteData, headers=headers, timeout=requestTimeOut)

    file_object = open('log_a.txt', 'a+')
    print '>>> Delete Target %s Result: %s' %(target.targetName, result.text)
    file_object.write('>>> Delete Target %s Result: %s' %(target.targetName, result.text) + '\n')
    file_object.close()
    


# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Download Package
# ///////////////////////////////////////////////////////////////////////////////////////////////////

#CREATEPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/createDataBaseForDownloadZip'
CREATEPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/project/createDataBaseForDownloadZip'
#CHECKPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/waitForTimeHintExpiry'
CHECKPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/project/waitForTimeHintExpiry'
#DOWNLOADPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/fetchDataBaseForDownloadZip'
DOWNLOADPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/project/fetchDataBaseForDownloadZip'

def QCAR_Check_Package(session, token, url):
    
    headers = {
        'CSRFToken': token,
        'User-Agent': userAgent
    }

    checkData = {
        'dataSetUrl': url
    }

    result = session.post(CHECKPACKAGE_URL, data=checkData, headers=headers, timeout=requestTimeOut)

    file_object = open('log_a.txt', 'a+')
    print result.text
    file_object.write(result.text + '\n')
    file_object.close()
    

    if result.text == 'true':
        return True
    else:
        return False

def QCAR_Download_Package(session, user, database, targetList, downloadPath, licenseID):

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]

    print '>>> token %s' %(token)
    '''

    file_object = open('log_a.txt', 'a+')
    print '>>> Start Make Package'
    file_object.write('>>> Start Make Package' + '\n')
    file_object.close()
    

    ids = ''
    for target in targetList:
        ids += target.targetID + '__-1::'

    file_object = open('log_a.txt', 'a+')
    print ids
    file_object.write(ids + '\n')
    file_object.close()

    createData = {
        'PROJECT_ID': database.databaseID,
        'DATABASE_TYPE': 'native',
        'databaseName': database.databaseName,
        'ids': ids,
        'initialProjName': database.databaseName
    }

    headers = {
        'CSRFToken': user.token,
        'User-Agent': userAgent
    }

    result = session.post(CREATEPACKAGE_URL, data=createData, headers=headers, timeout=requestTimeOut)

    file_object = open('log_a.txt', 'a+')
    print '>>> Make Package Result: %s' %(result.text)
    file_object.write('>>> Make Package Result: %s' %(result.text) + '\n')
    file_object.close()
    
    jsonRes = json.loads(result.text)

    count = 1

    while QCAR_Check_Package(session, user.token, jsonRes[3]) == False:
        time.sleep(1)
        count += 1
        if count > 15:
            print '>>> download failed'
            return None
        else:
            print '>>> wait %d seconds' %(count)
    
    file_object = open('log_a.txt', 'a+')
    print '>>> Waitting For Download'
    file_object.write('>>> Waitting For Download' + '\n')
    file_object.close()

    downloadData = {
        'dataSetUrl': jsonRes[3],
        'timeDelay': jsonRes[2],
        'targetIds': jsonRes[8],
        'databaseNameForFetchFile': jsonRes[5],
        'download_token_value_id': datetime.datetime.now().microsecond,
        'PROJECT_ID_For_Fetch_File': jsonRes[6],
        'dbType': jsonRes[4],
        'initialProjName': jsonRes[7],
        'CSRFToken': user.token,
        'projectLicenseId': licenseID
    }

    headers = {
        'CSRFToken': user.token,
        'User-Agent': userAgent
    }

    result = session.post(DOWNLOADPACKAGE_URL, data=downloadData, headers=headers, timeout=requestTimeOut)

    #file_object = open('log_a.txt', 'a+')
    #print result.content
    #file_object.write(result.content + '\n')
    #file_object.close()

    file_object = open(downloadPath + database.databaseName + '.zip', 'wb')
    file_object.write(result.content)
    file_object.close()
