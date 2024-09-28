import subprocess
import threading
import json
import os
import argparse
import re
import threading
import time
import pexpect
# sudo apt install python3-pexpect


def main():
    # เรียกฟังก์ชันเพื่อลบข้อมูลในไฟล์ log
    clear_log_files()

    # สร้าง stop_event เพื่อใช้หยุดการทำงานของ timer_thread
    stop_event = threading.Event()

    # เริ่ม timer_thread ใน background
    timer = threading.Thread(target=timer_thread, args=(stop_event,))
    timer.start()

    args = parse_args()  # รับค่าจาก command-line arguments

    # ตั้งค่า variables ที่เปลี่ยนแปลงได้
    ip_address = args.ip_address
    time_test = args.time_test
    bandwidth = args.bandwidth
    bandwidth2 = args.bandwidth2
    bandwidth3 = args.bandwidth3

    parallel = args.parallel
    buffer_size = args.buffer
    new_num_core = args.new_num_core
    new_cpu_limit = args.new_cpu_limit
    new_ram_limit = args.new_ram_limit
    link_capacity = args.link_capacity

    results = {}

    if new_cpu_limit:
        print(f"Setting modified cpu to {new_cpu_limit}")
        modify_cpu_limit(new_cpu_limit)

    if new_ram_limit:
        print(f"Setting modified ram to {new_ram_limit}")
        modify_ram_limit(new_ram_limit)
        
    if new_num_core:
        print(f"Setting modified num_core to {new_num_core}")
        modify_num_core(new_num_core)
        
    # docker_start()  # ต้องให้ docker_start() ทำงานเสร็จก่อน

    if link_capacity:
        print(f"Setting link capacity to {link_capacity}")
        set_link_capacity(link_capacity)

    # เพิ่มเฉพาะค่าที่ต้องการบันทึกลงใน JSON
    results["arguments"] = {
        "time_test": time_test,
        "bandwidth": bandwidth,
        "bandwidth2": bandwidth2,
        "bandwidth3": bandwidth3,
        "parallel": parallel,
        "num_core": new_num_core,
        "cpu_limit": new_cpu_limit,
        "ram_limit": new_ram_limit,
        "link_capacity": link_capacity,
    }

    # ฟังก์ชันที่ทำงานร่วมกับ threads เพื่อเก็บผลลัพธ์
    def run_iperf():
        results["iperf"] = iperf(ip_address, time_test, bandwidth, parallel)

    def run_getcpu():
        results["cpu"] = getcpu(time_test)

    def run_getmem():
        results["memory"] = get_memory_usage(time_test)

    def run_ping():
        results["ping"] = ping(ip_address, time_test)

    def run_ping_full():
        results["ping_full"] = ping_full_link(time_test)

    def run_iperf2():
        results["iperf2"] = iperf2(time_test, bandwidth2, parallel)

    def run_iperf3():
        results["iperf3"] = iperf3(time_test, bandwidth3, parallel)

    # สร้าง threads สำหรับ iperf, getcpu, และ get_memory_usage
    iperf_thread = threading.Thread(target=run_iperf)
    getcpu_thread = threading.Thread(target=run_getcpu)
    getmem_thread = threading.Thread(target=run_getmem)
    ping_thread = threading.Thread(target=run_ping)
    ping_full_thread = threading.Thread(target=run_ping_full)

    iperf2_thread = threading.Thread(target=run_iperf2)
    iperf3_thread = threading.Thread(target=run_iperf3)

    # เรียกใช้ทั้งสามฟังก์ชันพร้อมกัน
    iperf_thread.start()
    getcpu_thread.start()
    getmem_thread.start()
    ping_thread.start()
    ping_full_thread.start()

    if bandwidth2:
        iperf2_thread.start()
        iperf2_thread.join()

    if bandwidth3:
        iperf3_thread.start()
        iperf3_thread.join()

    # รอให้ทั้งสามฟังก์ชันเสร็จสิ้นการทำงาน
    iperf_thread.join()
    getcpu_thread.join()
    getmem_thread.join()
    ping_thread.join()
    ping_full_thread.join()

    # เรียกฟังก์ชันเพื่อรวมข้อมูลจากไฟล์ log ทั้งหมด
    combine_iperf_logs()

    # เรียกฟังก์ชัน process_file หลังจาก combine_iperf_logs เพื่อประมวลผล iperfall.log
    iperf_log_results = process_file('iperfall.log')
    
    # เพิ่มผลลัพธ์ลงใน results
    results["iperf_log"] = iperf_log_results

    # บันทึกผลลัพธ์ลงไฟล์ JSON
    with open('output_latest.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print("Results including ping saved to output_latest.json")

    # บันทึกผลลัพธ์ลงไฟล์ JSON (เขียนต่อท้ายข้อมูลเก่า)
    append_to_json('output_history.json', results)

    print("Results saved to output_latest.json and output_history.json")

    # หยุดการทำงานของ timer_thread เมื่อ main ทำงานเสร็จ
    stop_event.set()
    # รอให้ thread หยุดทำงาน
    timer.join()
    # หยุดการทำงานของ timer_thread เมื่อ main ทำงานเสร็จ
    stop_event.set()
    # รอให้ thread หยุดทำงาน
    timer.join() 

# ฟังก์ชันสำหรับเขียนข้อมูลต่อท้ายในไฟล์ JSON
def append_to_json(filename, new_data):
    if os.path.exists(filename):
        # ถ้าไฟล์มีอยู่แล้ว ให้อ่านข้อมูลเก่าเข้ามาก่อน
        with open(filename, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = []  # ถ้าไฟล์ว่าง ให้เริ่มเป็นลิสต์ว่าง
    else:
        data = []  # ถ้าไฟล์ไม่มีอยู่ ให้เริ่มเป็นลิสต์ว่าง

    # เพิ่มข้อมูลใหม่ลงในลิสต์
    data.append(new_data)

    # เขียนข้อมูลใหม่กลับลงไฟล์
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)    
        
            
        
# ฟังก์ชัน parse_args เพื่อรับค่าจาก command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Test performance script")
    
    # =================== input for iperf test =================
    parser.add_argument('-ip', '--ip_address', type=str, default="192.168.110.110", help='IP address to test')
    parser.add_argument('-t', '--time_test', type=str, default="1", help='Test duration in seconds')
    parser.add_argument('-b', '--bandwidth', type=str, default="1Gb", help='Bandwidth for iperf')
    parser.add_argument('-p', '--parallel', type=str, default="1", help='Number of parallel streams for iperf')
    parser.add_argument('-bf', '--buffer', type=str, default="8KB", help='Buffer size for iperf')
    
    parser.add_argument('-b2', '--bandwidth2', type=str,help='Bandwidth for iperf Node2')
    parser.add_argument('-b3', '--bandwidth3', type=str,help='Bandwidth for iperf Node3')
    
    
    # ====================== link_capacity =================
    # parser.add_argument('-lc', '--link_capacity', type=str, default="1024Mbit", help='link_capacity of VPN-Server')
    parser.add_argument('-lc', '--link_capacity', type=str, help='link_capacity of VPN-Server')
    # ====================== resource configguration =================
    parser.add_argument('-cpu', '--new_cpu_limit', type=str,default="1", help='resource configguration of .env')
    parser.add_argument('-ram', '--new_ram_limit', type=str,default="1024M", help='resource configguration of .env')
    parser.add_argument('-core', '--new_num_core', type=str,default="0", help='resource configguration of .env')
    
    
    return parser.parse_args()   
    
def get_shell_output(command):
    # รันคำสั่ง shell และดึงผลลัพธ์กลับมา
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()    
    
# ฟังก์ชัน iperf ใช้ตัวแปร ip_address จากภายนอก
def iperf(ip_address, time_test, bandwidth, parallel):
    print('iperf_test_start') 
    # เริ่มจับเวลา
    start_time = time.time()

    # คำสั่งหลักสำหรับ iperf
    # sudo docker exec IperfClient1 iperf3 -c 10.0.0.6 -t 1 >
    
    command = f"docker exec IperfClient1 iperf3 -c {ip_address} -u -t {time_test} -b {bandwidth} -P {parallel} > iperf1.log"
    
    # รันคำสั่ง iperf และรอให้เสร็จสิ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # สิ้นสุดการจับเวลา
    end_time = time.time()
    print('iperf_test_end') 
    
    # คำนวณเวลาที่ใช้ (response time)
    response_time = end_time - start_time

    if result.returncode != 0:
        return {"error": result.stderr}  # คืนค่าข้อผิดพลาดถ้าเกิดปัญหา
    
    # จัดเก็บผลลัพธ์ใน dictionary เพื่อบันทึกลง JSON
    return {
        "response_time": f"{response_time:.2f} seconds"            # เพิ่ม response time ที่จับได้
    }
    
# ฟังก์ชัน iperf ใช้ตัวแปร ip_address จากภายนอก
def iperf2(time_test, bandwidth2, parallel):
    print('iperf_test_start') 
    # เริ่มจับเวลา
    start_time = time.time()

    # คำสั่งหลักสำหรับ iperf
    # sudo docker exec IperfClient1 iperf3 -c 10.0.0.7 -t 1
    # command = f"docker exec IperfClient2 iperf3 -c 10.0.0.7 -u -t {time_test} -b {bandwidth2} -P {parallel} > iperf2.log"
    command = f"docker exec IperfClient3 iperf3 -c 192.168.120.110 -u -t {time_test} -b {bandwidth2} -P {parallel} > iperf3.log"
    
    
    # รันคำสั่ง iperf และรอให้เสร็จสิ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # สิ้นสุดการจับเวลา
    end_time = time.time()
    print('iperf_test_end') 
    
    # คำนวณเวลาที่ใช้ (response time)
    response_time = end_time - start_time

    if result.returncode != 0:
        return {"error": result.stderr}  # คืนค่าข้อผิดพลาดถ้าเกิดปัญหา
    
    # จัดเก็บผลลัพธ์ใน dictionary เพื่อบันทึกลง JSON
    return {
        "response_time": f"{response_time:.2f} seconds"            # เพิ่ม response time ที่จับได้
    }
    
# ฟังก์ชัน iperf ใช้ตัวแปร ip_address จากภายนอก
def iperf3(time_test, bandwidth3, parallel):
    print('iperf_test_start') 
    # เริ่มจับเวลา
    start_time = time.time()

    # คำสั่งหลักสำหรับ iperf
    # sudo docker exec IperfClient1 iperf3 -c 10.0.0.6 -t 1
    # command = f"docker exec IperfClient3 iperf3 -c 10.0.0.8 -u -t {time_test} -b {bandwidth3} -P {parallel} > iperf3.log"
    command = f"docker exec IperfClient3 iperf3 -c 192.168.130.110 -u -t {time_test} -b {bandwidth3} -P {parallel} > iperf3.log"
    
    # รันคำสั่ง iperf และรอให้เสร็จสิ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # สิ้นสุดการจับเวลา
    end_time = time.time()
    print('iperf_test_end') 
    
    # คำนวณเวลาที่ใช้ (response time)
    response_time = end_time - start_time

    if result.returncode != 0:
        return {"error": result.stderr}  # คืนค่าข้อผิดพลาดถ้าเกิดปัญหา

    
    # จัดเก็บผลลัพธ์ใน dictionary เพื่อบันทึกลง JSON
    return {
        "response_time": f"{response_time:.2f} seconds"            # เพิ่ม response time ที่จับได้
    }    
    
# ============================================================================================================    

# ฟังก์ชันเพื่อดึงบรรทัดที่ต้องการจากไฟล์ iperf log
def extract_data_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        sender_lines = []
        receiver_lines = []

        # หาบรรทัดที่มี sender และ receiver
        for line in lines:
            if "sender" in line:
                sender_lines.append(line.strip())
            elif "receiver" in line:
                receiver_lines.append(line.strip())

        return sender_lines, receiver_lines

# ฟังก์ชันเพื่อรวมผลลัพธ์จากหลายไฟล์และเขียนไปที่ iperfall.log
def combine_iperf_logs():
    # กำหนด directory ที่ไฟล์ log และไฟล์ python อยู่
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # ระบุรายชื่อไฟล์ log และรวม path ของไฟล์
    log_files = [
        os.path.join(current_directory, 'iperf1.log'),
        os.path.join(current_directory, 'iperf2.log'),
        os.path.join(current_directory, 'iperf3.log')
    ]

    # ระบุ output file ที่จะเขียน
    output_file = os.path.join(current_directory, 'iperfall.log')

    with open(output_file, 'w') as outfile:
        # เขียน header ให้กับไฟล์ output
        outfile.write("[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams\n")
        
        # ดึงข้อมูลจากแต่ละไฟล์ log และเขียนไปยัง output
        for log_file in log_files:
            sender_lines, receiver_lines = extract_data_from_file(log_file)
            # เขียน sender ทั้งหมดก่อน
            for sender in sender_lines:
                outfile.write(f"{sender}\n")
            # เขียน receiver ทั้งหมดหลังจาก sender
            for receiver in receiver_lines:
                outfile.write(f"{receiver}\n")

    print("ข้อมูลถูกรวมใน iperfall.log เรียบร้อยแล้ว")

# ฟังก์ชันเพื่อเคลียร์ข้อมูลในไฟล์ log หลังจากรวมข้อมูลแล้ว
def clear_log_files():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # ระบุรายชื่อไฟล์ log และรวม path ของไฟล์
    log_files = [
        os.path.join(current_directory, 'iperf1.log'),
        os.path.join(current_directory, 'iperf2.log'),
        os.path.join(current_directory, 'iperf3.log')
    ]

    # ลบข้อมูลในไฟล์ log
    for log_file in log_files:
        if os.path.exists(log_file):
            # เปิดไฟล์ในโหมดเขียนเพื่อเคลียร์ข้อมูลในไฟล์
            with open(log_file, 'w') as clear_file:
                clear_file.write("")  # เขียนค่าเป็นค่าว่างเพื่อทำให้ไฟล์ว่างเปล่า
            print(f"ลบข้อมูลในไฟล์ {log_file} เรียบร้อยแล้ว")

    
# =====================================================================================================

def modify_num_core(new_num_core):
    print('start_modify_num_core')
    
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@172.21.10.200 'python3 /home/debian/vpnserver/scaling.py -core {new_num_core}'"
    
    password = "debian"  # รหัสผ่านสำหรับ SSH

    # รันคำสั่ง SSH โดยใช้ pexpect
    child = pexpect.spawn(ssh_command)

    try:
        # ตรวจสอบข้อความที่ปรากฏ
        index = child.expect([pexpect.TIMEOUT, pexpect.EOF, "password:", "Are you sure you want to continue connecting (yes/no/[fingerprint])?"])

        if index == 3:  # ถ้ามีการถามเกี่ยวกับการยืนยันการเชื่อมต่อครั้งแรก
            print("SSH first-time connection prompt detected, sending 'yes'...")
            child.sendline("yes")  # ตอบ 'yes'
            index = child.expect(["password:", pexpect.EOF])  # รอตรวจสอบการถามรหัสผ่านหรือ EOF

        if index == 0 or index == 2:  # ถ้ามีการถามรหัสผ่าน
            print("Password prompt detected, sending password...")
            child.sendline(password)  # ส่งรหัสผ่านไป
            child.expect(pexpect.EOF)  # รอจนกระทั่งคำสั่งทำงานเสร็จสิ้น
        elif index in [1, 2]:  # ถ้าไม่มีการถามรหัสผ่าน
            print("No password prompt detected.")
        
        # ดึงผลลัพธ์ที่ได้รับจากการรันคำสั่ง
        output = child.before.decode("utf-8").splitlines()  # แยกบรรทัดจากผลลัพธ์
        
        # ลบช่องว่างและบรรทัดว่าง
        cleaned_output = [line.strip() for line in output if line.strip()]
        
        print(cleaned_output)

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"An error occurred: {e}")
        return None

