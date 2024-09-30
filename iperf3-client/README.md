

sudo apt install python3-pip
pip install pexpect
sudo apt install python3-pexpect




################################### XanMod Kernel (xanmod.org) #################################


hostnamectl

wget -qO - https://dl.xanmod.org/archive.key | gpg --dearmor -vo /usr/share/keyrings/xanmod-archive-keyring.gpg

echo 'deb [signed-by=/usr/share/keyrings/xanmod-archive-keyring.gpg] http://deb.xanmod.org releases main' | tee /etc/apt/sources.list.d/xanmod-release.list

apt update && apt install linux-xanmod-x64v2

--------------------------------------------------------------------------------------------------
ตรวจสอบการมีอยู่ของไฟล์ cpu.rt_runtime_us ในระบบ

ls /sys/fs/cgroup/cpu.rt_runtime_us
/sys/fs/cgroup/cpu.rt_runtime_us
zcat /proc/config.gz | grep CONFIG_RT_GROUP_SCHED

cat /boot/config-$(uname -r) | grep CONFIG_RT_GROUP_SCHED
# CONFIG_RT_GROUP_SCHED is not set

hostnamectl
cat /proc/version

apt update
apt install git

cd /usr/src/
mkdir /usr/src/linux-6.9.9/build
cd /usr/src/linux-6.9.9

wget https://mirrors.edge.kernel.org/pub/linux/kernel/v6.x/linux-6.8.tar.gz
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.15.tar.

wget https://gitlab.com/xanmod/linux/-/archive/6.6.50-rt42-xanmod1/linux-6.6.50-rt42-xanmod1.tar.gz
wget -4 https://gitlab.com/xanmod/linux/-/archive/6.6.50-rt42-xanmod1/linux-6.6.50-rt42-xanmod1.tar.gz


tar -xzvf linux-6.8.tar.gz
tar -xzvf linux-5.15.tar.gz
tar -xzvf linux-6.6.50-rt42-xanmod1.tar.gz

cd linux-6.8/
cd linux-5.15/
cd linux-6.6.50-rt42-xanmod1/


sudo apt install git build-essential fakeroot libncurses-dev libssl-dev ccache bison flex

make menuconfig

# Go to General setup ─> Control Group Support ─> CPU controller ─> Group scheduling for SCHED_RR/FIFO configuration as shown below: 
0 33 4 3

# Go to General setup ─> Kernel .config support and enable access to .config through /proc/config.gz
0 24 25

make -j20


################################### sudoers #################################
apt install sudoers

nano ls /etc/sudoers

debian  ALL=(ALL:ALL) ALL

usermod -aG root debian
nano /etc/group

groups debian

#################################### install docker #######################################

apt update

apt install apt-transport-https ca-certificates curl gnupg lsb-release -y 

curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update

apt install docker-ce docker-ce-cli containerd.io -y

docker --version

systemctl enable docker
systemctl start docker


####################################### Docker-compose #################################

curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

docker-compose --version

###################################### install git ####################################

apt install git

git clone https://github.com/Taothong98/VPN-NFV.git 

sudo apt install python3

----------------------- apache2 ---------------------------------------

nano /etc/apache2/sites-available/000-default.conf
/var/www/html

groups debian
usermod -aG debian www-data
groups www-data

chmod -R g+rX /home/debian/VPN-NFV

chmod -R 777 /home/debian/VPN-NFV

systemctl restart apache2

ln -s /var/www/html/VPN-NFV /home/debian/VPN-NFV



---------------------------- Test cpu ----------------------------------

sudo docker exec -it VPNserver apk add --no-cache stress-ng

sudo docker exec -it VPNserver stress-ng --cpu 1 --timeout 60

docker exec -it IperfServer bash
htop
sudo docker exec -it VPNserver htop

docker exec -it VPNserver stress-ng --cpu 0 --cpu-load 70 --timeout 60


stdocker exec -it VPNserver ress-ng --vm 1 --vm-bytes 128M --timeout 60
docker exec -it VPNserver stress-ng --vm 2 --vm-bytes 2G --timeout 60


sudo docker stats VPNserver

sudo docker-compose restart
sudo docker restart VPNserver 

sudo docker-compose up stop
sudo docker-compose up start
sudo docker-compose up -d



