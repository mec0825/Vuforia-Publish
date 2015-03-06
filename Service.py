#!/usr/bin/env python
# coding:utf-8

import QCAR
import os
import time
import ConfigParser
import sys
import codecs

# ///////////////////////////////////////////////////////////////////////////////////////////////////
# Running Code

config = ConfigParser.ConfigParser()
#config.read('config.ini')
config.readfp(codecs.open('config.ini', "r", "utf-8-sig"))

username = config.get('User','username')
password = config.get('User','password')
databaseName = config.get('Settings','databaseName')
imagePath = config.get('Settings','imagePath')
packagePath = config.get('Settings','packagePath')


session, user =  QCAR.QCAR_Login(username, password)

licenses = QCAR.QCAR_Get_Licenses(session, user)
response = QCAR.QCAR_Validate_Databases(session, user, databaseName, licenses[0].licenseID)
validateResult = response.content

print validateResult

if validateResult == "true":
    print ">>> database exist"
else:
    print ">>> create database"
    if len(licenses) > 0:
        QCAR.QCAR_Create_License_Databases(session, user, databaseName, licenses[0].licenseID)
    else:
        print ">>> no license find"

databases = QCAR.QCAR_Get_Databases(session, user)

database = None
for element in databases:
    if element.databaseName == databaseName:
        database = element

print '>>> ' + database.databaseName

targetList = QCAR.QCAR_Get_Targets(session, user, database)

remoteTargetNameList = []
for element in targetList:
    remoteTargetNameList.append(element.targetName)

localTargetNameList = []
for root, dirs, files in os.walk(imagePath):
    for element in files:
        print '>>> File name: %s' %(element)
        if element.split('.')[1] == 'JPG' or element.split('.')[1] == 'jpg':
            localTargetNameList.append(element)

commonTargetNameList = []
for rName in remoteTargetNameList:
    for lName in localTargetNameList:
        if rName == lName:
            commonTargetNameList.append(rName)

for element in targetList:
    canDelete = True
    for name in commonTargetNameList:
        if element.targetName == name:
            canDelete = False

    if canDelete == True:
        QCAR.QCAR_Delete_Target(session, user, element, database)

for root, dirs, files in os.walk(imagePath):
    for element in files:
        print '>>> File name: %s' %(element)
        
        canAdd = True
        for name in commonTargetNameList:
            if element == name:
                canAdd = False

        if canAdd == True:
            if element.split('.')[1] == 'JPG' or element.split('.')[1] == 'jpg':
                QCAR.QCAR_Add_Target(session, user, database, element.split('.')[0], imagePath + element)

isTargetsReady = False
while isTargetsReady == False:
    isTargetsReady = True
    targetList = QCAR.QCAR_Get_Targets(session, user, database)
    
    if len(targetList) == 0:
        isTargetsReady = False
        time.sleep(15)

    for element in targetList:
        if element.targetRating == -1:
            isTargetsReady = False
            time.sleep(15)

QCAR.QCAR_Download_Package(session, user, database, targetList, packagePath, licenses[0].licenseID)
