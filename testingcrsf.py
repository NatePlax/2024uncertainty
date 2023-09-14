import pygame
import time
import usb.core
import usb.util
import sys
from ctypes import *
import ctypes
import crcmod
import numpy as np

# TODO: UT_AUTOMATA values. Need to figure these out for the Omega truck
normal_speed = 1.0
turbo_speed = 3.4
accel_limit = 6.0
maxTurnRate = 0.25
commandInterval = 1.0/20
speed_to_erpm_gain = 5171
speed_to_erpm_offset = 180.0
erpm_speed_limit = 22000
steering_to_servo_gain = -0.9015
steering_to_servo_offset = 0.553
servo_min = 0.05
servo_max = 0.95
wheelbase = 0.324

min_v = -0.3
max_v = 0.3
# May need changing, rough estimate based on crsf docs
crsf_val_half_range = 810
crsf_val_middle = 992


def getCommandsFromJoystick(axes, buttons):
    steer_joystick = -axes[0]
    drive_joystick = -axes[4]
    turbo_mode = axes[2] >= 0.9
    max_speed = turbo_mode*turbo_speed + (1-turbo_mode)*normal_speed
    speed = drive_joystick*max_speed
    steering_angle = steer_joystick*maxTurnRate
    last_speed = 0.0
    smooth_speed = max(speed, last_speed - commandInterval*accel_limit)
    smooth_speed = min(smooth_speed, last_speed + commandInterval*accel_limit)
    last_speed = smooth_speed
    erpm = speed_to_erpm_gain * smooth_speed + speed_to_erpm_offset
    erpm_clipped = min(max(erpm, -erpm_speed_limit), erpm_speed_limit)
    clipped_speed = (erpm_clipped - speed_to_erpm_offset) / speed_to_erpm_gain

    servo = steering_to_servo_gain * steering_angle + steering_to_servo_offset
    clipped_servo = np.fmin(np.fmax(servo, servo_min), servo_max)
    steering_angle = (clipped_servo - steering_to_servo_offset) / steering_to_servo_gain
    print(clipped_speed, steering_angle)
    return clipped_speed, steering_angle

class CrsfChannels(ctypes.LittleEndianStructure):
    _fields_ = (
        ("ch0", ctypes.c_uint32, 11),
        ("ch1", ctypes.c_uint32, 11),
        ("ch2", ctypes.c_uint32, 11),
        ("ch3", ctypes.c_uint32, 11),
        ("ch4", ctypes.c_uint32, 11),
        ("ch5", ctypes.c_uint32, 11),
        ("ch6", ctypes.c_uint32, 11),
        ("ch7", ctypes.c_uint32, 11),
        ("ch8", ctypes.c_uint32, 11),
        ("ch9", ctypes.c_uint32, 11),
        ("ch10", ctypes.c_uint32, 11),
        ("ch11", ctypes.c_uint32, 11),
        ("ch12", ctypes.c_uint32, 11),
        ("ch13", ctypes.c_uint32, 11),
        ("ch14", ctypes.c_uint32, 11),
        ("ch15", ctypes.c_uint32, 11)
    )


def get11PaddedBitString(bitstring):
    while len(bitstring) < 11:
        bitstring = '0' + bitstring
    return bitstring

# Will be replaced once we move to C++
def pack_structure(structure: CrsfChannels):
    # First, get all the bit strings, unpadded past 11.
    # Concatenate them together
    # Break them down into chunks of 8
    bitstring = ""
    for field_name, _, _ in structure._fields_:
        field_value = getattr(structure, field_name)
        bitstring += get11PaddedBitString(bin(field_value)[2:])

    hex_value = hex(int(bitstring, 2))[2:]

    byte_array = []

    # Iterate through the hex string in pairs of two characters
    for i in range(0, len(hex_value), 2):
        byte_string = hex_value[i:i+2]
        byte_array.insert(0, int(byte_string, 16))
    return byte_array


# CRSF protocol constants
CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16

vendor_id = 0x04d8
product_id = 0xf94c

tracer = usb.core.find(idVendor=vendor_id, idProduct=product_id)

if tracer is None:
    raise ValueError("Device Not Found")
else:
    print("Found tracer!")

endpoint = 0x01
interface = tracer[0].interfaces()[0].bInterfaceNumber

if tracer.is_kernel_driver_active(interface):
    try:
        tracer.detach_kernel_driver(interface)
    except usb.core.USBError as e:
        sys.exit("could not detach kernel driver from interface")

# Function to send a CRSF packet
def send_crsf_packet(packet_data):
    packed = pack_structure(packet_data)
    dataForCRC = [CRSF_FRAMETYPE_RC_CHANNELS_PACKED] + packed
    crc8d5_func = crcmod.mkCrcFun(0xD5 + 256, rev=False, initCrc=0)
    crc = crc8d5_func(bytearray(dataForCRC))
    complete_packet = [0xEE, len(packed) + 2] + dataForCRC + [crc]
    bytesArray = bytes(complete_packet)
    tracer.write(endpoint, bytesArray)

"""
channels_data = CrsfChannels()

channels_data.ch0 = 1700
channels_data.ch1 = 1700
channels_data.ch2 = 1700
channels_data.ch3 = 0
channels_data.ch4 = 0
channels_data.ch5 = 0
channels_data.ch6 = 0
channels_data.ch7 = 0
channels_data.ch8 = 0
channels_data.ch9 = 0
channels_data.ch10 = 0
channels_data.ch11 = 0
channels_data.ch12 = 0
channels_data.ch13 = 0
channels_data.ch14 = 0
channels_data.ch15 = 0

send_crsf_packet(channels_data)
"""

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Check if there is at least one joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    pygame.quit()
    exit()

# Initialize the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

output_file = "joystick_commands.txt"

try:
    with open(output_file, "w") as file:
        print("Recording joystick commands...")
        while True:
            pygame.event.get()
            
            # Get joystick input
            command = {
                "timestamp": time.time(),
                "axis_values": [joystick.get_axis(i) for i in range(joystick.get_numaxes())],
                "button_values": [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
            }

            # Get the commanded velocity and steering angle from the joystick input
            cmd_v, cmd_sa = getCommandsFromJoystick(command["axis_values"], command["button_values"])

            # Get the value to send to the esc
            crsf_v_value = int(crsf_val_middle + (crsf_val_half_range / max_v * cmd_v))


            # TODO: Fix and implement servo values
            channels_data = CrsfChannels()
            channels_data.ch0 = crsf_v_value
            channels_data.ch1 = crsf_v_value
            channels_data.ch2 = crsf_v_value
            send_crsf_packet(channels_data)
            
            # Write the command to the file
            #file.write(str(command) + "\n")
            
            # TODO: Possibly remove, see if we need to control the rate at which messages are sent to transmitter. Could be related to bug
            time.sleep(0.0001)

except KeyboardInterrupt:
    print("\nRecording stopped.")
finally:
    joystick.quit()
    pygame.quit()