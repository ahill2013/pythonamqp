import time

from roboclaw import Roboclaw

# Windows comport name
# rc = Roboclaw("COM9", 115200)
# Linux comport name
rc = Roboclaw("/dev/roboclaw", 115200)


def displayspeed():
    enc1 = rc.ReadEncM1(address)
    enc2 = rc.ReadEncM2(address)
    speed1 = rc.ReadSpeedM1(address)
    speed2 = rc.ReadSpeedM2(address)

    print("Encoder1:"),
    if enc1[0] == 1:
        print enc1[1],
        print format(enc1[2], '02x'),
    else:
        print "failed",
    print "Encoder2:",
    if enc2[0] == 1:
        print enc2[1],
        print format(enc2[2], '02x'),
    else:
        print "failed ",
    print "Speed1:",
    if speed1[0]:
        print speed1[1],
    else:
        print "failed",
    print("Speed2:"),
    if speed2[0]:
        print speed2[1]
    else:
        print "failed "

rc.Open()
address = 0x80

while 1:
    rc.ForwardM1(address, 127)  # 1/4 power forward
    # rc.BackwardM2(address, 32)  # 1/4 power backward
    # time.sleep(2)

    # rc.BackwardM1(address, 32)  # 1/4 power backward
    rc.ForwardM2(address, 127)  # 1/4 power forward

    for i in range(0, 80):
        displayspeed()
        time.sleep(0.1)

    time.sleep(2)

    rc.BackwardM1(address, 0)  # Stopped
    rc.ForwardM2(address, 0)  # Stopped
    for i in range(0, 80):
        displayspeed()
        time.sleep(0.1
)
    time.sleep(5)

    # m1duty = 16
    # m2duty = -16
    # rc.ForwardBackwardM1(address, 64 + m1duty)  # 1/4 power forward
    # rc.ForwardBackwardM2(address, 64 + m2duty)  # 1/4 power backward
    # time.sleep(2)

    # m1duty = -16
    # m2duty = 16
    # rc.ForwardBackwardM1(address, 64 + m1duty)  # 1/4 power backward
    # rc.ForwardBackwardM2(address, 64 + m2duty)  # 1/4 power forward
    # time.sleep(2)

    # rc.ForwardBackwardM1(address, 64)  # Stopped
    # rc.ForwardBackwardM2(address, 64)  # Stopped
    # time.sleep(2)
