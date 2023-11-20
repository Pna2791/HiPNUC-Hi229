#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' For hipnuc module '
import sys
#this specify path of pyserial
#sys.path.append("/usr/lib/python3/dist-packages")
import threading
import serial
import json
from queue import Queue
from hipnuc_protocol import *
import time
import os

# 用於測試
import binascii

class hipnuc_module(object):
    def __init__(self, port, baud, path_configjson=None):

        def serialthread():
            while self.serthread_alive:
                # If the serial port has data, it is received into the buffer
                if self.serial.in_waiting:
                    # 讀取序列埠
                    data = self.serial.read(self.serial.in_waiting)
                    # 放至緩衝區
                    self.binbuffer.extend(data)
                else:
                    pass

                # 解析緩衝區數據
                try:
                    while True:
                        #嘗試查找完整幀,若失敗會拋出異常
                        headerpos, endpos = intercept_one_complete_frame(self.binbuffer)
                        #解析完整幀
                        extraction_information_from_frame(self.binbuffer[headerpos :endpos + 1],self.module_data_fifo,self.config["report_datatype"])
                        self.binbuffer = self.binbuffer[endpos + 1:]

                except HipnucFrame_NotCompleted_Exception as NotCompleted:
                    #接收進行中
                    pass
                except HipnucFrame_ErrorFrame_Exception as e:
                    print(e)
                    #目前幀有幀頭，但是為錯誤幀，跳過錯誤幀
                    headerpos = find_frameheader(self.binbuffer)
                    self.binbuffer = self.binbuffer[headerpos + 1:]
                # finally:
                #     pass
                
                #max achieve 1000Hz
                time.sleep(0.001)

        # config
        if path_configjson != None:
            # read json file
            config_json = open(path_configjson, 'r', encoding='utf-8')
            self.config = json.load(config_json)
            # Close file
            config_json.close()
        else:
            pass

        # 初始化序列埠
        # 打開序列埠，並得到序列埠對像
        self.serial = serial.Serial(port, baud, timeout=None)
        # FIFO
        self.module_data_fifo = Queue()

        self.binbuffer = []

        self.serthread_alive = True
        self.serthread = threading.Thread(target=serialthread)
        self.serthread.start()

        self.sample_timer = None
        self.sample_timer = threading.Timer(1.00, sample_rate_timer_cb, args=(self.sample_timer,))
        self.sample_timer.start()

        self.frame_counter=0
        self.csv_timestamp=0

    def get_module_data(self, timeout=None):
        data = self.module_data_fifo.get(block=True, timeout=timeout)
        return data

    def get_module_data_size(self):
        return self.module_data_fifo.qsize()

    def close(self):
        self.serthread_alive = False
        sample_rate_timer_close()
        self.serial.close()

    def create_csv(self, filename="chlog.csv"):
        self.frame_counter=0
        
        if os.path.exists(filename):
            os.remove(filename)
        f = open(filename,'w')
        print ('%s is created(overwited).'%(filename))

        f.close()

    def write2csv(self, data, filename="chlog.csv"):
     
        f = open(filename,'a')

        if self.frame_counter==0:
            csv_row_name="frame,"
            for key, data_list in data.items():
                for axis_dic in data_list:
                        for axis, value in axis_dic.items():
                            
                            csv_row_name+=key+axis+','
            csv_row_name+='\n'
            f.write(csv_row_name)
            self.frame_counter+=1
        
        
        csv_row_value="%d,"%(self.frame_counter)
        for data_list in data.values():
            for axis_dic in data_list:
                for axis, value in axis_dic.items():
                    csv_row_value+=str(value)+','

        csv_row_value+='\n'
        
        f.write(csv_row_value)
        f.close()
        self.frame_counter+=1

        #print ('writed %s:%d'%(filename,self.frame_counter))


            