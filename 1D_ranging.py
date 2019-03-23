#!/usr/bin/env python
"""
The Pozyx ready to range tutorial (c) Pozyx Labs
Please read the tutorial: https://www.pozyx.io/Documentation/Tutorials/ready_to_range/Python
This demo requires two Pozyx devices. It demonstrates the ranging capabilities and the functionality to
to remotely control a Pozyx device. Move around with the other Pozyx device.
This demo measures the range between the two devices.
"""
import sys
import os
import atexit
import signal
from pypozyx import *
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
import time
from modules.file_writing import RangingFileWriting as FileIO
from modules.file_writing import FileOpener
from modules.console_logging_functions import CondensedConsoleLogging as Console
from modules.configuration import Configuration as Configuration
from modules.messaging import PozyxUDP, MmapCommunication
sys.path.append(sys.path[0] + "/..")
from constants import definitions
 

class RangeOutputContainer:
    """Holds the range data, motion data, and more for a single device"""

    def __init__(self, tag, device_range, smoothed_range, sensor_data, loop_status, num_of_dropped_zero, num_of_error):
        self.tag = tag
        self.device_range = device_range
        self.sensor_data = sensor_data
        self.loop_status = loop_status
        self.smoothed_range = smoothed_range
        self.velocity = ""
        self.num_of_dropped_zero = num_of_dropped_zero      # set counter for dropped zero that occurs when distance randomly becomes zero 
        self.num_of_error = num_of_error                    # set counter for whenever POZYX_FAILURE is returned


