# jul/20/2026 16:24:53 by RouterOS 6.49.10
# software id = U8KM-STHL
#
# model = RB760iGS
# serial number = D4500D8DE0D5
/interface bridge
add name=RED
/interface pptp-client
add connect-to=190.128.138.66 disabled=no name=Nasser password=Nasserttxs2251 \
    user=NasserZFdeposito
add connect-to=45.170.129.97 disabled=no name=NasserZFdeposito password=\
    Nasserttxs2251 user=NasserZFdeposito
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=dhcp_pool0 ranges=192.168.15.2-192.168.15.254
/ip dhcp-server
add address-pool=dhcp_pool0 disabled=no interface=RED lease-time=3d10m name=\
    dhcp1
/interface bridge port
add bridge=RED interface=ether3
add bridge=RED interface=ether4
add bridge=RED interface=ether1
add bridge=RED interface=ether5
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=192.168.15.1/24 interface=RED network=192.168.15.0
/ip dhcp-client
add disabled=no interface=ether2
/ip dhcp-server lease
add address=192.168.15.254 client-id=1:0:17:61:11:7c:23 mac-address=\
    00:17:61:11:7C:23 server=dhcp1
/ip dhcp-server network
add address=192.168.15.0/24 dns-server=192.168.15.1,8.8.8.8 gateway=\
    192.168.15.1
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,1.1.1.1
/ip firewall filter
add action=accept chain=forward dst-address=192.168.15.0/24 src-address=\
    192.168.13.0/24
add action=accept chain=forward dst-address=192.168.13.0/24 src-address=\
    192.168.15.0/24
add action=accept chain=input
add action=accept chain=output
add action=accept chain=forward
add action=drop chain=input comment="dropping port scanners" \
    src-address-list="port scanners"
add action=drop chain=input comment="drop ssh brute forcers" protocol=tcp \
    src-address-list=ssh_blacklist
add action=accept chain=input dst-address=190.128.138.66 dst-port=161 \
    protocol=udp src-address=45.228.137.178
add action=passthrough chain=unused-hs-chain comment=\
    "place hotspot rules here" disabled=yes
add action=drop chain=input comment="Drop Invalid connections" \
    connection-state=invalid disabled=yes
add action=accept chain=input comment="Allow Established connections" \
    connection-state=established
add action=accept chain=input comment="Allow ICMP" protocol=icmp
add action=accept chain=input src-address=192.168.15.0/24
add action=accept chain=input dst-address=190.128.138.66 dst-port=161 \
    protocol=tcp src-address=45.228.137.178
add action=drop chain=forward comment="drop invalid connections" \
    connection-state=invalid disabled=yes protocol=tcp
add action=accept chain=forward comment=\
    "allow already established connections" connection-state=established
add action=accept chain=forward comment="allow related connections" \
    connection-state=related
add action=drop chain=forward src-address=0.0.0.0/8
add action=drop chain=forward dst-address=0.0.0.0/8
add action=drop chain=forward src-address=127.0.0.0/8
add action=drop chain=forward dst-address=127.0.0.0/8
add action=drop chain=forward src-address=224.0.0.0/3
add action=drop chain=forward dst-address=224.0.0.0/3
add action=drop chain=forward dst-address=127.0.0.0/8
add action=drop chain=forward src-address=224.0.0.0/3
add action=drop chain=forward dst-address=224.0.0.0/3
add action=drop chain=tcp comment="deny TFTP" dst-port=69 protocol=tcp
add action=drop chain=tcp comment="deny RPC portmapper" dst-port=111 \
    protocol=tcp
add action=drop chain=tcp comment="deny RPC portmapper" dst-port=135 \
    protocol=tcp
add action=drop chain=tcp comment="deny NBT" dst-port=137-139 protocol=tcp
add action=drop chain=tcp comment="deny cifs" dst-port=445 protocol=tcp
add action=drop chain=tcp comment="deny NFS" dst-port=2049 protocol=tcp
add action=drop chain=tcp comment="deny NetBus" dst-port=12345-12346 \
    protocol=tcp
add action=drop chain=tcp comment="deny NetBus" dst-port=20034 protocol=tcp
add action=drop chain=tcp comment="deny BackOriffice" dst-port=3133 protocol=\
    tcp
