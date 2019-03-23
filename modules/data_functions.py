class DataFunctions:
    @staticmethod
    def str_append_length(number, length):
        """
        Make a data value have a set character length.

        :param float number: the data point, probably a number, that you want to round
        :param int length: the length of characters you want the output to be
        :return: a string representation of the input number with set length
        :rtype: str

        This function takes a number and rounds it off/adds zeros to
        return a string of the number with a set character length.
        This is to make it easier to read the data from the console
        since every row will have the same number of data points.
        """
        num_string = str(number)
        # remove trailing .0
        if num_string[-2:] == ".0":
            num_string = num_string[:-2]
        # add spaces
        while len(num_string) < length:
            num_string += " "
        while len(num_string) > length:
            num_string = num_string[:-1]
        return num_string

    @staticmethod
    def str_prepend_length(number, length):
        """
        Make a data value have a set character length.

        :param int number: the data point, probably a number, that you want to round
        :param int length: the length of characters you want the output to be
        :return: a string representation of the input number with set length
        :rtype: str

        This function takes a number and adds zeros to the beginning
        as necessary to return a string of the number with a set
        character length. This is to make it easier to read the data
        from the console since every row will have the same number
        of data points.
        """
        num_string = str(number)
        # remove trailing .0
        if num_string[-2:] == ".0":
            num_string = num_string[:-2]
        # add decimal place if nonexistent
        if len(num_string) >= length:
            return num_string
        while len(num_string) < length:
            num_string = " " + num_string
        return num_string

    @staticmethod
    def convert_hertz(time_difference):
        """
        Finds the instantaneous frequency of the data in hertz

        :param float time_difference: the difference in time between two data points
        :return: instantaneous frequency in hertz
        :rtype: float

        The average hertz is calculated with the number of data points and the total time elapsed
        """
        try:
            hertz = 1 / time_difference
        except ZeroDivisionError:
            hertz = 0
        return hertz

    @staticmethod
    def find_average_hertz(index, elapsed):
        """
        Finds the average frequency of the data in hertz

        :param int index: the index of the data point
        :param float elapsed: the total elapsed time since function began
        :return: average frequency in hertz
        :rtype: float
        The average hertz is calculated with the number of data points and the total time elapsed
        """
        try:
            average_hertz = index / elapsed
        except ZeroDivisionError:
            average_hertz = 0
        return average_hertz
