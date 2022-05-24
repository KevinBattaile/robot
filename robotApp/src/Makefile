TOP=../..

include $(TOP)/configure/CONFIG

PROD_IOC = robot
DBD += robot.dbd

robot_DBD += base.dbd
robot_DBD += calc.dbd
robot_DBD += asyn.dbd
robot_DBD += drvAsynIPPort.dbd
robot_DBD += stream.dbd

robot_LIBS += calc
robot_LIBS += asyn
robot_LIBS += stream

robot_SRCS += robot_registerRecordDeviceDriver.cpp
robot_SRCS += robotMain.cpp

robot_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