class ReadyToRange(object):
    """Continuously performs ranging between the Pozyx and a destination"""

    def __init__(self, i_pozyx, i_tags, i_destination_id, i_to_get_sensor_data,
                 i_protocol=POZYX_RANGE_PROTOCOL_FAST):
        self.pozyx = i_pozyx
        self.tags = i_tags
        self.destination_id = i_destination_id
        self.to_get_sensor_data = i_to_get_sensor_data
        self.protocol = i_protocol

    def loop(self, range_data_array):
        """Performs ranging and collects motion data as needed"""
        for idx, tag in enumerate(self.tags):
            # get 1D position in this section
            device_range = DeviceRange()
            loop_status = self.pozyx.doRanging(tag, device_range, self.destination_id)
            if int(device_range.distance) > 2147483647:
                loop_status = POZYX_FAILURE

            # get motion data in this section-
            sensor_data = SensorData()
            calibration_status = SingleRegister()
            if self.to_get_sensor_data:
                sensor_data.data_format = 'IhhhhhhhhhhhhhhhhhhhhhhB'
                if tag is not None or self.pozyx.checkForFlag(POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS:
                    loop_status = self.pozyx.getAllSensorData(sensor_data, tag)
                    loop_status &= self.pozyx.getCalibrationStatus(calibration_status, tag)

            single = range_data_array[idx]
            single.tag = tag
            single.device_range = device_range
            single.sensor_data = sensor_data
            single.loop_status = loop_status

            if loop_status != POZYX_SUCCESS:
                single.num_of_error += 1

class ContinueI(Exception):
    pass


continue_i = ContinueI()


if __name__ == "__main__":
    serial_port = Configuration.get_correct_serial_port()
    pozyx = PozyxSerial(serial_port)
    use_velocity = True

    # import properties from saved properties file
    config = Configuration.get_properties()
    tags = config.tags
    anchors = config.anchors
    attributes_to_log = config.attributes_to_log
    to_use_file = config.use_file
    filename = config.data_file
    range_anchor_id = config.range_anchor_id
    alpha_pos = config.position_smooth
    alpha_vel = config.velocity_smooth
    smooth_velocity = alpha_vel < 1.00
    share_data_over_lan = config.share_data_over_lan

    to_get_sensor_data = not attributes_to_log == []

    ranging_protocol = POZYX_RANGE_PROTOCOL_PRECISION  # the ranging protocol

    r = ReadyToRange(
        pozyx, tags, range_anchor_id, to_get_sensor_data, ranging_protocol)

    range_data_array = []
    previous_distance_array = []
    for tag in tags:
        range_data_array.append(RangeOutputContainer(None, None, 0, None, None, 0, 0))
        previous_distance_array.append(0)
    if not tags:
        sys.exit("Please add at least one remote device for 1D ranging.")

    
    filepath = os.path.expanduser('~') + "/Documents/PSUPozyx/Producer File/"
    producer_name = filepath + "producer_file.csv"
    os.remove(producer_name)   # remove old file so the program won't have to overwrite the old file which will slow it down
    producer_write = open(producer_name, 'w', 1)
    FileIO.write_range_headers_to_file(producer_write, tags, attributes_to_log)

    if to_use_file:
        logfile = FileOpener.create_csv(filename)
        FileIO.write_range_headers_to_file(logfile, tags, attributes_to_log)
    # wait for motion data to work before running main loop
    if to_get_sensor_data:
        not_started = True
        while not_started:
            r.loop(range_data_array)
            try:
                not_started = int(range_data_array[0].sensor_data.pressure.value) == 0
            except TypeError:
                not_started = True

    udp_messenger = None
    mmap_messenger = None
    try:
        # Initialize EMA filter so it doesn't start at 0
        r.loop(range_data_array)
        for single_data in range_data_array:
            if type(single_data.device_range.distance) is int:
                single_data.smoothed_range = single_data.device_range.distance

        # update message client after data working - don't send initial 0 range over osc
        if share_data_over_lan:
            udp_messenger = PozyxUDP()
        mmap_messenger = MmapCommunication()


        index = 0
        start = time.time()
        new_time = 0.0
        time.sleep(0.0001)

        def handle_quit(signal, frame):
            producer_write.close()
            if to_use_file:
                logfile.close()
            if share_data_over_lan:
                udp_messenger.producer.cleanup()
            mmap_messenger.cleanup()
            print("I'm killed gracefully")

        while True:
            try:
                current_time = time.time()
                elapsed = current_time - start
                old_time = new_time
                new_time = elapsed
                time_difference = new_time - old_time

                for idx, dataset in enumerate(range_data_array):
                    previous_distance_array[idx] = dataset.device_range.distance

                r.loop(range_data_array)

                for idx, dataset in enumerate(range_data_array):  # a distance of zero is dropped when the previous distance is also zero
                    if dataset.device_range.distance == 0 and previous_distance_array[idx] != 0:
                        dataset.num_of_dropped_zero += 1
                        raise continue_i

                for single_data in range_data_array:
                    single_data.elapsed_time = elapsed  # update time for OSC message
                    # EMA filter calculations
                    if type(single_data.device_range.distance) is int:
                        old_smoothed_range = single_data.smoothed_range
                        single_data.smoothed_range = (
                            (1 - alpha_pos) * single_data.smoothed_range
                            + alpha_pos * single_data.device_range.distance)
                        new_smoothed_range = single_data.smoothed_range
                        if not (time_difference == 0) and not (elapsed <= 0.001):
                            if single_data.velocity == "":
                                single_data.velocity = 0.0
                            measured_velocity = (new_smoothed_range - old_smoothed_range) / time_difference
                            single_data.velocity = (
                                (1 - alpha_vel) * single_data.velocity
                                + alpha_vel * measured_velocity)
                            if not smooth_velocity:
                                single_data.velocity = measured_velocity

                #Console.print_1d_ranging_output(
                    #index, elapsed, range_data_array, attributes_to_log)

                if to_use_file:
                    FileIO.write_range_data_to_file(
                        logfile, index, current_time, elapsed, time_difference, range_data_array, attributes_to_log)

                FileIO.write_range_data_to_file(
                        producer_write, index, current_time, elapsed, time_difference, range_data_array, attributes_to_log)

                if range_data_array[0].loop_status == POZYX_SUCCESS:
                    data_type = ([definitions.DATA_TYPE_RANGING, definitions.DATA_TYPE_MOTION_DATA] if attributes_to_log
                                 else [definitions.DATA_TYPE_RANGING])
                    if share_data_over_lan:
                        udp_messenger.send_message(elapsed, tags, range_data_array, data_type)
                    mmap_messenger.send_message(elapsed, tags, range_data_array, data_type)
                
                #Console.print_1d_output_from_csv(producer_read)

                index = index + 1
                
                signal.signal(signal.SIGTERM, handle_quit)
                signal.signal(signal.SIGINT, handle_quit)

            except ContinueI:
                continue


    finally:
        print("I'm done")