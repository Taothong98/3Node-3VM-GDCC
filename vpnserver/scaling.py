# chmod +x scaling.py

import argparse  # สำหรับรับค่าจาก command-line arguments
import subprocess  # สำหรับรันคำสั่ง shell
import os  # สำหรับจัดการไฟล์และ path
import time  # สำหรับการหน่วงเวลา

# ฟังก์ชัน parse_args เพื่อรับค่าจาก command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="scaling.py script")
    # ====================== resource configuration =================
    # parser.add_argument('-cpu', '--new_cpu_limit', type=str, default="1", help='resource configuration of .env')
    parser.add_argument('-cpu', '--new_cpu_limit', type=str, help='resource configuration of .env')
    
    # parser.add_argument('-ram', '--new_ram_limit', type=str, default="1024M", help='resource configuration of .env')
    parser.add_argument('-ram', '--new_ram_limit', type=str, help='resource configuration of .env')
    
    # parser.add_argument('-core', '--new_num_core', type=str, default="0", help='resource configuration of .env')
    parser.add_argument('-core', '--new_num_core', type=str, help='resource configuration of .env')
    
    
    return parser.parse_args()   
   

# ฟังก์ชันสำหรับตรวจสอบและแก้ไข NUM_core
def modify_num_core(new_num_core):
    # file_path = '.env'
    # current_path = os.getcwd()  # รับ path ปัจจุบัน
    # env_file_path = os.path.join(current_path, file_path)  # ประกอบ path ของไฟล์ .env
    file_path = '/home/debian/vpnserver/.env'  # ระบุ absolute path ไปยังไฟล์ .env
    with open(file_path, 'r') as f:
    # with open(env_file_path, 'r') as f:
        lines = f.readlines()

    # ตรวจสอบค่า NUM_core ปัจจุบันในไฟล์
    current_num_core = None
    for line in lines:
        if "NUM_core" in line:
            current_num_core = line.split('=')[1].strip()  # อ่านค่าเป็น string

    # ตรวจสอบว่า NUM_core ตรงกับค่าที่รับเข้ามาหรือไม่
    if current_num_core == new_num_core:
        print("NUM_core is the same, no changes needed.")
    else:
        # ถ้าไม่ตรง ให้ทำการเปลี่ยนแปลงค่า
        new_lines = []
        for line in lines:
            if "NUM_core" in line:
                new_lines.append(f"NUM_core={new_num_core}\n")
            else:
                new_lines.append(line)

        # เขียนข้อมูลกลับไปที่ไฟล์
        # with open(env_file_path, 'w') as f:
        with open(file_path, 'w') as f:
            
            f.writelines(new_lines)

        print(f"NUM_core updated to {new_num_core}. Auto change success, Check again..")



# ฟังก์ชันสำหรับตรวจสอบและแก้ไข CPU
def modify_cpu_limit(new_cpu_limit):
    # file_path = '.env'
    # current_path = os.getcwd()  # รับ path ปัจจุบัน
    # env_file_path = os.path.join(current_path, file_path)  # ประกอบ path ของไฟล์ .env
    file_path = '/home/debian/vpnserver/.env'  # ระบุ absolute path ไปยังไฟล์ .env
    with open(file_path, 'r') as f:
    # with open(env_file_path, 'r') as f:
        lines = f.readlines()

    current_cpu_limit = None
    for line in lines:
        if "CPU_limits" in line:
            current_cpu_limit = line.split('=')[1].strip()  # อ่านค่าเป็น string

    if current_cpu_limit == new_cpu_limit:
        print("CPU resource is same, you can test it")
    else:
        new_lines = []
        for line in lines:
            if "CPU_limits" in line:
                new_lines.append(f"CPU_limits={new_cpu_limit}\n")
            else:
                new_lines.append(line)

        # with open(env_file_path, 'w') as f:
        with open(file_path, 'w') as f:
            
            f.writelines(new_lines)
        
        print("CPU limit updated. Auto change success, Check again..")

# ฟังก์ชันสำหรับตรวจสอบและแก้ไข RAM
def modify_ram_limit(new_ram_limit):
    # file_path = '.env'
    # current_path = os.getcwd()  # รับ path ปัจจุบัน
    # env_file_path = os.path.join(current_path, file_path)  # ประกอบ path ของไฟล์ .env
    file_path = '/home/debian/vpnserver/.env'  # ระบุ absolute path ไปยังไฟล์ .env
    with open(file_path, 'r') as f:
    # with open(env_file_path, 'r') as f:
        lines = f.readlines()

    current_ram_limit = None
    for line in lines:
        if "RAM_limits" in line:
            current_ram_limit = line.split('=')[1].strip()

    if current_ram_limit == new_ram_limit:
        print("RAM resource is same, you can test it")
    else:
        new_lines = []
        for line in lines:
            if "RAM_limits" in line:
                new_lines.append(f"RAM_limits={new_ram_limit}\n")
            else:
                new_lines.append(line)

        # with open(env_file_path, 'w') as f:
        with open(file_path, 'w') as f:
            
            f.writelines(new_lines)
        
        print("RAM limit updated. Auto change success, Check again..")

def docker_start():
    current_path = os.getcwd()

    command = f"docker-compose -f {current_path}/docker-compose.yml ps -a"
    compose_stop = f"docker-compose -f {current_path}/docker-compose.yml stop"
    compose_rm = f"docker-compose -f {current_path}/docker-compose.yml rm -f"
    compose_up = f"docker-compose -f {current_path}/docker-compose.yml up -d"

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_compose_stop = subprocess.run(compose_stop, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_compose_stop.stdout)
    
    run_compose_rm = subprocess.run(compose_rm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_compose_rm.stdout)
    
    run_compose_up = subprocess.run(compose_up, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(run_compose_up.stdout)
    print('docker-compose up')

def natTraffic():
    current_path = os.getcwd()
    nat_traffic = "sudo {current_path}/iptables-setup.sh"
    run_natTraffic = subprocess.run(nat_traffic, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Nat Traffic: ", run_natTraffic.stdout)

if __name__ == "__main__":
    args = parse_args()

    # ตรวจสอบการแก้ไข CPU และ RAM
    if args.new_cpu_limit:
        print(f"Setting modified CPU to {args.new_cpu_limit}")
        modify_cpu_limit(args.new_cpu_limit)

    if args.new_ram_limit:
        print(f"Setting modified RAM to {args.new_ram_limit}")
        modify_ram_limit(args.new_ram_limit)
        
    if args.new_num_core:
        print(f"Setting modified core to {args.new_num_core}")
        modify_num_core(args.new_num_core)        
        
    docker_start()
    time.sleep(1)  # ลดหน่วงเวลาเป็น 1 วินาที
    natTraffic()