add action=drop chain=tcp comment="deny DHCP" dst-port=67-68 protocol=tcp
add action=drop chain=udp comment=" deny TFTP" dst-port=69 protocol=udp
add action=drop chain=udp comment=" deny PRC portmapper" dst-port=111 \
    protocol=udp
add action=drop chain=udp comment=" deny PRC portmapper" dst-port=135 \
    protocol=udp
add action=drop chain=udp comment=" deny NBT" dst-port=137-139 protocol=udp
add action=drop chain=udp comment=" deny NFS" dst-port=2049 protocol=udp
add action=drop chain=udp comment=" deny BackOriffice" dst-port=3133 \
    protocol=udp
add action=drop chain=icmp comment=" deny all other types"
add action=drop chain=input comment=" drop ftp brute forcers" dst-port=21 \
    protocol=tcp src-address-list=ftp_blacklist
add action=accept chain=output content=" 530 Login incorrect" dst-limit=\
    1/1m,9,dst-address/1m protocol=tcp
add action=add-dst-to-address-list address-list=ftp_blacklist \
    address-list-timeout=3h chain=output content=" 530 Login incorrect" \
    protocol=tcp
add action=add-src-to-address-list address-list=ssh_blacklist \
    address-list-timeout=1w3d chain=input connection-state=new dst-port=22 \
    protocol=tcp src-address-list=ssh_stage3
add action=add-src-to-address-list address-list=ssh_stage3 \
    address-list-timeout=1m chain=input connection-state=new dst-port=22 \
    protocol=tcp src-address-list=ssh_stage2
add action=add-src-to-address-list address-list=ssh_stage2 \
    address-list-timeout=1m chain=input connection-state=new dst-port=22 \
    protocol=tcp src-address-list=ssh_stage1
add action=add-src-to-address-list address-list=ssh_stage1 \
    address-list-timeout=1m chain=input connection-state=new dst-port=22 \
    protocol=tcp
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="Port scanners to list " \
    protocol=tcp psd=21,3s,3,1
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="NMAP FIN Stealth scan" \
    protocol=tcp tcp-flags=fin,!syn,!rst,!psh,!ack,!urg
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="SYN/FIN scan" protocol=tcp \
    tcp-flags=fin,syn
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="SYN/RST scan" protocol=tcp \
    tcp-flags=syn,rst
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="FIN/PSH/URG scan" protocol=\
    tcp tcp-flags=fin,psh,urg,!syn,!rst,!ack
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="ALL/ALL scan" protocol=tcp \
    tcp-flags=fin,syn,rst,psh,ack,urg
add action=add-src-to-address-list address-list="port scanners" \
    address-list-timeout=2w chain=input comment="NMAP NULL scan" protocol=tcp \
    tcp-flags=!fin,!syn,!rst,!psh,!ack,!urg
add action=add-src-to-address-list address-list=blocked-addr \
    address-list-timeout=1d chain=input connection-limit=!100,32 disabled=yes \
    protocol=tcp
add action=tarpit chain=input connection-limit=3,32 protocol=tcp \
    src-address-list=blocked-addr
add action=jump chain=forward comment="SYN Flood protect" connection-state=\
    new jump-target=SYN-Protect protocol=tcp tcp-flags=syn
add action=accept chain=SYN-Protect connection-state=new limit=400,5 \
    protocol=tcp tcp-flags=syn
add action=drop chain=SYN-Protect connection-state=new disabled=yes protocol=\
    tcp tcp-flags=syn
add action=reject chain=forward comment="Reject if in the 24-hour-list" \
    reject-with=icmp-network-unreachable src-address-list=24-hour-list
/ip firewall nat
add action=passthrough chain=unused-hs-chain comment=\
    "place hotspot rules here" disabled=yes
add action=dst-nat chain=dstnat disabled=yes dst-port=80 protocol=udp \
    to-addresses=192.168.13.161 to-ports=80
add action=masquerade chain=srcnat out-interface=ether2
add action=masquerade chain=srcnat comment="masquerade hotspot network" \
    disabled=yes src-address=192.168.15.254
add action=masquerade chain=srcnat dst-address=192.168.15.0/24
/ip firewall service-port
set dccp disabled=yes
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh disabled=yes
set api disabled=yes
set api-ssl disabled=yes
/routing ospf network
add area=backbone network=192.168.15.0/24
add area=backbone network=192.168.11.0/24
/system clock
set time-zone-name=America/Asuncion
/system identity
set name="Nasser km12 Deposito"
