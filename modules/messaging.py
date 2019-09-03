import sys
sys.path.append(sys.path[0] + "/..")
from constants import definitions
from modules import udp
import os
import mmap
import array

class MessageBuilder():
    @staticmethod
    def add_range_data(data_for_tag, data_types):
        if definitions.DATA_TYPE_RANGING not in data_types:
            return [0] * 2
        range = data_for_tag.smoothed_range
        velocity = data_for_tag.velocity
        return [range, velocity]

    @staticmethod
    def add_position_data(data_for_tag, data_types):
        if definitions.DATA_TYPE_POSITIONING not in data_types:
            return [0] * 6
        pos_x = data_for_tag.smoothed_x
        pos_y = data_for_tag.smoothed_y
        pos_z = data_for_tag.smoothed_z

        #Kaela edit Jun 20th:
        if type(data_for_tag.velocity_x) == str:
            vel_x = 0.0
        else:
            vel_x = data_for_tag.velocity_x
        if type(data_for_tag.velocity_y) == str:
            vel_y = 0.0
        else:
            vel_y = data_for_tag.velocity_y
        if type(data_for_tag.velocity_z) == str:
            vel_z = 0.0
        else:
            vel_z = data_for_tag.velocity_z

        return [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]

    @staticmethod
    def add_motion_data(data_for_tag, data_types):
        if definitions.DATA_TYPE_MOTION_DATA not in data_types:
            return [0] * 23
        return [data_for_tag.sensor_data.pressure.value,
                data_for_tag.sensor_data.acceleration.x,
                data_for_tag.sensor_data.acceleration.y,
                data_for_tag.sensor_data.acceleration.z,
                data_for_tag.sensor_data.magnetic.x,
                data_for_tag.sensor_data.magnetic.y,
                data_for_tag.sensor_data.magnetic.z,
                data_for_tag.sensor_data.angular_vel.x,
                data_for_tag.sensor_data.angular_vel.y,
                data_for_tag.sensor_data.angular_vel.z,
                data_for_tag.sensor_data.euler_angles.heading,
                data_for_tag.sensor_data.euler_angles.roll,
                data_for_tag.sensor_data.euler_angles.pitch,
                data_for_tag.sensor_data.quaternion.w,
                data_for_tag.sensor_data.quaternion.x,
                data_for_tag.sensor_data.quaternion.y,
                data_for_tag.sensor_data.quaternion.z,
                data_for_tag.sensor_data.linear_acceleration.x,
                data_for_tag.sensor_data.linear_acceleration.y,
                data_for_tag.sensor_data.linear_acceleration.z,
                data_for_tag.sensor_data.gravity_vector.x,
                data_for_tag.sensor_data.gravity_vector.y,
                data_for_tag.sensor_data.gravity_vector.z]

class PozyxUDP:
    def __init__(self):
        self.producer = udp.Producer()

    def send_message(self, elapsed_time, tags, data_array, data_types):
        message_array = [elapsed_time]
        for idx, tag in enumerate(tags):
            message_array.append(tag)
            data_for_tag = data_array[idx]
            message_array = message_array + MessageBuilder.add_range_data(data_for_tag, data_types)
            message_array = message_array + MessageBuilder.add_position_data(data_for_tag, data_types)
            message_array = message_array + MessageBuilder.add_motion_data(data_for_tag, data_types)
        self.producer.send(message_array)


class MmapCommunication():
    def __init__(self):
        self.temp_file_name = definitions.MMAP_TEMP_FILE_NAME
        if not os.path.exists(self.temp_file_name):
            with open(self.temp_file_name, 'wb'):
                pass  # creates file if not existing

        self.f = open(self.temp_file_name, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), definitions.MMAP_LENGTH)  # memory-map the file
        self.previous_index_value = None

    def send_message(self, elapsed_time, tags, data_array, data_types):
        message_array = [elapsed_time]
        for idx, tag in enumerate(tags):
            message_array.append(tag)
            data_for_tag = data_array[idx]
            message_array = message_array + MessageBuilder.add_range_data(data_for_tag, data_types)
            message_array = message_array + MessageBuilder.add_position_data(data_for_tag, data_types)
            message_array = message_array + MessageBuilder.add_motion_data(data_for_tag, data_types)
        # the mmap reader strips all the Null bytes from the end of the padded message, so if your last
        # data point ends with a zero, it will be removed from the message, screwing it up. This line
        # adds a dummy [1] value to the end so that the message is never cut before that on read
        message_array = message_array + [1]
        self.send_array(message_array)

    def send_array(self, message_array):
        self.mm.seek(0)
        packed = array.array("d", message_array)
        # print(packed)
        self.mm.write(packed)

    def receive(self):
        self.mm.seek(0)
        raw = self.mm.read(definitions.MMAP_LENGTH)
        data = raw.rstrip(b"\x00") # remove trailing padding
        unpacked = array.array("d", data).tolist()
        if unpacked[0] != self.previous_index_value:
            self.previous_index_value = unpacked[0] # store index to avoid duplicate data
            return None, unpacked # returns None for address to match UDP.consumer.receive()
        return definitions.MMAP_NO_NEW_DATA_FLAG

    def cleanup(self):
        self.mm.close()
        self.f.close()
