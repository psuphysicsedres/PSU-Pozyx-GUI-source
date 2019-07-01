#!/usr/bin/env python
"""
The Pozyx ready to localize tutorial (c) Pozyx Labs

Modified by Gabriel Mukobi for use with the PSU Pozyx Configurator Graphical
User Interface and incorporating the sensor data and multitag localization
scripts. That is, this file smartly collects 3D position and optionally sensor
data at the same time for 1 or more remote devices based on the active settings
in the PSUPozyx GUI.

"""
import time
import os
import sys
from pypozyx import *
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
from modules.console_logging_functions import CondensedConsoleLogging as Console
from modules.configuration import Configuration as Configuration
from modules.file_writing import FileOpener
from modules.file_writing import PositioningFileWriting as FileIO
from modules.messaging import PozyxUDP, MmapCommunication
sys.path.append(sys.path[0] + "/..")
from constants import definitions

class PositionOutputContainer:
    def __init__(self, i_tag, i_position, i_num_of_ranges, i_num_of_error, i_smoothed_x, i_smoothed_y, i_smoothed_z,
                 i_sensor_data, i_loop_status):
        self.tag = i_tag
        self.position = i_position
        self.sensor_data = i_sensor_data
        self.num_of_ranges = i_num_of_ranges
        self.num_of_error = i_num_of_error
        self.loop_status = i_loop_status
        self.smoothed_x = i_smoothed_x
        self.smoothed_y = i_smoothed_y
        self.smoothed_z = i_smoothed_z
        self.velocity_x = ""
        self.velocity_y = ""
        self.velocity_z = ""


