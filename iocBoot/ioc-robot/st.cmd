#!../../bin/linux-x86_64/robot

< envPaths

epicsEnvSet("STREAM_PROTOCOL_PATH", "$(TOP)/robotApp/Db")

epicsEnvSet("PREFIX", "XF:19IDC-ES{Rbt:1}")
epicsEnvSet("PORT",   "ROBOT")

dbLoadDatabase("$(TOP)/dbd/robot.dbd",0,0)
robot_registerRecordDeviceDriver(pdbbase)

drvAsynIPPortConfigure("$(PORT)", "10.19.2.40:5002")
#drvAsynIPPortConfigure("$(PORT)", "localhost:5002")

asynOctetSetInputEos("$(PORT)", 0, "\r\n")
asynOctetSetOutputEos("$(PORT)", 0, "\r\n")

dbLoadRecords("$(TOP)/db/robot.db","P=$(PREFIX),PORT=$(PORT)")
dbLoadRecords("$(ASYN)/db/asynRecord.db","P=$(PREFIX),R=Asyn,PORT=$(PORT),ADDR=0,OMAX=80,IMAX=80")

iocInit()
