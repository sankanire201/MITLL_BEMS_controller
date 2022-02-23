import copy as cp
from collections import defaultdict
#import cvxpy
import numpy as np
from abc import ABC,abstractmethod
from scipy.optimize import minimize

class LoadShifting(ABC):
        @abstractmethod
        def get_schedule():
            pass
        def get_updated_schedule():
            pass
        def get_differableLoadAmount():
            pass
        def get_shiftedLoadAmount():
            pass        
        def set_threashhold(THRESHOLD):
            pass
        def set_schedule(schedule):
            pass
        def set_priority_list(PRIORITY_LIST):
            pass
        def __sort_priority_list(PRIORITY_LIST):
            pass
        def __calc_total_rated_consumption():
            pass
        def __calc_window_consumption(window):
            pass
        def __calc_window_threshold(window):
            pass
        def __shed_loads():
            pass
        def __shift_loads_scipy():
            pass
        def __objective_function(x0,CURRENT,THREAHHOLD):
            pass
        
class LoadShiftingGM(LoadShifting):
        def __init__(self,schedule,THRESHOLD,PRIORITY_LIST,RATED_LOAD_CONSUMPTION,WINDOW=[(0,23)]):
            self.__schedule=schedule
            self.__updatedSchedule=cp.deepcopy(schedule)
            self.__updatedTotalConsumption={}
            self.__hourlyPriorityGroups={}
            self.__THRESHOLD=THRESHOLD
            self.__totalConsumption={}
            self.__RATED_LOAD_CONSUMPTION=RATED_LOAD_CONSUMPTION
            self.__PRIORITY_LIST= self.__sort_priority_list(PRIORITY_LIST) 
            self.__differableLoadAmount=0
            self.__shiftedLoadAmount=0
            self.__WINDOW=WINDOW
            self.__calc_total_rated_consumption()
            self.__shed_loads()
            self.__shift_loads_scipy()
        def get_schedule(self):
            return(self.__schedule)
        def get_updated_schedule(self):
            return(self.__updatedSchedule)
        def get_differableLoadAmount(self):
            return(self.__differableLoadAmount)
        def get_shiftedLoadAmount(self):
            return(self.__shiftedLoadAmount)
        def set_threashhold(self,THRESHOLD):
            self.__THRESHOLD=THRESHOLD
        def set_schedule(self,schedule):
            self.__schedule=schedule
        def set_priority_list(PRIORITY_LIST):
            self.__PRIORITY_LIST= self.sortPriorityList(PRIORITY_LIST) 
        def __sort_priority_list(self,PRIORITY_LIST):
            priorityList=defaultdict(list)
            for i in PRIORITY_LIST:
                priorityList[PRIORITY_LIST[i]].append([i,self.__RATED_LOAD_CONSUMPTION[i]])
            return sorted(priorityList.items(),key=lambda kv:(kv[0],kv[1]),reverse=False)
        def __calc_total_rated_consumption(self):
            for i in self.__schedule:
                    self.__totalConsumption[i]=sum(self.__schedule[i].values())-self.__schedule[i]['UT']
        def __objective_function(self,x0,CURRENT,THREAHHOLD):
            val =np.sum(np.square(100*x0+CURRENT-THREAHHOLD))
            return val
        def __calc_window_consumption(self,window):
            current=[]
            for i in range(window[0],window[1]):
                current.append( self.__updatedTotalConsumption[i])
            return np.array(current)
        def __calc_window_threshold(self,window):
            Threshold=[]
            for i in range(window[0],window[1]):
                Threshold.append( self.__THRESHOLD[i])
            return np.array(Threshold)
        def __shed_loads(self):
            for i in self.__totalConsumption:
               penalty=self.__THRESHOLD[i]-self.__totalConsumption[i]
               if penalty <0 :
                    hourlySchedule=cp.deepcopy(self.__updatedSchedule[i])

                    for k in self.__PRIORITY_LIST:
                        for j in k[1]:
                            penalty=penalty+hourlySchedule[j[0]]
                            if penalty>0 and j[0]=='CT10':
                                self.__differableLoadAmount=-penalty+self.__differableLoadAmount+hourlySchedule[j[0]]
                                self.__updatedSchedule[i]['CT10']=penalty
                                break
                            if penalty <=0 and j[0]=='CT10':
                                self.__differableLoadAmount=hourlySchedule[j[0]]+self.__differableLoadAmount
                            self.__updatedSchedule[i][j[0]]=0
                            if penalty >0:
                                break
                            #self.__updatedSchedule[i][j[0]]=0                        
                        if penalty >=0:
                                break
               self.__updatedTotalConsumption[i]=sum(self.__updatedSchedule[i].values())-self.__updatedSchedule[i]['UT']
               #print(sum(self.__updatedSchedule[i].values())-prev,i,self.__differableLoadAmount,self.__totalConsumption[i])
               print(self.__updatedTotalConsumption[i],self.__totalConsumption[i],self.__differableLoadAmount)
        def __shift_loads_scipy(self):
            print('Shifting Loads')
            window=0
            current=[]
            threshold=[]
            consumption=self.__RATED_LOAD_CONSUMPTION['CT1']
            for i in self.__WINDOW:
                window=abs(i[0]-i[1])
                current=self.__calc_window_consumption(i)
                threshold=self.__calc_window_threshold(i)
            print(current,'current')
            cons1 = {'type': 'ineq', 'fun': lambda x:  -np.sum(consumption*x)+self.__differableLoadAmount}
            cons2 = {'type': 'ineq', 'fun': lambda x:  -x*consumption-current+threshold}
            bnds = []
            for k in range(0,window):
                bnds.append((0,1))
            x0=np.zeros(window)
            sol = minimize(self.__objective_function,x0,args=(current,threshold),method='SLSQP',bounds=bnds,constraints=[cons1,cons2])
            for i in self.__WINDOW:
                k=0
                for p in range(i[0],i[1]):
                    self.__updatedSchedule[p]['CT10']=self.__updatedSchedule[p]['CT10']+consumption*sol.x[k]
                    k=k+1
            self.__shiftedLoadAmount=np.sum(consumption*sol.x)
            print(self.__shiftedLoadAmount,self.__differableLoadAmount,'After',self.__updatedSchedule)
            return self.__updatedSchedule