# ฟังก์ชันสำหรับตรวจสอบและแก้ไข CPU
def modify_cpu_limit(new_cpu_limit):
    print('start_modify_cpu_limit')
    
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@172.21.10.200 'python3 /home/debian/vpnserver/scaling.py -cpu {new_cpu_limit}'"
    
    password = "debian"  # รหัสผ่านสำหรับ SSH

    # รันคำสั่ง SSH โดยใช้ pexpect
    child = pexpect.spawn(ssh_command)

    try:
        # ตรวจสอบข้อความที่ปรากฏ
        index = child.expect([pexpect.TIMEOUT, pexpect.EOF, "password:", "Are you sure you want to continue connecting (yes/no/[fingerprint])?"])

        if index == 3:  # ถ้ามีการถามเกี่ยวกับการยืนยันการเชื่อมต่อครั้งแรก
            print("SSH first-time connection prompt detected, sending 'yes'...")
            child.sendline("yes")  # ตอบ 'yes'
            index = child.expect(["password:", pexpect.EOF])  # รอตรวจสอบการถามรหัสผ่านหรือ EOF

        if index == 0 or index == 2:  # ถ้ามีการถามรหัสผ่าน
            print("Password prompt detected, sending password...")
            child.sendline(password)  # ส่งรหัสผ่านไป
            child.expect(pexpect.EOF)  # รอจนกระทั่งคำสั่งทำงานเสร็จสิ้น
        elif index in [1, 2]:  # ถ้าไม่มีการถามรหัสผ่าน
            print("No password prompt detected.")
        
        # ดึงผลลัพธ์ที่ได้รับจากการรันคำสั่ง
        output = child.before.decode("utf-8").splitlines()  # แยกบรรทัดจากผลลัพธ์
        
        # ลบช่องว่างและบรรทัดว่าง
        cleaned_output = [line.strip() for line in output if line.strip()]
        
        print(cleaned_output)

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"An error occurred: {e}")
        return None

