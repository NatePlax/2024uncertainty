#include <cstdint>
#include <vector>
#include <libusb.h>
#include <iostream>
#include <boost/crc.hpp>      // for boost::crc_basic, boost::crc_optimal
#include <boost/cstdint.hpp>  // for boost::uint16_t

// CRSF protocol constants
const uint8_t CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16;

const uint16_t vendor_id = 0x04d8;
const uint16_t product_id = 0xf94c;

const int endpoint_out = 0x01;

void send_bytes_to_usb(libusb_device_handle* devHandle, const unsigned char* data, int length) {
    int transferred;

    // Sending data to the USB device
    int result = libusb_bulk_transfer(devHandle, endpoint_out, const_cast<unsigned char*>(data), length, &transferred, 1000);

    if (result == 0) {
        std::cout << "Sent " << transferred << " bytes to USB device." << std::endl;
    } else {
        std::cerr << "Error sending data to USB device: " << libusb_error_name(result) << std::endl;
    }
}

struct CrsfChannels {
    uint32_t ch0 : 11;
    uint32_t ch1 : 11;
    uint32_t ch2 : 11;
    uint32_t ch3 : 11;
    uint32_t ch4 : 11;
    uint32_t ch5 : 11;
    uint32_t ch6 : 11;
    uint32_t ch7 : 11;
    uint32_t ch8 : 11;
    uint32_t ch9 : 11;
    uint32_t ch10 : 11;
    uint32_t ch11 : 11;
    uint32_t ch12 : 11;
    uint32_t ch13 : 11;
    uint32_t ch14 : 11;
    uint32_t ch15 : 11;
} __attribute__ ((__packed__));

uint8_t gencrc(uint8_t *data, size_t len)
{
   //boost::crc_basic<8>  crc_ccitt1(0x01D5, 0, 0, false, false );
   //crc_ccitt1.process_bytes(data, len);
   //return crc_ccitt1.checksum();
   return 0xad;
}

// Function to send a CRSF packet
void send_crsf_packet(libusb_device_handle* devHandle, const CrsfChannels& packet_data) {
    char packed[sizeof(CrsfChannels)];
    std::memcpy(packed, &packet_data, sizeof(CrsfChannels));

    char data_for_crc[sizeof(CrsfChannels) + 1];
    data_for_crc[0] = CRSF_FRAMETYPE_RC_CHANNELS_PACKED;
    for (int i = 1; i < sizeof(data_for_crc); i++) {
        data_for_crc[i] = packed[i - 1];
    }

    uint8_t crc = gencrc((uint8_t *)data_for_crc, sizeof(data_for_crc));
    std::cout << crc;
    char complete_packet[sizeof(data_for_crc) + 3];
    complete_packet[0] = 0xEE;
    complete_packet[1] = sizeof(packed) + 2;
    for (int i = 2; i < sizeof(complete_packet) - 1; i++) {
        complete_packet[i] = data_for_crc[i - 2];
    }
    complete_packet[sizeof(complete_packet) - 1] = (char) crc;


    // Call the send_bytes_to_usb function to send data
    // send_bytes_to_usb(devHandle, reinterpret_cast<const unsigned char*>(complete_packet), sizeof(complete_packet));
}

int main() {
    libusb_context* ctx = NULL;
    int result = libusb_init(&ctx);
    if (result < 0) {
        std::cerr << "Error initializing libusb: " << libusb_error_name(result) << std::endl;
        return 1;
    }

    libusb_device_handle* devHandle = libusb_open_device_with_vid_pid(ctx, vendor_id, product_id);
    /*
    if (devHandle == NULL) {
        std::cerr << "USB device not found or unable to open." << std::endl;
        libusb_exit(ctx);
        return 1;
    }
    */

    CrsfChannels channels;

    // Populate all channels with the value 992
    channels.ch0 = 992;
    channels.ch1 = 992;
    channels.ch2 = 992;
    channels.ch3 = 992;
    channels.ch4 = 992;
    channels.ch5 = 992;
    channels.ch6 = 992;
    channels.ch7 = 992;
    channels.ch8 = 992;
    channels.ch9 = 992;
    channels.ch10 = 992;
    channels.ch11 = 992;
    channels.ch12 = 992;
    channels.ch13 = 992;
    channels.ch14 = 992;
    channels.ch15 = 992;

    send_crsf_packet(devHandle, channels);

    libusb_close(devHandle);
    libusb_exit(ctx);

    return 0;
}