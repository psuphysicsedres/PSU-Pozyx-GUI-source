import os
import random
import sys
import time
import numpy as np
from socket import gethostbyname, gethostname

import pyqtgraph as pg
from PyQt5 import QtGui
from pyqtgraph.Qt import QtCore

import _thread
from constants import definitions
from modules import udp
from modules.configuration import Configuration as Configuration
from modules.file_writing import FileOpener
from modules.messaging import MmapCommunication

# global config variables
data_address = "/pozyx"
(ip, network_code) = ("127.0.0.1", 8888)
max_data_length = 200

my_local_ip_address = gethostbyname(gethostname())


class DataHandler:
    def __init__(self):
        self.x_axis = "TimeElapsed"
        self.y_axis = "Index"
        self.transform = "None"
        self.transform_on = False
        self.center_tag = "0x6000"
        self.outer_tag = "0x6000"
        self.x_data = []
        self.y_data = []
        self.export_data = []
        self.header = {}
        self.maxLen = max_data_length
        self.use_lan_data = False
        if self.use_lan_data:
            self.consumer = udp.Consumer()
        else:
            self.consumer = MmapCommunication()
        #self.tag_idx = 1
        #self.to_check_tag_idx = False

    def set_use_lan_data(self, new_value):
        self.use_lan_data = new_value
        if self.use_lan_data:
            self.consumer = udp.Consumer()
        else:
            self.consumer = MmapCommunication()

    def clear_data(self):
        self.x_data = []
        self.y_data = []
        
    def change_x_axis(self, x_axis_in):
        self.x_axis = x_axis_in

    def change_y_axis(self, y_axis_in):
        self.y_axis = y_axis_in

    def change_transform(self, transform_in):
        self.transform = transform_in

    def change_center_tag(self, center_tag_in):
        self.center_tag = center_tag_in

    def change_outer_tag(self, outer_tag_in):
        self.outer_tag = outer_tag_in
        #self.to_check_tag_idx = True

    def change_max_data_len(self, len_in):
        self.maxLen = len_in

    '''
    def extract_data(self, new_data):
        message = new_data[1]
        if self.to_check_tag_idx:
            try:
                self.tag_idx = message.index(int(self.tag, 16))
                #self.clear_data()
            except Exception as e:
                print("Error, " + self.tag + " has no data. Defaulting to first tag.")
                self.tag_idx = 1
            self.to_check_tag_idx = False  # done checking

        x_index = definitions.OSC_INDEX_DICT[self.x_axis] + self.tag_idx
        if self.x_axis == "Time":
            x_index = 0
        y_index = definitions.OSC_INDEX_DICT[self.y_axis] + self.tag_idx
        if self.y_axis == "Time":
            y_index = 0

        x = message[x_index]
        try:
            y = message[y_index]
        except IndexError:
            pass
        print(new_data[1])
        return x, y
    '''
    def extract_data(self, new_data):
        try:
            data_array = []
            for i in new_data.split(','):
                float_data = float(i)
                data_array.append(float_data)
            self.export_data.append(data_array)
            print(data_array)

            x_index = header[self.x_axis]
            y_index = header[self.y_axis]
            x = data_array[x_index]
            y = data_array[y_index]
            return x, y

        except (ValueError, UnboundLocalError, IndexError, TypeError):
            pass


    def add(self, x, y):
        if len(self.x_data) == len(self.y_data):
            self.x_data.append(x)
            self.y_data.append(y)
        else:
            pass
        number_x_over = len(self.x_data) - self.maxLen
        if number_x_over > 0:
            self.x_data = self.x_data[number_x_over:]
        number_y_over = len(self.y_data) - self.maxLen
        if number_y_over > 0:
            self.y_data = self.y_data[number_y_over:]

    def deal_with_data(self, new_data):
        data_array = []
        for i in new_data.split(','):
            if i != '\n':
                float_data = float(i)
                data_array.append(float_data)
            else:
                break
        self.export_data.append(data_array)
        #print(data_array)

        x_index = self.header[self.x_axis]
        y_index = self.header[self.y_axis]

        x = data_array[x_index]
        y = data_array[y_index]


        if self.transform == "None":       
            self.add(x, y)

        if self.transform == "Earth Center":
            try:
                xc_index = self.header[self.center_tag + " Measured-X"]
                yc_index = self.header[self.center_tag + " Measured-Y"]
                xo_index = self.header[self.outer_tag + " Measured-X"]
                yo_index = self.header[self.outer_tag + " Measured-Y"]

                xc = data_array[xc_index]
                yc = data_array[yc_index]
                xo = data_array[xo_index]
                yo = data_array[yo_index]

                transform_x = xo - xc
                transform_y = yo - yc

                self.add(transform_x, transform_y)

            except(KeyError):
                print("Current Earth or observed tag name invalid")
                pass
            
        if self.transform == "Angle":
                        
            time_index = self.header["TimeElapsed"]
            t = data_array[time_index]
            
            angle = np.arctan2(y,x)
            self.add(angle,t)

        if self.transform == "Angular Earth Center":
            
            time_index = self.header["TimeElapsed"]
            t = data_array[time_index]
            
            try:
                xc_index = self.header[self.center_tag + " Measured-X"]
                yc_index = self.header[self.center_tag + " Measured-Y"]
                xo_index = self.header[self.outer_tag + " Measured-X"]
                yo_index = self.header[self.outer_tag + " Measured-Y"]

                xc = data_array[xc_index]
                yc = data_array[yc_index]
                xo = data_array[xo_index]
                yo = data_array[yo_index]

                transform_x = xo - xc
                transform_y = yo - yc

                angle = np.arctan2(transform_y,transform_x)
                self.add(angle,t)

            except(KeyError):
                print("Current Earth or observed tag name invalid")
                pass
            
    def extract_header(self, header_string):
        index = 0
        header_name = header_string.split(',')
        for entry in header_name:
            self.header[entry] = index
            index += 1
        print(self.header)

    def start_running(self, *args):
        #config = Configuration.get_properties()
        #attributes_to_log = config.attributes_to_log
        #new_data = self.consumer.receive() # take the first outlier data out of the loop so it won't make the graph looks weird
        #while True:
            #new_data = self.consumer.receive()
            #if new_data is None:
            #    time.sleep(0.04)
            #    continue
            #elif new_data == definitions.MMAP_NO_NEW_DATA_FLAG:
            #    time.sleep(0.007) # wait a lot less since MMAP so fast
            #    continue
            #self.add_export_data(new_data)
            #self.deal_with_data(new_data)
        filepath = os.path.expanduser('~') + "/Documents/PSUPozyx/Producer File/"
        producer_name = filepath + "producer_file.csv"
        producer_read = open(producer_name, 'r')  
        header_string = producer_read.readline()   # read the first line of the producer file, which should be the header
        self.extract_header(header_string)    # separate the header using comma delimiter to form a dictionary of headers and a corresponding index. This is
                                              # use to organize the axis names
        while True:
            new_data = producer_read.readline()   
            #if new_data == "" or new_data == "Index,Time,Difference,Hz,AveHz,0x604e Range,0x604e Smoothed Range,0x604e Velocity,0x604e Num-of-Dropped-Zero,0x604e Num-of-Error,":
                #next_new_data = producer_read.readline()
                #if next_new_data == "":
                    #time.sleep(0.5)
                    #continue
                #else:
                 #   self.deal_with_data(next_new_data)
            #else:
             #   self.deal_with_data(new_data)
            try:
                self.deal_with_data(new_data)
            except (ValueError, TypeError):
                time.sleep(0.001)
                continue
            

    def get_data(self):
        return self.x_data, self.y_data

    def add_export_data(self, new_data):
        self.export_data.append(new_data[1])

    
    def get_export_data(self):
        return self.export_data
    

