import pexpect

# ฟังก์ชัน set_link_capacity ใช้เพื่อเรียกคำสั่ง SSH และตั้งค่า link capacity
def modify_num_core(new_num_core):
    print('start_modify_num_core')
    
    # คำสั่ง SSH ที่ต้องการรัน
    ssh_command = f"ssh debian@192.168.1.236 'python3 /home/debian/vpnserver/scaling.py -core {new_num_core}'"
    
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

# เรียกใช้ฟังก์ชัน set_link_capacity
modify_num_core("2")