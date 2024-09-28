import subprocess
import time
import os
import threading


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

def combine_logs_and_clear(nodes_count):
    combined_log = "iperfall.log"
    
    with open(combined_log, 'w') as f_combined:
        for node_num in range(1, nodes_count+1):
            log_file = f"/home/iperf/iperf{node_num}.log"
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f_log:
                    f_combined.write(f_log.read())
                
                open(log_file, 'w').close()

def iperf_test(ip_address, time_test, bandwidth, parallel, node_number):
    print(f'iperf_test_start for node {node_number}')
    
    start_time = time.time()
    
    command = f"docker exec IperfClient{node_number} iperf3 -c {ip_address} -u -t {time_test} -b {bandwidth} -P {parallel} > /home/iperf/iperf{node_number}.log"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    end_time = time.time()
    response_time = end_time - start_time

    if result.returncode != 0:
        return {"error": result.stderr}

    senderTransfer = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'sender' | tail -n 2 | awk '{{print $5}}' | sed 's/[A-Za-z]*//g'"
    receiverTransfer = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'receiver' | tail -n 1 | awk '{{print $5}}' | sed 's/[A-Za-z]*//g'"
    senderBitrate = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'sender' | tail -n 2 | awk '{{print $7}}' | sed 's/[A-Za-z]*//g'"
    receiverBitrate = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'receiver' | tail -n 1 | awk '{{print $7}}' | sed 's/[A-Za-z]*//g'"
    senderJitter = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'sender' | tail -n 2 | awk '{{print $9}}' | sed 's/[A-Za-z]*//g'"
    receiverJitter = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'receiver' | tail -n 1 | awk '{{print $9}}' | sed 's/[A-Za-z]*//g'"
    senderLostTotal = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'sender' | tail -n 2 | awk '{{print $11}}' | sed 's/[A-Za-z]*//g'"
    receiverLostTotal = f"docker exec IperfClient{node_number} cat /home/iperf/iperf{node_number}.log | grep -a 'receiver' | tail -n 1 | awk '{{print $11}}' | sed 's/[A-Za-z]*//g'"

    result_sender_transfer = subprocess.run(senderTransfer, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_receiver_transfer = subprocess.run(receiverTransfer, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_sender_bitrate = subprocess.run(senderBitrate, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_receiver_bitrate = subprocess.run(receiverBitrate, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_sender_jitter = subprocess.run(senderJitter, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_receiver_jitter = subprocess.run(receiverJitter, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_sender_lost = subprocess.run(senderLostTotal, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    result_receiver_lost = subprocess.run(receiverLostTotal, shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()

    return {
        "node": node_number,
        "senderTransfer": f"{result_sender_transfer} MB",
        "receiverTransfer": f"{result_receiver_transfer} MB",
        "senderBitrate": f"{result_sender_bitrate} Mbps",
        "receiverBitrate": f"{result_receiver_bitrate} Mbps",
        "senderJitter": f"{result_sender_jitter} ms",
        "receiverJitter": f"{result_receiver_jitter} ms",
        "senderLostTotal": f"{result_sender_lost} packets",
        "receiverLostTotal": f"{result_receiver_lost} packets",
        "response_time": f"{response_time:.2f} seconds"
    }

def run_all_tests(ip_addresses, time_tests, bandwidths, parallels):
    nodes = len(ip_addresses)
    results = []
    threads = []

    for i in range(nodes):
        ip_address = ip_addresses[i]
        time_test = time_tests[i]
        bandwidth = bandwidths[i]
        parallel = parallels[i]
        node_number = i + 1
        
        thread = threading.Thread(target=lambda: results.append(iperf_test(ip_address, time_test, bandwidth, parallel, node_number)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    combine_logs_and_clear(nodes)
    
    return {
        "nodes_tested": nodes,
        "results": results
    }

def main():
    iperf_server_start()
    # กำหนดค่าของแต่ละ node
    ip_addresses = ["10.0.0.6", "10.0.0.7", "10.0.0.8"]
    time_tests = [1, 1, 1]
    bandwidths = ["200Mb", "300Mb", "400Mb"]
    parallels = [1, 1, 1]

    # เรียกใช้ฟังก์ชันทดสอบทั้งหมด
    results = run_all_tests(ip_addresses, time_tests, bandwidths, parallels)
    
    # แสดงผลลัพธ์
    print("Test Results:")
    for result in results["results"]:
        print(result)

# ตรวจสอบให้แน่ใจว่าโค้ดนี้จะถูกรันเมื่อเรียกใช้โดยตรง
if __name__ == "__main__":
    main()
