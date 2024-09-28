



def iperf_server_start():

    # สร้าง command สำหรับ docker-compose ps โดยระบุ path ของไฟล์ docker-compose.yml
    commandsts1 = f"sudo docker exec IperfClient4 iperf3 -s &"
    commandsts2 = f"sudo docker exec IperfClient5 iperf3 -s &"
    commandsts3 = f"sudo docker exec IperfClient6 iperf3 -s &"
    # รัน command ที่สร้างขึ้น
    run_s1 = subprocess.run(commandsts1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_s2 = subprocess.run(commandsts1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_s3 = subprocess.run(commandsts1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print('iperf3 -s ')  # แสดงผลลัพธ์ทาง stdout
    


def main():
    iperf_server_start()
# เรียกใช้ฟังก์ชัน main เมื่อสคริปต์ถูกเรียกใช้โดยตรง

if __name__ == "__main__":
    main()