# ฟังก์ชันสำหรับตรวจสอบและแก้ไข RAM
def modify_ram_limit(new_ram_limit):
    print('start_modify_ram_limit')
    
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@172.21.10.200 'python3 /home/debian/vpnserver/scaling.py -ram {new_ram_limit}'"
    
    password = "debian"  # รหัสผ่านสำหรับ SSH

    # รันคำสั่ง SSH โดยใช้ pexpect
    child = pexpect.spawn(ssh_command)

    try:
        # ตรวจสอบข้อความที่ปรากฏ
        index = child.expect([pexpect.TIMEOUT, pexpect.EOF, "password:", "Are you sure you want to continue connecting (yes/no/[fingerprint])?"])

        if index == 3:  # ถ้ามีการถามเกี่ยวกับการยืนยันการเชื่อมต่อครั้งแรก
            print("SSH first-time connection prompt detected, sending 'yes'...")
            child.sendline("yes")  # ตอบ 'yes'
            index = child.expect(["password:", pexpect.EOF])  # รอตรวจสอบการถามรหัสผ่านหรือ EOF

        if index == 0 or index == 2:  # ถ้ามีการถามรหัสผ่าน
            print("Password prompt detected, sending password...")
            child.sendline(password)  # ส่งรหัสผ่านไป
            child.expect(pexpect.EOF)  # รอจนกระทั่งคำสั่งทำงานเสร็จสิ้น
        elif index in [1, 2]:  # ถ้าไม่มีการถามรหัสผ่าน
            print("No password prompt detected.")
        
        # ดึงผลลัพธ์ที่ได้รับจากการรันคำสั่ง
        output = child.before.decode("utf-8").splitlines()  # แยกบรรทัดจากผลลัพธ์
        
        # ลบช่องว่างและบรรทัดว่าง
        cleaned_output = [line.strip() for line in output if line.strip()]
        
        print(cleaned_output)

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"An error occurred: {e}")
        return None       

