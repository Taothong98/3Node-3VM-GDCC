

sudo ufw status
sudo ufw allow 22
sudo ufw allow 60000
sudo ufw allow 61000
sudo ufw allow 51820
sudo ufw allow 51821
sudo ufw allow 51000

sudo sysctl -w net.ipv4.ip_forward=1      -----ชั่วคราว
sudo nano /etc/sysctl.conf
net.ipv4.ip_forward=1
sudo sysctl -p                              ----ยืนยัน
cat /proc/sys/net/ipv4/ip_forward           ----ตรวจสอบ


sudo sysctl -w net.ipv4.conf.all.src_valid_mark=1           -----ชั่วคราว
sudo nano /etc/sysctl.conf
net.ipv4.conf.all.src_valid_mark=1
sudo sysctl -p                                              ----ยืนยัน
cat /proc/sys/net/ipv4/conf/all/src_valid_mark              ----ตรวจสอบ

sudo ip route add <destination_network> via 192.168.110.200
sudo ip route add <destination_network> via 192.168.110.200
sudo ip route add <destination_network> via 192.168.110.200



-------------- host route ------------------------------
sudo sysctl -w net.ipv4.conf.all.src_valid_mark=1

echo "net.ipv4.conf.all.src_valid_mark=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

-------------  host nat -------------------
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o ens40 -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o ens41 -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o ens42 -j MASQUERADE
sudo iptables -t nat -L -v

sudo iptables -A FORWARD -i wg0 -o ens40 -j ACCEPT
sudo iptables -A FORWARD -i wg0 -o ens41 -j ACCEPT
sudo iptables -A FORWARD -i wg0 -o ens42 -j ACCEPT


NAT (Network Address Translation):
หากคุณต้องการให้ทราฟฟิกจาก VPN client ออกไปยังเครือข่ายภายในผ่าน interface เครือข่ายหลักของเซิร์ฟเวอร์ (เช่น eth0 หรือ interface อื่นที่เชื่อมต่อกับเครือข่ายภายใน):
กฎ iptables เหล่านี้จำเป็นต้องถูกบันทึกเพื่อคงอยู่ถาวรหลังการรีบูตระบบ (ใช้เครื่องมือเช่น iptables-save หรือการตั้งค่าใน /etc/iptables/rules.v4).
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

/etc/iptables/rules.v4

apk add iptables
sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -m physdev --physdev-in eth1 -o eth4 -j MASQUERADE

sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -m physdev --physdev-in eth2 -o eth5 -j MASQUERADE

sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -m physdev --physdev-in eth3 -o eth6 -j MASQUERADE

sudo docker exec -it VPNserver iptables -t nat -L -v



sudo docker exec -it VPNserver sh -c "iptables-save > /etc/iptables/rules.v4"




การตั้งค่า Forwarding Rules ใน Docker:
ตรวจสอบการกำหนดค่าการส่งต่อทราฟฟิกระหว่างเครือข่าย Docker และเครือข่ายภายในผ่าน WireGuard
sudo iptables -A FORWARD -i wg0 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o wg0 -j ACCEPT


ถ้าไม่มีเส้นทางไปยังเครือข่ายภายใน ให้เพิ่มเส้นทางโดยใช้คำสั่ง ip route add หรือแก้ไขการตั้งค่า routing บนระบบ:
sudo ip route add 172.16.10.0/24 via 172.16.10.1 dev eth0

ip route





3. ตรวจสอบการตั้งค่า Firewall บน Web Server
sudo ufw allow from 10.0.0.0/24   # หรือ subnet ของ VPN client
sudo iptables -A INPUT -s 10.0.0.0/24 -j ACCEPT


<!-- ========================================================= -->


docker exec -it VPNserver ip route




bash-5.0# sysctl net.ipv4.ip_forward
net.ipv4.ip_forward = 1




sudo docker exec -it VPNserver iptables -A FORWARD -i wg0 -o ens40 -j ACCEPT
sudo docker exec -it VPNserver iptables -A FORWARD -i wg0 -o ens41 -j ACCEPT
sudo docker exec -it VPNserver iptables -A FORWARD -i wg0 -o ens42 -j ACCEPT


sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -o ens40 -j MASQUERADE
sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -o ens41 -j MASQUERADE
sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -o ens42 -j MASQUERADE




sudo netfilter-persistent save

