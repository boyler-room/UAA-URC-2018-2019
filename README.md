# UAA-URC 2018-2019

UAA Robotics code for the 2018-2019 season of the University Rover Challenge

duino - arduino hardware interface programs
  arm     arm controller: shoulder and elbow joints
  crane   science platform crane controller
  dirtc   science platform dirt scoop controller
  eff     end effector controller: wrist joint, grabber, screwdriver, and laser diodes
  gas     science platform gas sensors
  mast    mast camera gimble controller and autonomous section LED indicators

rover - rover control and management applications
  ROS implementation, message types in msg/ and srv/, source in src/
    arm.py    arm control interface
    drive.py  drive motor control interface
    gpd.py    USB gamepad control
    nav.py    gps readings
    stream.py camera streams via gst-launch