def set_link_capacity(link_capacity):
    print('start_set_link_capacity')
    
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@172.21.10.200 'python3 /home/debian/vpnserver/setlinkcapacity.py --link_capacity {link_capacity}'"
    
    password = "debian"  # รหัสผ่านสำหรับ SSH

    # รันคำสั่ง SSH โดยใช้ pexpect
    child = pexpect.spawn(ssh_command)

    try:
        # ตรวจสอบข้อความที่ปรากฏ
        index = child.expect([pexpect.TIMEOUT, pexpect.EOF, "password:", "Are you sure you want to continue connecting (yes/no/[fingerprint])?"])

        if index == 3:  # ถ้ามีการถามเกี่ยวกับการยืนยันการเชื่อมต่อครั้งแรก
            print("SSH first-time connection prompt detected, sending 'yes'...")
            child.sendline("yes")  # ตอบ 'yes'
            index = child.expect(["password:", pexpect.EOF])  # รอตรวจสอบการถามรหัสผ่านหรือ EOF

        if index == 0 or index == 2:  # ถ้ามีการถามรหัสผ่าน
            print("Password prompt detected, sending password...")
            child.sendline(password)  # ส่งรหัสผ่านไป
            child.expect(pexpect.EOF)  # รอจนกระทั่งคำสั่งทำงานเสร็จสิ้น
        elif index in [1, 2]:  # ถ้าไม่มีการถามรหัสผ่าน
            print("No password prompt detected.")
        
        # ดึงผลลัพธ์ที่ได้รับจากการรันคำสั่ง
        output = child.before.decode("utf-8").splitlines()  # แยกบรรทัดจากผลลัพธ์
        
        # ลบช่องว่างและบรรทัดว่าง
        cleaned_output = [line.strip() for line in output if line.strip()]
        
        print(cleaned_output)

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"An error occurred: {e}")
        return None
           
    
