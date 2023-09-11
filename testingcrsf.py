# import pygame
# import time
import usb.core
import usb.util

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

# Create a file to record commands
output_file = "joystick_commands.txt"

try:
    with open(output_file, "w") as file:
        print("Recording joystick commands. Press 'Ctrl + C' to stop.")
        while True:
            pygame.event.get()
            
            # Get joystick input
            command = {
                "timestamp": time.time(),
                "axis_values": [joystick.get_axis(i) for i in range(joystick.get_numaxes())],
                "button_values": [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
            }
            
            # Write the command to the file
            #file.write(str(command) + "\n")
            print(command)
            
            # Wait for a short time to avoid excessive writing
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\nRecording stopped.")
finally:
    joystick.quit()
    pygame.quit()

"""
# CRSF protocol constants
CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16

vendor_id = 0x04d8
product_id = 0xf94c

tracer = usb.core.find(idVendor=vendor_id, idProduct=product_id)

if tracer is None:
    raise ValueError("Device Not Found")
else:
    print("Found tracer!")

endpoint = 0x1
interface = tracer[0].interfaces()[0].bInterfaceNumber

if tracer.is_kernel_driver_active(interface):
    try:
        tracer.detach_kernel_driver(interface)
    except usb.core.USBError as e:
        sys.exit("could not detach kernel driver from interface")

"""
for cfg in tracer:
    for intf in cfg:
        for ep in intf:
            print(f"Endpoint Address: {ep.bEndpointAddress}")
            print(f"Transfer Type: {usb.util.endpoint_type(ep.bmAttributes)}")
"""


# Function to send a CRSF packet
def send_crsf_packet(packet_data):
    crc = sum(packet_data) & 0xFF
    complete_packet = [0xEE, len(packet_data) + 2, CRSF_FRAMETYPE_RC_CHANNELS_PACKED] + packet_data + [crc]
    tracer.write(endpoint, bytes(complete_packet))

# Replace with your RC channel values (11-bit values, little-endian)
rc_channels = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]

# Convert RC channel values to 11-bit little-endian representation
rc_data = []
for value in rc_channels:
    rc_data.append(value & 0x7FF)
    rc_data.append(value >> 11)

# Send the CRSF packet with RC channel data
send_crsf_packet(rc_data)

