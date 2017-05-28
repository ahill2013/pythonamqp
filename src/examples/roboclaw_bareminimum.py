from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM3",115200)
#Linux comport name
rc = Roboclaw("/dev/roboclaw",115200)

rc.Open()