# ฟังก์ชัน getcpu ใช้ mpstat เพื่อเก็บค่า CPU usage
def getcpu(time_test):
    print('get_cpu_usage') 
    
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@172.21.10.200 'for i in {{1..{time_test}}}; do mpstat -P ALL 1 1 | grep \"all\" | awk \"NR==1 {{print \\$13}}\"; done'"
    
    password = "debian"  # ใส่รหัสผ่านที่นี่

    # รันคำสั่ง SSH โดยใช้ pexpect
    child = pexpect.spawn(ssh_command)

    try:
        # ตรวจสอบข้อความที่ปรากฏ
        index = child.expect([pexpect.TIMEOUT, pexpect.EOF, "password:", "Are you sure you want to continue connecting (yes/no/[fingerprint])?"])

        if index == 3:  # ถ้ามีการถามเกี่ยวกับการยืนยันการเชื่อมต่อครั้งแรก
            print("SSH first-time connection prompt detected, sending 'yes'...")
            child.sendline("yes")  # ตอบ 'yes'
            index = child.expect(["password:", pexpect.EOF])  # รอตรวจสอบการถามรหัสผ่านหรือ EOF

        if index == 0 or index == 2:  # ถ้ามีการถามรหัสผ่าน
            print("Password prompt detected, sending password...")
            child.sendline(password)  # ส่งรหัสผ่านไป
            child.expect(pexpect.EOF)  # รอจนกระทั่งคำสั่งทำงานเสร็จสิ้น
        elif index in [1, 2]:  # ถ้าไม่มีการถามรหัสผ่าน
            print("No password prompt detected.")
        
        # ดึงผลลัพธ์ที่ได้รับจากการรันคำสั่ง
        output = child.before.decode("utf-8").splitlines()  # แยกบรรทัดจากผลลัพธ์
        print(output)

        # แปลงค่า %idle เป็นค่า CPU ที่ถูกใช้
        cpu_usages = []
        for line in output:
            try:
                idle = float(line.strip())  # แปลงค่า idle จากผลลัพธ์
                cpu_usages.append(100 - idle)  # คำนวณ CPU usage จาก idle
            except ValueError:
                continue  # ถ้าไม่สามารถแปลงค่าได้ให้ข้ามไป

        # ตรวจสอบว่าได้ค่า CPU usage หรือไม่
        if not cpu_usages:
            print("No CPU usage data found.")
            return None

        # คำนวณค่าเฉลี่ยของ CPU ที่ถูกใช้
        avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)

        # คืนค่าผลลัพธ์ CPU ที่ถูกใช้
        return avg_cpu_usage    

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"An error occurred: {e}")
        return None
            

