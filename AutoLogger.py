# resumes gracefully from sleep

from PCANBasic import *
import time
import os
import msvcrt
import datetime

os.add_dll_directory(os.getcwd())

# constants
channel = PCAN_USBBUS1
baud = PCAN_BAUD_500K
heartbeat_timeout = 15  # seconds
tic_sleep_period = .001

# log log file
log_log_file = open("logs.txt", "a")

# init pcan
pcan = PCANBasic()

status = pcan.Initialize(channel, baud)
if (status != PCAN_ERROR_OK):
    print("Error initializing CAN dongle")
    exit()
else:
    print("Successfully initialized CAN dongle. Waiting for heartbeats...")

pcan.Reset(channel)
pcan.SetValue(channel, PCAN_TRACE_CONFIGURE, TRACE_FILE_SEGMENTED | TRACE_FILE_DATE | TRACE_FILE_TIME)
pcan.SetValue(channel, PCAN_TRACE_SIZE, 100)


logging_active = False
def start_logging():
    log_log_file.write("\nStarted Logging: " + str(datetime.datetime.now()) + ", ")
    log_log_file.flush()

    pcan.SetValue(channel, PCAN_TRACE_STATUS, PCAN_PARAMETER_ON)
    global logging_active
    logging_active = True

def stop_logging():
    log_log_file.write("Stopped Logging: " + str(datetime.datetime.now()))
    log_log_file.flush()

    pcan.SetValue(channel, PCAN_TRACE_STATUS, PCAN_PARAMETER_OFF)
    global logging_active
    logging_active = False


heartbeat_timer = heartbeat_timeout

while (True):

    time.sleep(tic_sleep_period)
    read_result = pcan.Read(channel)
    msg = read_result[1]

    heartbeat_found_flag = False

    # if (msvcrt.kbhit()):
    #     msvcrt.getch()
    #     heartbeat_found_flag = True

    if(msg.MSGTYPE == PCAN_MESSAGE_STANDARD.value):
        # got a good message
        if(msg.ID == 0x729):
            # got a heartbeat
            heartbeat_timer = heartbeat_timeout  # reset heartbeat timer
            heartbeat_found_flag = True

    if (heartbeat_found_flag):
        if (not logging_active):
            print("Detected Heartbeat. Starting Log...\t\t\t\tCurrent Time: " + str(datetime.datetime.now()))
            start_logging()
    elif (logging_active):
        heartbeat_timer -= tic_sleep_period

    if (heartbeat_timer <= 0 and logging_active):
        print("Lost Heatbeat. Stopping Log")
        stop_logging()