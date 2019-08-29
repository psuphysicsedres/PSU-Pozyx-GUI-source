import os
import time
import subprocess
import sys

if __name__ == "__main__":
    filepath = os.path.expanduser('~') + "/Documents/PSUPozyx/Producer File/"
    producer_name = filepath + "producer_file.csv"
    #f = subprocess.Popen(['tail','-F', producer_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    f = open(producer_name, 'r', buffering=1)
    while True:
        line = f.readline().strip('\n')
        if line != "":
            print(line)
        else:
            continue
        
    
        
    

    