# ฟังก์ชัน get_memory_usage เพื่อเก็บค่า RAM usage
def get_memory_usage(time_test,):
    print('get_memory_usage') 
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@172.21.10.200 'for i in {{1..{time_test}}}; do free | awk \"/Mem/ {{printf(\\\"%.2f\\\\n\\\", \\$3/\\$2 * 100.0)}}\"; sleep 1; done'"
    
    password = "debian"

    # รันคำสั่ง SSH โดยใช้ pexpect
    child = pexpect.spawn(ssh_command)

    try:
        # ตรวจสอบข้อความที่ปรากฏ
        index = child.expect([pexpect.TIMEOUT, pexpect.EOF, "password:", "Are you sure you want to continue connecting (yes/no/[fingerprint])?"])

        if index == 3:  # ถ้ามีการถามเกี่ยวกับการยืนยันการเชื่อมต่อครั้งแรก
            print("SSH first-time connection prompt detected, sending 'yes'...")
            child.sendline("yes")
            index = child.expect(["password:", pexpect.EOF])

        if index == 0 or index == 2:  # ถ้ามีการถามรหัสผ่าน
            print("Password prompt detected, sending password...")
            child.sendline(password)
            child.expect(pexpect.EOF)
        elif index in [1, 2]:
            print("No password prompt detected.")
        
        # ดึงผลลัพธ์ที่ได้รับจากการรันคำสั่ง
        output = child.before.decode("utf-8").splitlines()
        print("Raw output:", output)
        
        # แปลงผลลัพธ์เป็น float
        ram_usages = []
        for line in output:
            try:
                ram_usages.append(float(line.strip()))  # แปลงบรรทัดที่ไม่ว่างเป็น float
            except ValueError:
                continue  # ถ้าบรรทัดไม่ใช่ตัวเลขให้ข้ามไป

        # ตรวจสอบว่ามีค่า RAM usage หรือไม่
        if not ram_usages:
            print("No RAM usage data found.")
            return None

        # คำนวณค่าเฉลี่ยการใช้ RAM
        avg_ram_usage = sum(ram_usages) / len(ram_usages)

        return avg_ram_usage

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"An error occurred: {e}")
        return None    