======================================= TC ====================================================
สร้าง
tc qdisc add dev wg0 root handle 1:0 htb default 10
tc class add dev wg0 parent 1:0 classid 1:10 htb rate 500Mbit prio 0
tc filter add dev wg0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10

แสดง
tc class show dev wg0

เปลี่ยนแปลงค่า
tc class change dev wg0 classid 1:10 htb rate 30Mbit

ลบ
tc class del dev wg0 classid 1:10

--------------------------------------- TC docker --------------------------------------------
docker exec VPNserver tc class show dev wg0

docker exec VPNserver tc qdisc add dev wg0 root handle 1:0 htb default 10
docker exec VPNserver tc class add dev wg0 parent 1:0 classid 1:10 htb rate 500Mbit prio 0
docker exec VPNserver tc filter add dev wg0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10

docker exec VPNserver tc class show dev wg0

docker exec VPNserver ping 192.168.100.100
docker exec IperfClient2 iperf3 -c 192.168.100.100
docker exec -it IperfClient bash


1. ลบค่าเก่าก่อนเปลี่ยนแปลง

tc class del dev wg0 classid 1:10
tc class add dev wg0 parent 1:0 classid 1:10 htb rate 200Mbit prio 0

2. แก้ไขค่าแบนด์วิธโดยไม่ต้องลบ

tc class change dev wg0 parent 1:0 classid 1:10 htb rate 200Mbit prio 0

#########################################################333

iperf3 -c 192.168.100.100

docker exec -it IperfClient apk add iperf3
docker exec -it IperfClient iperf3 -c 192.168.100.100

docker stats VPNserver


  cat /proc/cpuinfo
  
  cat /proc/net/dev






























sudo hostnamectl set-hostname vpn_server
sudo hostnamectl set-hostname iperf_client
sudo hostnamectl set-hostname iperf_server


sudo nano /etc/network/interfaces

---------------------------------------------------------- vpn server ------------------------------

source /etc/network/interfaces.d/*

auto lo
iface lo inet loopback
allow-hotplug ens18
iface ens18 inet dhcp
iface ens18 inet6 auto
	
auto ens19
iface ens19 inet static
    address 172.21.111.200
    netmask 255.255.255.0  
auto ens20
iface ens20 inet static
    address 172.21.112.200   
    netmask 255.255.255.0   
auto ens21
iface ens21 inet static
    address 172.21.113.200   
    netmask 255.255.255.0   
auto ens22
iface ens22 inet static
    address 172.21.11.200   
    netmask 255.255.255.0   
auto ens23
iface ens23 inet static
    address 172.21.12.200   
    netmask 255.255.255.0   
auto enp2s1
iface enp2s1 inet static
    address 172.21.13.200   
    netmask 255.255.255.0   
auto enp2s2
iface enp2s2 inet static
    address 10.10.10.1   
    netmask 255.255.255.0   


---------------------------------------------------------- iperf client ------------------------------

source /etc/network/interfaces.d/*

auto lo
iface lo inet loopback
allow-hotplug ens18
iface ens18 inet dhcp
iface ens18 inet6 auto
	
auto ens19
iface ens19 inet static
    address 172.21.11.50
    netmask 255.255.255.0  
auto ens20
iface ens20 inet static
    address 172.21.12.50   
    netmask 255.255.255.0   
auto ens21
iface ens21 inet static
    address 172.21.13.50   
    netmask 255.255.255.0   
auto ens22
iface ens22 inet static
    address 10.10.10.2 
    netmask 255.255.255.0   
 

---------------------------------------------------------- iperf server ------------------------------

source /etc/network/interfaces.d/*

auto lo
iface lo inet loopback
allow-hotplug ens18
iface ens18 inet dhcp
iface ens18 inet6 auto
	
auto ens20
iface ens20 inet static
    address 172.21.111.100
    netmask 255.255.255.0  
auto ens21
iface ens21 inet static
    address 172.21.112.100   
    netmask 255.255.255.0   
auto ens22
iface ens22 inet static
    address 172.21.113.100   
    netmask 255.255.255.0   
auto ens23
iface ens23 inet static
    address 10.10.10.3  
    netmask 255.255.255.0   

