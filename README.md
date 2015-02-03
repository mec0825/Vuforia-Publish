# Vuforia-Publish

Python script for vuforia target manager

![](http://mec0825.net/images/QCAR/targetManager.png)

## config.ini
````
[User]
username=
password=

[Settings]
databaseName=test
imagePath=./images/
packagePath=./
````

## QCAR.py
This file is for datastructure and apis.

## Service.py
This file is for business and test.

## Use
To upload images from imagePath and download zip file to packagePath.
````
// set config.ini before this
python Service.py
````
