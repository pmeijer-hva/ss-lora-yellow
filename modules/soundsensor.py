# this module reads the analog sound sensor from seeeds
# via an analog input port
# 2022 - Martin Vogel - HLSU martin.vogel@hslu.ch

import machine
import time

# global variables
queue = []          # queue to store the sound values
nbr_val = 10        # length of the queue
numberOfPeaks = 3   # To eliminate 0 values we take just the peaks to calculate the avg
periode = 1         # time in seconds between the sound measures


def mean(thelist: list) -> int:
# aid function to calculate the mean value of a list
    sum = 0
    for n in thelist:
        sum += n
    return(int(sum/len(thelist)))


def running_average(apin_soundsensor) -> int:
# calculates a running average in a queue
    global queue
    while len(queue) < nbr_val:     # only for the first values to fill it in
        queue.append(apin_soundsensor())
        time.sleep(0.1)             # capture the filling with this time periode
    queue.pop(0)                    # remove the oldest value
    queue.append(apin_soundsensor()) # add the newest value to the queue
    queue.sort()
    maxList = queue[-numberOfPeaks:]
    print(maxList)
    return mean(maxList)



if __name__ == "__main__":
    adc = machine.ADC()             # create an ADC object for the sound sensor
    apin_soundsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13
    while True:
        avg_sound = running_average(apin_soundsensor)
        print(avg_sound)
        time.sleep(periode)