if __name__ == "__main__":
    arguments = sys.argv
    arg_length = len(arguments)
    '''
    possible_data_types = [
        "Time",
        "1D Range","1D Velocity",
        "3D Position X", "3D Position Y", "3D Position Z",
        "3D Velocity X", "3D Velocity Y", "3D Velocity Z",
        "Pressure",
        "Acceleration X", "Acceleration Y", "Acceleration Z",
        "Magnetic X", "Magnetic Y", "Magnetic Z",
        "Angular Vel X", "Angular Vel Y", "Angular Vel Z",
        "Euler Heading", "Euler Roll", "Euler Pitch",
        "Quaternion W","Quaternion X", "Quaternion Y", "Quaternion Z",
        "Lin Acc X", "Lin Acc Y", "Lin Acc Z",
        "Gravity X", "Gravity Y", "Gravity Z"]
    '''

    data_handler = DataHandler()

    data_thread = _thread.start_new_thread(data_handler.start_running, ())

    time.sleep(0.01)
    axis_names = []
    for key in data_handler.header.keys():
        axis_names.append(str(key))
    possible_data_types = axis_names

    possible_transform_types = ["None", "Earth Center", "Angle", "Angular Earth Center"]

    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('useOpenGL', True)
    pg.setConfigOption('crashWarning', True)
    pg.setConfigOption('antialias', False)

    app = QtGui.QApplication([])
    pw = pg.PlotWidget()

    pw.showGrid(x=True, y=True)
    #pw.setAutoPan(x=True)
    #pw.setDownsampling(ds=80)

    w = QtGui.QWidget()

    pause_button = QtGui.QPushButton("Pause")
    export_button = QtGui.QPushButton("Export")

    x_label = QtGui.QLabel("X-axis:")
    x_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    x_dropdown = pg.ComboBox(items=possible_data_types)
    x_dropdown.setValue("TimeElapsed")
    y_label = QtGui.QLabel("Y-axis:")
    y_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    y_dropdown = pg.ComboBox(items=possible_data_types)
    y_dropdown.setValue("Index")

    transform_label = QtGui.QLabel("Transform")
    transform_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    #transform_dropdown = pg.ComboBox(items=possible_transform_types)
    transform_dropdown = QtGui.QComboBox()
    transform_dropdown.addItems(possible_transform_types)
    #transform_dropdown.setValue("None")
    #transform_dropdown.setFlags(QtCore.Qt.ItemIsUserCheckable | Qt.Core.Qt.ItemIsEnabled)
    #transform_dropdown.setCheckState(QtCore.Qt.Unchecked)

    center_tag_label = QtGui.QLabel("Earth Tag:")
    center_tag_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    center_tag_input= QtGui.QLineEdit()
    center_tag_input.setText("0x6000")
    center_tag_input.setMaxLength(6)

    data_point_label = QtGui.QLabel("Points:")
    data_point_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    data_point_spin = pg.SpinBox(value=100, bounds=(2, 5000), step=1.0, dec=True, int=True)

    outer_tag_label = QtGui.QLabel("Observed Tag:")
    outer_tag_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    outer_tag_input = QtGui.QLineEdit()
    outer_tag_input.setText("0x6000")
    outer_tag_input.setMaxLength(6)

    clear_data_button = QtGui.QPushButton("Clear Window")

    color_label = QtGui.QLabel("Color:")
    color_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    colors = ["g", "r", "c", "m", "b", "k"]
    color_dropdown = pg.ComboBox(items=["Black", "Green", "Red", "Cyan", "Magenta", "Blue"])
    color_dropdown.setValue("Black")

    lan_data_checkbox = QtGui.QCheckBox("LAN Data")

    layout = QtGui.QGridLayout()
    w.setLayout(layout)

    # row 1
    layout.addWidget(pause_button,      0, 0, 1, 2)
    layout.addWidget(x_label,           0, 2, 1, 1)
    layout.addWidget(x_dropdown,        0, 3, 1, 2)
    layout.addWidget(color_label,       0, 5, 1, 1)
    layout.addWidget(color_dropdown,    0, 6, 1, 1)
    layout.addWidget(data_point_label,  0, 7, 1, 1)
    layout.addWidget(data_point_spin,   0, 8, 1, 2)
    layout.addWidget(export_button,     0, 11, 1, 1)
    # row 2
    layout.addWidget(clear_data_button, 1, 0, 1, 2)
    layout.addWidget(y_label,           1, 2, 1, 1)
    layout.addWidget(y_dropdown,        1, 3, 1, 2)
    layout.addWidget(transform_label,   1, 5, 1, 1)
    layout.addWidget(transform_dropdown,1, 6, 1, 1)
    layout.addWidget(lan_data_checkbox, 1, 7, 1, 2, QtCore.Qt.AlignCenter)
    # row 3
    layout.addWidget(center_tag_label,    2, 5, 1, 1)
    layout.addWidget(center_tag_input,    2, 6, 1, 1)
    layout.addWidget(outer_tag_label,             2, 7, 1, 1)
    layout.addWidget(outer_tag_input,             2, 8, 1, 2)
    #row 4
    layout.addWidget(pw,                3, 0, 1, 10)

    for i in range(0, 10):
        layout.setColumnStretch(i, 1)

    w.show()

    connect = []
    pen = pg.mkPen('k', width=2)
    symbolpen = pg.mkPen('k')
    curve = pw.plot(connect="finite", pen=pen, symbol='o', symbolPen=symbolpen)

    graphing_paused = False

    def update():
        if graphing_paused:
            return
        try:
            #connect.append(0)
            x, y = data_handler.get_data()
            # print(x)
            curve.setData(x, y)
            QtGui.QApplication.processEvents()
        except Exception as e:
            print(e)

    def change_x_axis(ind):
        data_handler.clear_data()
        print("Change x-axis to: " + x_dropdown.value())
        data_handler.change_x_axis(x_dropdown.value())

    def change_y_axis(ind):
        data_handler.clear_data()
        print("Change y-axis to: " + y_dropdown.value())
        data_handler.change_y_axis(y_dropdown.value())

    def change_transform(ind):
        data_handler.clear_data()
        print("Change transform to: " + transform_dropdown.currentText())
        data_handler.change_transform(transform_dropdown.currentText())
        if transform_dropdown.currentText() == "None":
            data_handler.transform_on = False
        elif transform_dropdown.currentText() == "Angle":
            data_handler.transform_on = False
        else:
            data_handler.transform_on = True
            print("Earth tag: " + data_handler.center_tag)

    def change_center_tag(item):
        new_center_tag = center_tag_input.text()
        try:
            int(new_center_tag, 16)
        except ValueError as e:
            print(new_center_tag + " is not a valid hexadecimal tag name.")
            return
        print("Change Earth tag to: " + new_center_tag)
        data_handler.change_center_tag(new_center_tag)

    def change_data_length(item):
        print("Change num data points to: " + str(item.value()))
        data_handler.change_max_data_len(int(item.value()))
        
    def change_outer_tag(item):
        new_outer_tag = outer_tag_input.text()
        try:
            int(new_outer_tag, 16)
        except ValueError as e:
            print(new_outer_tag + " is not a valid hexadecimal tag name.")
            return
        print("Change observed tag to: " + new_outer_tag)
        data_handler.change_outer_tag(new_outer_tag)

    def pause_handler(ind):
        global graphing_paused
        graphing_paused = not graphing_paused
        print("Graphing", "paused." if graphing_paused else "resumed.")

    def clear_data_handler(ind):
        data_handler.clear_data()
        print("Cleared data")

    def lan_data_handler(ind):
        check_state = bool(lan_data_checkbox.checkState())
        print("Toggling the use of LAN data. This affects whether or not you receive "
              "data to graph from other systems collecting data on the local network.")
        data_handler.set_use_lan_data(check_state)

    def color_handler(ind):
        global curve
        new_color = color_dropdown.value()
        print("Change color to: " + new_color)
        color_char = new_color[0].lower()
        if new_color == "Black":
            color_char = "k"
        curve.setPen(color_char, width=2)
        curve.setSymbolPen(color_char)
    
    def export_handler(ind):
        start_value = pw.viewRange()[0][0]
        end_value = pw.viewRange()[0][1]
        data = data_handler.get_export_data()  
        starting_index = 0
        ending_index = 0
        header_index = data_handler.header[x_dropdown.value()]
        for index, data_array in enumerate(data):
            value = data_array[header_index]
            if value > start_value or value == start_value:
                starting_index = int(data_array[0])
                print("got min x = " + str(starting_index))
                continue_index = index
                break

        for idx, data_array in enumerate(data):
            value = data_array[header_index]
            print(value)
            if value > end_value or value == end_value:
                ending_index = int(data_array[0])
                print("got max x = " + str(ending_index))
                break
                

        filepath = os.path.expanduser('~') + "/Documents/PSUPozyx/Data/"
        filename = filepath + "chopped_data.csv"
        logfile = FileOpener.create_csv(filename)
        header = ""
        for header_name in possible_data_types:
            header += header_name + ","
        header += "\n"
        logfile.write(header)
        output = ""
        for idx in range(starting_index, ending_index):
            for single_data in data[idx]:
                output += str(single_data) + ","
            output += "\n"
        logfile.write(output)
        logfile.close()


    x_dropdown.currentIndexChanged.connect(change_x_axis)
    y_dropdown.currentIndexChanged.connect(change_y_axis)
    transform_dropdown.currentIndexChanged.connect(change_transform)
    center_tag_input.textEdited.connect(change_center_tag)
    data_point_spin.sigValueChanged.connect(change_data_length)
    outer_tag_input.textEdited.connect(change_outer_tag)
    pause_button.clicked.connect(pause_handler)
    clear_data_button.clicked.connect(clear_data_handler)
    lan_data_checkbox.clicked.connect(lan_data_handler)
    color_dropdown.currentIndexChanged.connect(color_handler)
    export_button.clicked.connect(export_handler)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(40)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()

    data_handler.consumer.cleanup()

    app.closeAllWindows()

    _thread.exit_thread()
