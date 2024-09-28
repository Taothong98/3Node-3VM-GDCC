#!/bin/bash
# chmod +x iptables-setup.sh

# sudo chmod +x ./dev-VPNserver/iptables-setup.sh

# # Forward traffic between WireGuard (wg0) and LAN interfaces (eth0-eth4)
# iptables -A FORWARD -i wg0 -o eth1 -j ACCEPT
# iptables -A FORWARD -i wg0 -o eth2 -j ACCEPT
# iptables -A FORWARD -i wg0 -o eth3 -j ACCEPT
# iptables -A FORWARD -i wg0 -o eth4 -j ACCEPT
# iptables -A FORWARD -i wg0 -o eth0 -j ACCEPT

# # Enable NAT for VPN clients to access LAN networks (eth0-eth4)
# iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
# iptables -t nat -A POSTROUTING -o eth2 -j MASQUERADE
# iptables -t nat -A POSTROUTING -o eth3 -j MASQUERADE
# iptables -t nat -A POSTROUTING -o eth4 -j MASQUERADE
# iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# # Allow forwarding from LAN to VPN
# # iptables -A FORWARD -i eth1 -o wg0 -j ACCEPT
# # iptables -A FORWARD -i eth2 -o wg0 -j ACCEPT
# # iptables -A FORWARD -i eth3 -o wg0 -j ACCEPT
# # iptables -A FORWARD -i eth4 -o wg0 -j ACCEPT
# # iptables -A FORWARD -i eth0 -o wg0 -j ACCEPT



# Forward traffic between WireGuard (wg0) and LAN interfaces (eth0-eth4)
sudo docker exec -it VPNserver iptables -A FORWARD -i wg0 -o ens40 -j ACCEPT
sudo docker exec -it VPNserver iptables -A FORWARD -i wg0 -o ens41 -j ACCEPT
sudo docker exec -it VPNserver iptables -A FORWARD -i wg0 -o ens42 -j ACCEPT

# Enable NAT for VPN clients to access LAN networks (eth0-eth4)
sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -o ens40 -j MASQUERADE
sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -o ens41 -j MASQUERADE
sudo docker exec -it VPNserver iptables -t nat -A POSTROUTING -o ens42 -j MASQUERADE
# sudo docker ps -a
sudo docker exec -it VPNserver ip route

# ==================================  TC link =========================================

###################### Egress (ส่งออก): --->  protocol ควบคุมการส่งข้อมูลออกจากอินเตอร์เฟซไปยังเครือข่าย.  #################################################
# sudo tc class show dev wg0    
sudo tc qdisc add dev wg0 root handle 1:0 htb default 10
sudo tc class add dev wg0 parent 1:0 classid 1:10 htb rate 1000Mbit prio 0
sudo tc filter add dev wg0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10
sudo iptables -A OUTPUT -t mangle -p udp -j MARK --set-mark 10



# ###################### Egress --> ACL  #################################################

# sudo tc qdisc add dev wg0 root handle 1:0 htb default 10
# sudo tc class add dev wg0 parent 1:0 classid 1:10 htb rate 1Mbit burst 10k
# sudo tc filter add dev wg0 parent 1:0 protocol ip prio 1 u32 match ip dst 0.0.0.0/0 flowid 1:10

# ###################### Ingress (รับเข้า): --> ACL  ควบคุมปริมาณข้อมูลที่เข้ามาในอินเตอร์เฟซโดยใช้การ policing  #################################################

# sudo tc qdisc add dev wg0 handle ffff: ingress
# sudo tc filter add dev wg0 parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate 1Mbit burst 10k drop
# sudo tc filter del dev wg0 parent ffff: protocol ip prio 50
# sudo tc filter add dev wg0 parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate 1000Mbit burst 10k drop
# sudo tc filter show dev wg0 parent ffff:
# sudo tc qdisc show dev wg0





# สมมติว่าคุณมีการเชื่อมต่อเครือข่ายที่ความเร็ว 100Mbps และคุณต้องการจำกัดแบนด์วิธการใช้งานดังนี้:
#    บริการ Web traffic ได้รับแบนด์วิธ 50Mbps.
#    บริการ File Transfer (FTP) ได้รับแบนด์วิธ 30Mbps.
#    ทราฟฟิกอื่น ๆ ได้รับแบนด์วิธ 20Mbps.
# sudo tc qdisc add dev eth0 root handle 1: htb default 10
# sudo tc class add dev eth0 parent 1: classid 1:1 htb rate 100Mbit
# sudo tc class add dev eth0 parent 1:1 classid 1:10 htb rate 50Mbit  # Web traffic
# sudo tc class add dev eth0 parent 1:1 classid 1:20 htb rate 30Mbit  # FTP
# sudo tc class add dev eth0 parent 1:1 classid 1:30 htb rate 20Mbit  # Other traffic


