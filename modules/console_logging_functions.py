import time as time
from .data_functions import DataFunctions as DataFunctions
import sys
import os
sys.stdout.flush()

class CondensedConsoleLogging:
    @staticmethod
    def get_time():
        """
        Gets processor time

        :return float current_time: the current processor time
        """
        current_time = time.time()
        return current_time

    @staticmethod
    def get_elapsed_time(self, start_time):
        """
        Gets elapsed time since start_time

        :param self:
        :param float start_time: time to count from, set at program start
        :return float elapsed_time: time passed since start_time
        """
        elapsed_time = self.get_time() - start_time
        return elapsed_time

    @staticmethod
    def single_cycle_time_difference(previous_time, current_time):
        """
        Calculates the time it took to get to the current cycle

        :param float previous_time: the point of time of the previous cycle
        :param float current_time: the point of time of the current cycle
        :return:
            :time_difference: the difference in time between cycles
            :new_previous_time: used as previous_time in next cycle
        :rtype: float, float
        """
        time_difference = current_time - previous_time
        new_previous_time = current_time
        return time_difference, new_previous_time

    @staticmethod
    def build_timestamp(index, elapsed):
        output = str(index)
        output += " Time: "
        elapsed_time_str = DataFunctions.str_append_length(elapsed, 10)
        output += elapsed_time_str
        output += " Hz: "
        ave_hertz = DataFunctions.find_average_hertz(index, elapsed)
        ave_hertz_str = DataFunctions.str_append_length(ave_hertz, 5)
        output += ave_hertz_str
        return output

    @staticmethod
    def build_tag(single_device):
        return " | " + hex(single_device.tag)

    @staticmethod
    def build_range(single_device):
        output = " | Dist "
        output += DataFunctions.str_prepend_length(
            single_device.device_range.distance, 5)
        output += " | Smooth "
        output += DataFunctions.str_prepend_length(
            int(single_device.smoothed_range + 0.5), 5)
        output += " | Vel "
        try:
            output += DataFunctions.str_prepend_length(
                int(single_device.velocity + 0.5), 5)
        except TypeError:
            output += "     "
        return output

    @staticmethod
    def build_position(single_device):
        output = " | Pos "
        output += DataFunctions.str_prepend_length(
            single_device.position.x, 5) + " "
        output += DataFunctions.str_prepend_length(
            single_device.position.y, 5) + " "
        output += DataFunctions.str_prepend_length(
            single_device.position.z, 5)

        output += " | Smooth "
        output += DataFunctions.str_prepend_length(
            int(single_device.smoothed_x + 0.5), 5) + " "
        output += DataFunctions.str_prepend_length(
            int(single_device.smoothed_y + 0.5), 5) + " "
        output += DataFunctions.str_prepend_length(
            int(single_device.smoothed_z + 0.5), 5)

        output += " | Vel "
        try:
            output += DataFunctions.str_prepend_length(
                int(single_device.velocity_x + 0.5), 5) + " "
            output += DataFunctions.str_prepend_length(
                int(single_device.velocity_y + 0.5), 5) + " "
            output += DataFunctions.str_prepend_length(
                int(single_device.velocity_z + 0.5), 5)
        except TypeError:
            output += " " * 15
        return output

    @staticmethod
    def format_sensor_data(sensor_data, multiple_attributes_to_log):
        """
        :param sensor_data:
        :param multiple_attributes_to_log:
        :return: formatted data dictionary
        """
        # if the sensor data was returned as an error string
        try:
            data_dictionary = {}
            for attribute_to_log in multiple_attributes_to_log:
                line_of_data = []
                if attribute_to_log == "pressure":
                    attribute_to_log = "Press"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.pressure.value, 8))
                elif attribute_to_log == "acceleration":
                    attribute_to_log = "Acc"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.acceleration.x, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.acceleration.y, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.acceleration.z, 6))
                elif attribute_to_log == "magnetic":
                    attribute_to_log = "Mag"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.magnetic.x, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.magnetic.y, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.magnetic.z, 6))
                elif attribute_to_log == "angular velocity":
                    attribute_to_log = "Ang Vel"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.angular_vel.x, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.angular_vel.y, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.angular_vel.z, 6))
                elif attribute_to_log == "euler angles":
                    attribute_to_log = ""
                    line_of_data.append("Heading")
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.euler_angles.heading, 6))
                    line_of_data.append("Roll")
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.euler_angles.roll, 6))
                    line_of_data.append("Pitch")
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.euler_angles.pitch, 6))
                elif attribute_to_log == "quaternion":
                    attribute_to_log = "Quat"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.quaternion.x, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.quaternion.y, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.quaternion.z, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.quaternion.w, 6))
                elif attribute_to_log == "linear acceleration":
                    attribute_to_log = "Lin Acc"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.linear_acceleration.x, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.linear_acceleration.y, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.linear_acceleration.z, 6))
                elif attribute_to_log == "gravity":
                    attribute_to_log = "Grav"
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.gravity_vector.x, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.gravity_vector.y, 6))
                    line_of_data.append(DataFunctions.str_append_length(
                        sensor_data.gravity_vector.z, 6))
                data_dictionary[attribute_to_log.title()] = line_of_data
            return data_dictionary
        except AttributeError:
            return " Error in data"

    @staticmethod
    def build_sensor_data(single_device_data, attributes_to_log):
        """
        Builds motion data output for a tag
        """
        if not attributes_to_log:
            return ""

        motion_data = single_device_data.sensor_data
        data_dictionary = CondensedConsoleLogging.format_sensor_data(
            motion_data, attributes_to_log)
        output = ""
        if type(data_dictionary) == str:
            output += data_dictionary
        else:
            for key in data_dictionary:
                output += " | " + key
                for item in data_dictionary[key]:
                    output += " " + str(item)
        return output

    @staticmethod
    def print_1d_ranging_output(index, elapsed, ranging_loop_array, attributes_to_log):
        output = CondensedConsoleLogging.build_timestamp(index, elapsed)
        for single_device in ranging_loop_array:
            output += CondensedConsoleLogging.build_tag(single_device)
            output += CondensedConsoleLogging.build_sensor_data(
                single_device, attributes_to_log)
            output += CondensedConsoleLogging.build_range(single_device)    
            output += " | Num of Dropped Zero " + str(single_device.num_of_dropped_zero)  
            output += " | Num of Error " + str(single_device.num_of_error)              
        print(output, flush=True)

    @staticmethod
    def print_3d_positioning_output(index, elapsed, position_loop_array, attributes_to_log):
        output = CondensedConsoleLogging.build_timestamp(index, elapsed)
        for single_device in position_loop_array:
            output += CondensedConsoleLogging.build_tag(single_device)
            output += CondensedConsoleLogging.build_sensor_data(
                single_device, attributes_to_log)
            output += CondensedConsoleLogging.build_position(single_device)
            output += " | Num of Error " + str(single_device.num_of_error)   
            output += " | Num of Ranges " + str(single_device.num_of_ranges)         
        print(output, flush=True)

    @staticmethod
    def print_motion_data_output(index, elapsed, loop_array, attributes_to_log):
        output = CondensedConsoleLogging.build_timestamp(index, elapsed)
        for single_device in loop_array:
            output += CondensedConsoleLogging.build_tag(single_device)
            output += CondensedConsoleLogging.build_sensor_data(
                single_device, attributes_to_log)
        print(output, flush=True)

    @staticmethod
    def print_1d_output_from_csv(open_file):
        print(open_file.readline())

