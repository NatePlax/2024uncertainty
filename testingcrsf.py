import serial
import pygame
import time

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

# Replace with your serial port name
serial_port = "/dev/ttyUSB0"  # Example for Linux, use COMx for Windows

# Open the serial port
ser = serial.Serial(serial_port, baudrate=115200, timeout=1)

# Function to send a CRSF packet
def send_crsf_packet(packet_data):
    # Calculate CRC
    crc = sum(packet_data) & 0xFF

    # Construct the complete packet
    complete_packet = [0xC8, len(packet_data) + 2, CRSF_FRAMETYPE_RC_CHANNELS_PACKED] + packet_data + [crc]

    # Send the CRSF packet
    ser.write(bytes(complete_packet))

# Replace with your RC channel values (11-bit values, little-endian)
rc_channels = [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]

# Convert RC channel values to 11-bit little-endian representation
rc_data = []
for value in rc_channels:
    rc_data.append(value & 0x7FF)
    rc_data.append(value >> 11)

# Send the CRSF packet with RC channel data
send_crsf_packet(rc_data)

# Close the serial port when done
ser.close()