# ===========================================================================================================
def ping(ip_address,time_test):
    command = f"docker exec IperfClient3 ping {ip_address} -c {time_test}"

    # รันคำสั่ง ping
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # แปลงผลลัพธ์เป็น string
    output = result.stdout.decode('utf-8')

    # ใช้ regular expression เพื่อดึงค่า max round-trip time
    match = re.search(r"min/avg/max = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)", output)

    if match:
        min_val, avg_val, max_val = match.groups()
        # print(f"Max round-trip time: {max_val} ms")
        # return {"min": min_val, "avg": avg_val, "max": max_val}
        return {"max": max_val}
    
    else:
        print("ไม่พบข้อมูล round-trip min/avg/max")
        return {"error": "ไม่พบข้อมูล ping"}
    
def ping_full_link(time_test):
    # command = f"docker exec IperfClient3 ping 10.0.0.8 -c {time_test}"
    command = f"docker exec IperfClient3 ping 192.168.130.100 -c {time_test}"
    

    # รันคำสั่ง ping
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # แปลงผลลัพธ์เป็น string
    output = result.stdout.decode('utf-8')

    # ใช้ regular expression เพื่อดึงค่า max round-trip time
    match = re.search(r"min/avg/max = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)", output)

    if match:
        min_val, avg_val, max_val = match.groups()
        # print(f"Max round-trip time: {max_val} ms")
        # return {"min": min_val, "avg": avg_val, "max": max_val}
        return {"max": max_val}
    
    else:
        print("ไม่พบข้อมูล round-trip min/avg/max")
        return {"error": "ไม่พบข้อมูล ping"}

# ================================== รวมข้อมูลในไฟล์ iperfall.log=======================================================

def parse_line(line):
    """Function to parse each line and return relevant metrics."""
    pattern = r'\[ *(\d+)\] +([\d\.]+-[\d\.]+) +sec +([\d\.]+) *([MKG]?Bytes) +([\d\.]+) *([MKG]?bits/sec) +([\d\.]+) *ms +(\d+)/(\d+) *\((\d+)%\)'
    match = re.match(pattern, line)
    if match:
        # Extracting all values needed
        id, interval, transfer, transfer_unit, bitrate, bitrate_unit, jitter, lost, total, loss_percentage = match.groups()
        transfer = float(transfer)
        bitrate = float(bitrate)
        jitter = float(jitter)  # Add jitter to the parsed values
        lost = int(lost)
        total = int(total)
        
        # Convert transfer size to bytes for consistency
        if transfer_unit == 'KBytes':
            transfer *= 1024
        elif transfer_unit == 'MBytes':
            transfer *= 1024 * 1024
        elif transfer_unit == 'GBytes':
            transfer *= 1024 * 1024 * 1024

        return {
            'id': int(id),
            'interval': interval,
            'transfer': transfer,
            'bitrate': bitrate,
            'jitter': jitter,  # Add jitter to the dictionary
            'lost': lost,
            'total': total,
            'loss_percentage': float(loss_percentage)
        }
    return None

