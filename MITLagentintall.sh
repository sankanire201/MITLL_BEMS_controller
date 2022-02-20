export VOLTTRON_HOME=~/.BEMS_1
vctl remove -f  --tag PshaverAgent
vctl remove -f  --tag LPCGMAgent
python scripts/install-agent.py -s ~/volttron/BEMS_control_package/PshaverGMagent/ -c ~/volttron/BEMS_control_package/PshaverGMagent/config1 -t PshaverAgent
python scripts/install-agent.py -s ~/volttron/BEMS_control_package/LPCGMAgent/ -c ~/volttron/BEMS_control_package/LPCGMAgent/config1 --t LPCGMAgent
vctl enable  --tag PshaverAgent LPCGMAgent
vctl start  --tag PshaverAgent LPCGMAgent

export VOLTTRON_HOME=~/.BEMS_2
vctl remove -f  --tag PshaverAgent
vctl remove -f  --tag LPCGMAgent

python scripts/install-agent.py -s ~/volttron/BEMS_control_package/PshaverGMagent/ -c ~/volttron/BEMS_control_package/PshaverGMagent/config2 -t PshaverAgent
python scripts/install-agent.py -s ~/volttron/BEMS_control_package/LPCGMAgent/ -c ~/volttron/BEMS_control_package/LPCGMAgent/config2 --t LPCGMAgent
vctl enable  --tag PshaverAgent LPCGMAgent
vctl start  --tag PshaverAgent LPCGMAgent

