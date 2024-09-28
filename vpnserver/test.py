import subprocess
import threading
import json
import os
import argparse
import re
import threading
import time


def ingress_lc():

    # add_ingress = f"sudo tc qdisc add dev wg0 handle ffff: ingress"
    del_ingress = f"sudo tc filter del dev wg0 parent ffff: protocol ip prio 50"
    rule_ingress = f"sudo tc filter add dev wg0 parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate 1Mbit burst 10k drop"
    sho_ingress = f"sudo tc filter show dev wg0 parent ffff:"

    run_del_ingress = subprocess.run(del_ingress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_rule_ingress = subprocess.run(rule_ingress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_rule_ingress.stdout)
    
    run_sho_ingress = subprocess.run(sho_ingress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_sho_ingress.stdout)

    print('ingress_lc end')
    
ingress_lc()
