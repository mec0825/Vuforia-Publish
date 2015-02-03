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


class Database:
    def __init__(self, databaseName, databaseID, parentTargetID, targetCount):
        self.databaseName = databaseName
        self.databaseID = databaseID
        self.parentTargetID = parentTargetID 
        self.targetCount = targetCount

    def __repr__(self):
        return '\
        \n---------------------------------------------\
        \nDatabase Name: %s\
        \nDatabase ID: %s\
        \nParentTargetID: %s\
        \nTarget Count:%s\
        \n---------------------------------------------' %(
            self.databaseName,
            self.databaseID,
            self.parentTargetID,
            self.targetCount
        )


class ImageTarget:
    def __init__(self, targetName, targetID, parentTargetID, targetRating):
        self.targetName = targetName
        self.targetID = targetID
        self.parentTargetID = parentTargetID
        self.targetRating = targetRating

    def __repr__(self):
        return '\
        \n---------------------------------------------\
        \nImageTarget Name: %s\
        \nImageTarget ID: %s\
        \nParentTargetID: %s\
        \nImageTarget Rating: %d\
        \n---------------------------------------------' %(
            self.targetName,
            self.targetID,
            self.parentTargetID,
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

    if r.text.find('My Account') != -1:
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
# Create Database
# ///////////////////////////////////////////////////////////////////////////////////////////////////

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



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Validate Database
# ///////////////////////////////////////////////////////////////////////////////////////////////////

VALIDATE_URL = 'https://developer.vuforia.com/targetmanager/project/validateProjectName'

def QCAR_Validate_Databases(session, user, databaseName):

    createData = {
        'project_name': databaseName
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
    jsonRes = json.loads(result.text)
    dataBaseRes = jsonRes['aaData']

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
    
    file_object = open('log_a.txt', 'a+')
    print databaseList
    file_object.write(('%s'%(databaseList)) + '\n')
    file_object.close()
    return databaseList



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Get Target List
# ///////////////////////////////////////////////////////////////////////////////////////////////////

#TOKEN_URL_2 = 'https://developer.vuforia.com/targetmanager/deviceTarget/deviceTargetListing'
IMAGETARGET_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/userDeviceTargetDisplayListing'

IMAGETARGET_MAX = 1000


def QCAR_Get_Targets(session, user, database):

    imageTargetList = []

    '''
    result = session.get(TOKEN_URL)
    #print result.text

    token = re.findall('<input type="hidden" name="CSRFToken" value="(.*?)">', result.text, re.S)[0]
    '''

    imageTargetData = '\
    {\
    "dataToBeShownForUser":"%s",\
    "sEcho":2,\
    "iColumns":1,\
    "sColumns":"",\
    "iDisplayStart":0,\
    "iDisplayLength":%d,\
    "amDataProp":[0],\
    "iSortingCols":0,\
    "abSortable":[true],\
    "synch":false,\
    "projectId":"%s",\
    "projectIds":[1,2,3]\
    }' %(user.userID,IMAGETARGET_MAX,database.databaseID)

    headers = {
        'CSRFToken': user.token,
        'content-type': 'application/json;charset=UTF-8',
        'User-Agent': userAgent
    }

    
    result = session.post(IMAGETARGET_URL, data=imageTargetData, headers=headers, timeout=requestTimeOut)
    #print result.text

    jsonRes = json.loads(result.text)
    dataBaseRes = jsonRes['aaData']

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
                
    file_object = open('log_a.txt', 'a+')
    print imageTargetList
    file_object.write(('%s'%imageTargetList) + '\n')
    file_object.close()
    
    return imageTargetList



# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Add New Target
# ///////////////////////////////////////////////////////////////////////////////////////////////////

ADDTARGET_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/createNonCloudTarget'
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

DELETETARGET_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/deviceSingleDeleteTarget'

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

CREATEPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/createDataBaseForDownloadZip'
CHECKPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/waitForTimeHintExpiry'
DOWNLOADPACKAGE_URL = 'https://developer.vuforia.com/targetmanager/deviceTarget/fetchDataBaseForDownloadZip'

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

def QCAR_Download_Package(session, user, database, targetList, downloadPath):

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
        'targetIds': jsonRes[7],
        'databaseNameForFetchFile': jsonRes[5],
        'download_token_value_id': datetime.datetime.now().microsecond,
        'PROJECT_ID_For_Fetch_File': jsonRes[6],
        'dbType': jsonRes[4],
        'initialProjName': jsonRes[8],
        'CSRFToken': user.token
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
