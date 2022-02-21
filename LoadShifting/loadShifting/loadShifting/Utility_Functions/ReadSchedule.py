import csv
import sys
from csv import DictReader, DictWriter
import os
from json import load
import copy as cp
from abc import ABC,abstractmethod

class Readschedule(ABC):
    @abstractmethod
    def read_rated_consumption():
        pass
    def get_schedule_rated_consumption(self):
        pass
    def get_schedule_states(self):
        pass
    def get_priority_list(self):
        pass

    
class ReadScheduleCSV(Readschedule):
    def __init__(self,CSV_PATH,LOADS):
        self.__CSV_PATH=CSV_PATH
        self.__LOADS = LOADS
        self.__scheduleRatedConsumption={}
        self.__scheduleStates={}
        self.__prioritylist={}      
    def get_schedule_rated_consumption(self):
        return self.__scheduleRatedConsumption
    def get_schedule_states(self):
        return self.__scheduleStates
    def get_priority_list(self):
        return self.__prioritylist    
    def read_rated_consumption(self):
        if os.path.isfile(self.__CSV_PATH):
            with open(self.__CSV_PATH, "r") as csvDevice:
                self.csvReader = DictReader(csvDevice)
                for point in self.csvReader:
                    tempRow={}
                    for i in point:
                        if i in self.__LOADS:
                            tempRow[i]=float(self.__LOADS[i])*float(point[i])                 
                    self.__scheduleRatedConsumption[int(point.get('Time'))]=tempRow
        else:
            raise RuntimeError("CSV device at {} does not exist".format(self.__CSV_PATH))
        return self.__scheduleRatedConsumption
        
 