def combine_metrics(metrics):
    """Function to combine metrics for sender and receiver."""
    combined = {
        'transfer': 0.0,
        'bitrate': 0.0,
        'jitter': 0.0,  # Initialize jitter sum
        'lost': 0,
        'total': 0,
    }
    
    for metric in metrics:
        combined['transfer'] += metric['transfer']
        combined['bitrate'] += metric['bitrate']
        combined['jitter'] += metric['jitter']  # Sum the jitter values
        combined['lost'] += metric['lost']
        combined['total'] += metric['total']
    
    # Calculate the average jitter
    combined['jitter'] = combined['jitter'] / len(metrics) if metrics else 0.0
    
    # Calculate the loss percentage
    combined['loss_percentage'] = (combined['lost'] / combined['total']) * 100 if combined['total'] > 0 else 0
    
    return combined

def process_file(file_name):
    """Process the iperfall.log file to combine metrics."""
    # หาที่อยู่ของไฟล์ iperfall.log ที่อยู่ใน directory เดียวกับไฟล์ Python
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    
    # เปิดไฟล์แล้วเริ่ม process
    with open(file_path, 'r') as file:
        sender_metrics = []
        receiver_metrics = []
        
        for line in file:
            parsed_data = parse_line(line)
            if parsed_data:
                if 'sender' in line:
                    sender_metrics.append(parsed_data)
                elif 'receiver' in line:
                    receiver_metrics.append(parsed_data)
        
        combined_sender = combine_metrics(sender_metrics)
        combined_receiver = combine_metrics(receiver_metrics)

        print("Combined Sender Metrics:")
        print(f"Transfer: {combined_sender['transfer'] / (1024 * 1024):.2f} MBytes")
        print(f"Bitrate: {combined_sender['bitrate']:.2f} Mbits/sec")
        print(f"Jitter: {combined_sender['jitter']:.3f} ms")
        print(f"Lost/Total Datagrams: {combined_sender['lost']}/{combined_sender['total']} ({combined_sender['loss_percentage']:.2f}%)")

        print("\nCombined Receiver Metrics:")
        print(f"Transfer: {combined_receiver['transfer'] / (1024 * 1024):.2f} MBytes")
        print(f"Bitrate: {combined_receiver['bitrate']:.2f} Mbits/sec")
        print(f"Jitter: {combined_receiver['jitter']:.3f} ms")
        print(f"Lost/Total Datagrams: {combined_receiver['lost']}/{combined_receiver['total']} ({combined_receiver['loss_percentage']:.2f}%)")

    output = {
        "SenderTransfer": f"{combined_sender['transfer'] / (1024 * 1024):.2f} MBytes",
        "ReceiverTransfer": f"{combined_receiver['transfer'] / (1024 * 1024):.2f} MBytes",
        "SenderBitrate": f"{combined_sender['bitrate']:.2f} Mbits/sec",
        "ReceiverBitrate": f"{combined_receiver['bitrate']:.2f} Mbits/sec",
        "SenderJitter": f"{combined_sender['jitter']:.3f} ms",
        "ReceiverJitter": f"{combined_receiver['jitter']:.3f} ms",
        "SenderLost/TotalDatagrams": f"{combined_sender['lost']}/{combined_sender['total']} ({combined_sender['loss_percentage']:.2f}%)",
        "ReceiverLost/TotalDatagrams": f"{combined_receiver['lost']}/{combined_receiver['total']} ({combined_receiver['loss_percentage']:.2f}%)"
    }

    # # Save the output to a JSON file
    # json_output_file = os.path.join(script_dir, 'iperf_results.json')
    # with open(json_output_file, 'w') as json_file:
    #     json.dump(output, json_file, indent=4)
    
    return output

# ===============================================================================================================


# ฟังก์ชันสำหรับนับเวลา
def timer_thread(stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        print(f"Time elapsed: {elapsed_time:.2f} seconds", end="\r")
        # time.sleep(1)  # อัปเดตทุก ๆ 1 วินาที
        time.sleep(0.01)  # ลดหน่วงเป็น 10 ms
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")
    
# เรียกใช้ฟังก์ชัน main เมื่อสคริปต์ถูกเรียกใช้โดยตรง
if __name__ == "__main__":
    main()