class Positioning(object):
    """Continuously performs multitag positioning"""
    def __init__(self, i_pozyx, i_tags, i_anchors, i_to_get_sensor_data,
                 i_algorithm=POZYX_POS_ALG_UWB_ONLY, i_dimension=POZYX_3D, i_height=1000):
        self.pozyx = i_pozyx
        self.tags = i_tags
        self.anchors = i_anchors
        self.algorithm = i_algorithm
        self.dimension = i_dimension
        self.height = i_height
        self.to_get_sensor_data = i_to_get_sensor_data

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        self.set_anchors_manual()

    def loop(self, loop_position_data_array):
        """Performs positioning and prints the results."""
        for idx, loop_tag in enumerate(self.tags):
            # get device position
            positioning_data = PositioningData(0b1000000000000001)
            loop_status = self.pozyx.doPositioningWithData(positioning_data, remote_id=loop_tag)

            # get motion data
            sensor_data = SensorData()
            calibration_status = SingleRegister()
            if self.to_get_sensor_data:
                sensor_data.data_format = 'IhhhhhhhhhhhhhhhhhhhhhhB'
                if loop_tag is not None or self.pozyx.checkForFlag(
                        POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS:
                    loop_status = self.pozyx.getAllSensorData(sensor_data, loop_tag)
                    loop_status &= self.pozyx.getCalibrationStatus(calibration_status, loop_tag)
            
            position = Coordinates()
            position.x = positioning_data.containers[0].x
            position.y = positioning_data.containers[0].y
            position.z = positioning_data.containers[0].z
            single = loop_position_data_array[idx]
            single.tag = loop_tag
            single.position = position
            single.sensor_data = sensor_data
            single.loop_status = loop_status
            single.num_of_ranges = positioning_data.containers[1].value

            if loop_status != POZYX_SUCCESS:
                single.num_of_error += 1
    

    def set_anchors_manual(self):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        for anchor_manual_tag in self.tags:
            status = self.pozyx.clearDevices(anchor_manual_tag)
            for anchor in self.anchors:
                status &= self.pozyx.addDevice(anchor, anchor_manual_tag)
            if len(anchors) > 4:
                status &= self.pozyx.setSelectionOfAnchors(
                    POZYX_ANCHOR_SEL_AUTO, len(anchors), remote_id=anchor_manual_tag)
            self.print_configuration_result(status, anchor_manual_tag)

    def print_configuration_result(self, status, tag_id):
        """Prints the configuration explicit result, prints and publishes error if one occurs"""
        if tag_id is None:
            tag_id = 0
        if status == POZYX_SUCCESS:
            print("Configuration of tag %s: success" % tag_id)
        else:
            self.print_error_code("configuration", tag_id)

    def print_error_code(self, operation, network_id):
        """Prints the Pozyx's error and possibly sends it as a OSC packet"""
        error_code = SingleRegister()
        status = self.pozyx.getErrorCode(error_code, None)
        if network_id is None:
            network_id = 0
        if status == POZYX_SUCCESS:
            print("Error %s on ID %s, error code %s" %
                  (operation, "0x%0.4x" % network_id, str(error_code)))
        else:
            # should only happen when not being able to communicate with a remote Pozyx.
            self.pozyx.getErrorCode(error_code)
            print("Error % s, local error code %s" % (operation, str(error_code)))


def apply_ema_filter(loop_position_data_array, loop_alpha_pos, loop_alpha_vel):
    #print("DEBUG: ema filter: enter.")
    for single_device_data in loop_position_data_array:
        # EMA filter calculations
        #print("DEBUG: ema filter: working on single_device_data")
        #print("DEBUG: ema filter: position.x type: {}".format(type(single_device_data.position.x)))
        if isinstance(single_device_data.position.x, int) or isinstance(single_device_data.position.x, float) :
            #print("DEBUG: ema filter: position.x is int or float")
            old_smoothed_x, old_smoothed_y, old_smoothed_z = (
                single_device_data.smoothed_x, single_device_data.smoothed_y, single_device_data.smoothed_z)

            single_device_data.smoothed_x = (
                (1 - loop_alpha_pos) * single_device_data.smoothed_x
                + loop_alpha_pos * single_device_data.position.x)
            new_smoothed_x = single_device_data.smoothed_x
            single_device_data.smoothed_y = (
                (1 - loop_alpha_pos) * single_device_data.smoothed_y
                + loop_alpha_pos * single_device_data.position.y)
            new_smoothed_y = single_device_data.smoothed_y
            single_device_data.smoothed_z = (
                (1 - loop_alpha_pos) * single_device_data.smoothed_z
                + loop_alpha_pos * single_device_data.position.z)
            new_smoothed_z = single_device_data.smoothed_z

            if not (time_difference == 0) and not (elapsed <= 0.001):
                if single_device_data.velocity_x == "":
                    single_device_data.velocity_x = 0.0
                    single_device_data.velocity_y = 0.0
                    single_device_data.velocity_z = 0.0
                measured_velocity_x = (new_smoothed_x - old_smoothed_x) / time_difference
                measured_velocity_y = (new_smoothed_y - old_smoothed_y) / time_difference
                measured_velocity_z = (new_smoothed_z - old_smoothed_z) / time_difference
                if not smooth_velocity:
                    #print("DEBUG: ema filter: smooth velocity disabled")
                    single_device_data.velocity_x = measured_velocity_x
                    single_device_data.velocity_y = measured_velocity_y
                    single_device_data.velocity_z = measured_velocity_z
                    continue
                # smooth velocity
                #print("DEBUG: ema filter: smoothing velocity")
                single_device_data.velocity_x = (
                    (1 - loop_alpha_vel) * single_device_data.velocity_x
                    + loop_alpha_vel * measured_velocity_x)
                single_device_data.velocity_y = (
                    (1 - loop_alpha_vel) * single_device_data.velocity_y
                    + loop_alpha_vel * measured_velocity_y)
                single_device_data.velocity_z = (
                    (1 - loop_alpha_vel) * single_device_data.velocity_z
                    + loop_alpha_vel * measured_velocity_z)


class ContinueI(Exception):
    pass


continue_i = ContinueI()


if __name__ == "__main__":
    # shortcut to not have to find out the port yourself
    serial_port = Configuration.get_correct_serial_port()

    # import properties from saved properties file
    config = Configuration.get_properties()
    tags = config.tags
    anchors = config.anchors
    attributes_to_log = config.attributes_to_log
    to_use_file = config.use_file
    filename = config.data_file
    to_get_sensor_data = not attributes_to_log == []
    alpha_pos = config.position_smooth
    alpha_vel = config.velocity_smooth
    smooth_velocity = alpha_vel < 1.00
    share_data_over_lan = config.share_data_over_lan

    tags 
    position_data_array = []
    for tag in tags:
        position_data_array.append(PositionOutputContainer(None, None, 0, 0, 0, 0, 0, None, None))
    if not tags:
        sys.exit("Please add at least one remote device for 1D ranging.")

    

    filepath = os.path.expanduser('~') + "/Documents/PSUPozyx/Producer File/"
    producer_name = filepath + "producer_file.csv"
    if os.path.exists(producer_name): #Kaela edit June 20
        os.remove(producer_name)  # remove old file so the program won't have to overwrite the old file which will slow it down
    producer_write = open(producer_name, 'w')
    FileIO.write_position_headers_to_file(producer_write, tags, attributes_to_log)

    pozyx = PozyxSerial(serial_port)
    r = Positioning(pozyx, tags, anchors, to_get_sensor_data)
    r.setup()

    if to_use_file:
        logfile = FileOpener.create_csv(filename)
        FileIO.write_position_headers_to_file(logfile, tags, attributes_to_log)

    # wait for motion data to work before running main loop
    if to_get_sensor_data:
        not_started = True
        while not_started:
            r.loop(position_data_array)
            not_started = position_data_array[0].sensor_data.pressure.value == 0
            for single_data in position_data_array:
                # Initialize EMA filter
                if type(single_data.position.x) is int:
                    single_data.smoothed_x = single_data.position.x
                    single_data.smoothed_y = single_data.position.y
                    single_data.smoothed_y = single_data.position.y

    udp_messenger = None
    mmap_messenger = None


    try:
        if share_data_over_lan:
            udp_messenger = PozyxUDP()
        mmap_messenger = MmapCommunication()

        index = 0
        start = time.time()
        new_time = 0.0
        time.sleep(0.00001)

        while True:
            try:
                current_time = time.time()
                elapsed = current_time - start
                old_time = new_time
                new_time = elapsed
                time_difference = new_time - old_time

                r.loop(position_data_array)
                for dataset in position_data_array:
                    if dataset.position.x == 0 and dataset.position.y == 0 and dataset.position.z == 0:
                        raise continue_i

                apply_ema_filter(position_data_array, alpha_pos, alpha_vel)

                #Console.print_3d_positioning_output(
                    #index, elapsed, position_data_array, attributes_to_log)    

                if to_use_file:
                    FileIO.write_position_data_to_file(
                        logfile, index, current_time, elapsed, time_difference, position_data_array, attributes_to_log)

                FileIO.write_position_data_to_file(producer_write, index, current_time, elapsed, time_difference,
                                                    position_data_array, attributes_to_log)

                if position_data_array[0].loop_status == POZYX_SUCCESS:
                    data_type = ([definitions.DATA_TYPE_POSITIONING, definitions.DATA_TYPE_MOTION_DATA] if attributes_to_log
                                 else [definitions.DATA_TYPE_POSITIONING])
                    if share_data_over_lan:
                        udp_messenger.send_message(elapsed, tags, position_data_array, data_type)
                    mmap_messenger.send_message(elapsed, tags, position_data_array, data_type)

                index = index + 1

            except ContinueI:
                continue

    except KeyboardInterrupt:
        pass

    finally:
        producer_write.close()
        if to_use_file:
            logfile.close()
        if share_data_over_lan:
            udp_messenger.producer.cleanup()
        mmap_messenger.cleanup()
