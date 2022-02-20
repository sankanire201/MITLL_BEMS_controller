"""
Agent documentation goes here.
"""
__docformat__ = 'reStructuredText'

import logging
import sys
#import volttron
from volttron.platform.agent import utils
from volttron.platform.agent.utils import get_platform_instance_name
from volttron.platform.vip.agent import Agent, Core, RPC
sys.path.insert(0, '/home/pi/volttron/LoadShifting/loadShifting/Utility_Functions')
sys.path.insert(0, '/home/pi/volttron/LoadShifting/loadShifting/Core_Functions')
import ReadSchedule as r
import LoadShifting as LS
import netifaces as ni
import csv
import os
from csv import DictReader, DictWriter
_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def loadShifting(config_path, **kwargs):
    """
    Parses the Agent configuration and returns an instance of
    the agent created using that configuration.

    :param config_path: Path to a configuration file.
    :type config_path: str
    :returns: Loadshifting
    :rtype: Loadshifting
    """
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    setting1 = int(config.get('setting1', 1))
    setting2 = config.get('setting2', "some/random/topic")

    return Loadshifting(setting1, setting2, **kwargs)


class Loadshifting(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, setting1=1, setting2="some/random/topic", **kwargs):
        super(Loadshifting, self).__init__(**kwargs)
        _log.debug("vip_identity: " + self.core.identity)

        self.setting1 = setting1
        self.setting2 = setting2

        self.default_config = {"setting1": setting1,
                               "setting2": setting2}

        # Set a default configuration to ensure that self.configure is called immediately to setup
        # the agent.
        self.hour=0
        self.Sn_kVA=0
        self.Pn_kW=0
        self.Building_type=''
        self.instancename=get_platform_instance_name()
        ni.ifaddresses('wlan0')
        self.ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
        # Hook self.configure up to changes to the configuration file "config".
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")
        
        csvpath='/home/pi/volttron/LoadShifting/Loads.csv'
        profilepath='/home/pi/volttron/LoadShifting/Prof_P_csv.csv'
        if os.path.isfile(csvpath):
            with open(csvpath, "r") as csv_device:
                 pass
                 reader = DictReader(csv_device)        
         #iterate over the line of the csv
                 for point in reader:
                     ##Rading the lines for configuration parameters
                    Type = point.get("Type")
                    Sn_kVA = point.get("Sn_kVA")
                    PF = point.get("PF")
                    Pn_kW= point.get("Pn_kW")
                    IP= point.get("IP")
                    Instance_name = point.get("Instance_name")
                    profile = point.get("Profile")
                    
                    if Instance_name==self.instancename:
                        self.Sn_kVA=int(Sn_kVA)
                        self.Pn_kW=int(Pn_kW)
                        self.Building_type=Type
                        profilepath='/home/pi/volttron/LoadShifting/'+profile
                    print(profilepath)
                   
        else:
            # Device hasn't been created, or the path to this device is incorrect
            raise RuntimeError("CSV device at {} does not exist".format(csv_path))
        LOADS={'CT1':Pn_kW, 'CT2':Pn_kW, 'CT3':Pn_kW, 'CT4':Pn_kW, 'CT5':Pn_kW, 'CT6':Pn_kW, 'CT7':Pn_kW, 'CT8':Pn_kW, 'CT9':Pn_kW, 'CT10':Pn_kW,'UT':2000}
        PRIORITY_LIST={'CT1':1, 'CT2':2, 'CT3':2, 'CT4':1, 'CT5':1, 'CT6':6, 'CT7':7, 'CT8':8, 'CT9':9, 'CT10':0,'UT':1000}
        THRESHOLD={0:25,1:22,2:22,3:22,4:23,5:24,6:25,7:26,8:27,9:28,10:22,11:22,12:25,13:23,14:14,15:15,16:21,17:17,18:18,19:22,20:22,21:22,22:23,23:24}
        WINDOW=[(11,17)]
            
        schedule=r.ReadScheduleCSV(profilepath,LOADS)
        self.schedule=schedule.read_rated_consumption()
        loadshifter=LS.LoadShiftingGM(self.schedule,THRESHOLD,PRIORITY_LIST,LOADS,WINDOW)
        self.updatedSchedule=loadshifter.get_updated_schedule()
        self.core.periodic(5,self.dowork)

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        _log.debug("Configuring Agent")

        try:
            setting1 = int(config["setting1"])
            setting2 = config["setting2"]
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))
            return

        self.setting1 = setting1
        self.setting2 = setting2
        for x in self.setting2:
            self._create_subscriptions(str(x))
            print(str(x))
    def _create_subscriptions(self, topic):
        """
        Unsubscribe from all pub/sub topics and create a subscription to a topic in the configuration which triggers
        the _handle_publish callback
        """
        self.vip.pubsub.unsubscribe("pubsub", None, None)

        self.vip.pubsub.subscribe(peer='pubsub',
                                  prefix=topic,
                                  callback=self._handle_publish,all_platforms=True)

    def _handle_publish(self, peer, sender, bus, topic, headers, message):
        """
        Callback triggered by the subscription setup using the topic from the agent's config file
        """
        Print('####################################################Recieve Load Shifting ########################',topic,message)

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.

        Usually not needed if using the configuration store.
        """
        # Example publish to pubsub
        self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")

        # Example RPC call
        # self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        pass
    def dowork(self):
        self.hour=1+self.hour
        if self.hour>=24:
            self.hour=0
        print(self.ip,self.instancename,self.Building_type,"Current: Hour",self.hour, ": ",self.schedule[self.hour])       
        print(self.ip,self.instancename,self.Building_type,"Updated: Hour",self.hour, ": ",self.updatedSchedule[self.hour])

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        pass

    @RPC.export
    def rpc_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
        """
        RPC method

        May be called from another agent via self.core.rpc.call
        """
        return self.setting1 + arg1 - arg2


def main():
    """Main method called to start the agent."""
    utils.vip_main(loadShifting, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
