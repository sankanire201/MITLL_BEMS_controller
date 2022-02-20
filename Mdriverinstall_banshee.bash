
vctl stop --tag MasterDriver

vctl remove --tag MasterDriver

python scripts/install-agent.py -s services/core/PlatformDriverAgent -c services/core/PlatformDriverAgent/platform-driver.agent -t MasterDriver
vctl config store platform.driver registry_configs/modbus_bansheeGM.csv ~/volttron/Config/modbus_bansheeGM.csv --csv 



vctl config store platform.driver devices/Campus1/Benshee1/BEMS_2  ~/volttron/Config/modbus_banshee.config

vctl enable --tag MasterDriver
vctl start --tag MasterDriver
