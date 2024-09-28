# sudo apt update
# sudo apt install iproute2


# sudo find / -name tc
# export PATH=$PATH:/usr/sbin
# sudo dpkg -L iproute2
# sudo apt install --reinstall iproute2


# tc -help
# dpkg -s iproute2 | grep Version



# sudo tc class show dev wg0    
# sudo tc qdisc add dev wg0 root handle 1:0 htb default 10
# sudo tc class add dev wg0 parent 1:0 classid 1:10 htb rate 1000Mbit prio 0
# sudo iptables -A OUTPUT -t mangle -p udp -j MARK --set-mark 10
# sudo tc filter add dev wg0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10


# sudo tc class change dev wg0 parent 1:0 classid 1:10 htb rate 900Mbit prio 0 && sudo tc class show dev wg0    
# sudo tc class show dev wg0

# chmod +x setlinkcapacity.py

import subprocess
import os


import subprocess
import os
import argparse

# ฟังก์ชันเพื่อ parse arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Test setlinkcapacity.py script")
    
    # รับค่า link_capacity จาก command line argument
    parser.add_argument('-lc', '--link_capacity', default="1000Mbit", type=str, help='link_capacity of VPN-Server')
    
    return parser.parse_args()   

# ฟังก์ชันเพื่อตั้งค่า link capacity
def set_linkcapacity(link_capacity):
    # กำหนดรหัสผ่าน sudo
    password = "debian"  # แทนที่ด้วยรหัสผ่าน sudo ของคุณ

    # หา path ปัจจุบันที่ไฟล์ Python อยู่
    current_path = os.getcwd()

    # สร้าง command สำหรับตั้งค่า link capacity ด้วย tc
    command = f"sudo -S tc class change dev wg0 parent 1:0 classid 1:10 htb rate {link_capacity} prio 0 && sudo -S tc class show dev wg0"
    
    # รัน command ที่สร้างขึ้นโดยส่งรหัสผ่าน sudo ผ่าน stdin
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # ส่งรหัสผ่านไปยัง stdin ของ process
    output, error = process.communicate(input=password + '\n')
    
    # แสดงผลลัพธ์ทาง stdout
    if process.returncode == 0:
        print(f"Link capacity set to {link_capacity} successfully.")
        print(output)
    else:
        print(f"Failed to set link capacity. Error: {error}")
        
def ingress_lc(link_capacity):

    # add_ingress = f"sudo tc qdisc add dev wg0 handle ffff: ingress"
    del_ingress = f"sudo tc filter del dev wg0 parent ffff: protocol ip prio 50"
    rule_ingress = f"sudo tc filter add dev wg0 parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate {link_capacity} burst 10k drop"
    sho_ingress = f"sudo tc filter show dev wg0 parent ffff:"

    run_del_ingress = subprocess.run(del_ingress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_rule_ingress = subprocess.run(rule_ingress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_rule_ingress.stdout)
    
    run_sho_ingress = subprocess.run(sho_ingress, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_sho_ingress.stdout)

    print('ingress_lc end')        

        
if __name__ == "__main__":
    # รับ arguments จาก command line
    args = parse_args()

    # เรียกฟังก์ชัน set_linkcapacity โดยส่งค่า link_capacity
    set_linkcapacity(args.link_capacity)
    ingress_lc(args.link_capacity)


    
