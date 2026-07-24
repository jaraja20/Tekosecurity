# jul/20/2026 16:23:39 by RouterOS 6.49.10
# software id = U8IB-HEVY
#
# model = CRS326-24G-2S+
# serial number = F5F60FAC6937
/interface bridge
add name=Hernandarias
/interface ethernet
set [ find default-name=ether1 ] name="ether1 - Neo Telecom"
set [ find default-name=ether2 ] name="ether2 - Tigo"
/interface pppoe-client
add add-default-route=yes disabled=no interface="ether1 - Neo Telecom" name=\
    "Giganet - Internet" password=22671 user=24441
/interface l2tp-client
add connect-to=190.128.138.66 disabled=no mrru=1600 name="PTP NASSER KM 6" \
    password=Nasserttxs2251 user=Hernandarias
add allow=mschap1,mschap2 connect-to=45.170.129.97 ipsec-secret=ipsecnasser \
    mrru=1600 name=l2tp-out1 password=Nasserttxs2251 user=Hernandarias
/interface pptp-client
add allow=mschap1,mschap2 connect-to=45.170.129.97 disabled=no name=\
    "pptp hern" password=Nasserttxs2251 user=HernardariosGiga
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=dhcp_pool0 ranges=192.168.16.100-192.168.16.254
/ip dhcp-server
add address-pool=dhcp_pool0 disabled=no interface=Hernandarias lease-time=\
    3d10m name=dhcp1
/routing ospf instance
set [ find default=yes ] redistribute-other-ospf=as-type-1 router-id=\
    192.168.16.1
/interface bridge port
add bridge=Hernandarias interface=ether5
add bridge=Hernandarias interface=ether6
add bridge=Hernandarias interface=ether7
add bridge=Hernandarias interface=ether8
add bridge=Hernandarias interface=ether9
add bridge=Hernandarias interface=ether10
add bridge=Hernandarias interface=ether11
add bridge=Hernandarias interface=ether12
add bridge=Hernandarias interface=ether13
add bridge=Hernandarias interface=ether14
add bridge=Hernandarias interface=ether15
add bridge=Hernandarias interface=ether16
add bridge=Hernandarias interface=ether17
add bridge=Hernandarias interface=ether18
add bridge=Hernandarias interface=ether19
add bridge=Hernandarias interface=ether20
add bridge=Hernandarias interface=ether21
add bridge=Hernandarias interface=ether22
add bridge=Hernandarias interface=ether23
add bridge=Hernandarias interface=ether24
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=192.168.16.1/24 interface=Hernandarias network=192.168.16.0
add address=10.156.97.162/30 interface="ether2 - Tigo" network=10.156.97.160
/ip dhcp-server lease
add address=192.168.16.105 client-id=1:34:e8:94:21:34:4c comment=\
    "PRINT SERVER CAJA HRIAS" mac-address=34:E8:94:21:34:4C server=dhcp1
/ip dhcp-server network
add address=192.168.16.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.16.1
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4
/ip firewall address-list
add address=172.16.0.0/12 list=allow-ip
add address=192.168.0.0/16 list=allow-ip
add address=127.0.0.1 list=allow-ip
/ip firewall filter
add action=add-src-to-address-list address-list=ip2 address-list-timeout=7s \
    chain=input comment=ip2 packet-size=359 protocol=icmp src-address-list=\
    ip1
add action=add-src-to-address-list address-list=allow-ip \
    address-list-timeout=1h chain=input comment=allow-ip packet-size=359 \
    protocol=icmp src-address-list=ip2
add action=add-src-to-address-list address-list=blacklist \
    address-list-timeout=2h chain=input comment=blacklist packet-size=!359 \
    protocol=icmp src-address-list=ip2
add action=add-src-to-address-list address-list=blacklist \
    address-list-timeout=2h chain=input comment=blacklist packet-size=1014 \
    protocol=icmp
add action=add-src-to-address-list address-list=blacklist \
    address-list-timeout=2h chain=input comment=blacklist packet-size=1055 \
    protocol=icmp
add action=accept chain=forward dst-address=192.168.13.0/24 src-address=\
    192.168.16.108
add action=drop chain=forward dst-address=186.16.15.89
add action=accept chain=forward src-address=192.168.13.169-192.168.13.170
add action=accept chain=input src-address=192.168.13.169-192.168.13.170
add action=accept chain=output src-address=192.168.13.169-192.168.13.170
add action=passthrough chain=unused-hs-chain comment=\
    "place hotspot rules here"
add action=drop chain=input comment="Drop Invalid connections" \
    connection-state=invalid
add action=accept chain=input comment="Allow Established connections" \
    connection-state=established
add action=accept chain=input comment="Allow ICMP" protocol=icmp
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
add action=accept chain=icmp comment=" echo reply" icmp-options=0:0 protocol=\
    icmp
add action=accept chain=icmp comment=" allow parameter bad" icmp-options=12:0 \
    protocol=icmp
add action=accept chain=icmp comment=" net unreachable" icmp-options=3:0 \
    protocol=icmp
add action=accept chain=icmp comment=" host unreachable" icmp-options=3:1 \
    protocol=icmp
add action=accept chain=icmp comment=\
    " host unreachable fragmentation required" icmp-options=3:4 protocol=icmp
add action=accept chain=icmp comment=" allow source quench" icmp-options=4:0 \
    protocol=icmp
add action=accept chain=icmp comment=" allow echo request" icmp-options=8:0 \
    protocol=icmp
add action=accept chain=icmp comment=" allow time exceed" icmp-options=11:0 \
    protocol=icmp
add action=accept chain=icmp comment=" allow parameter bad" icmp-options=12:0 \
    protocol=icmp
add action=drop chain=icmp comment=" deny all other types"
add action=drop chain=input comment=" drop ftp brute forcers" dst-port=21 \
    protocol=tcp src-address-list=ftp_blacklist
add action=accept chain=output content=" 530 Login incorrect" dst-limit=\
    1/1m,9,dst-address/1m protocol=tcp
add action=add-dst-to-address-list address-list=ftp_blacklist \
    address-list-timeout=3h chain=output content=" 530 Login incorrect" \
    protocol=tcp
add action=drop chain=input comment="drop ssh brute forcers" dst-port=22 \
    protocol=tcp src-address-list=ssh_blacklist
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
add action=drop chain=input comment="dropping port scanners" \
    src-address-list="port scanners"
add action=add-src-to-address-list address-list=blocked-addr \
    address-list-timeout=1d chain=input connection-limit=!100,32 disabled=yes \
    protocol=tcp
add action=tarpit chain=input connection-limit=3,32 protocol=tcp \
    src-address-list=blocked-addr
add action=jump chain=forward comment="SYN Flood protect" connection-state=\
    new jump-target=SYN-Protect protocol=tcp tcp-flags=syn
add action=drop chain=SYN-Protect connection-state=new disabled=yes protocol=\
    tcp tcp-flags=syn
add action=reject chain=forward comment="Reject if in the 24-hour-list" \
    reject-with=icmp-network-unreachable src-address-list=24-hour-list
add action=tarpit chain=input comment=\
    "Add you ip addess to allow-ip in Address Lists." dst-port=30553 \
    protocol=tcp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 - Neo Telecom"
add action=masquerade chain=srcnat out-interface="Giganet - Internet"
add action=masquerade chain=srcnat out-interface="ether2 - Tigo"
add action=dst-nat chain=dstnat disabled=yes dst-port=80 protocol=udp \
    to-addresses=192.168.13.161 to-ports=80
add action=masquerade chain=srcnat comment="masquerade hotspot network" \
    disabled=yes src-address=192.168.1.0/24
add action=masquerade chain=srcnat comment="masquerade hotspot network" \
    src-address=192.168.1.0/24
add action=masquerade chain=srcnat comment="masquerade hotspot network" \
    disabled=yes src-address=192.168.13.0/24
add action=masquerade chain=srcnat dst-address=192.168.16.217
add action=masquerade chain=srcnat dst-address=192.168.16.199
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set irc disabled=yes
set h323 disabled=yes
set sip disabled=yes
set udplite disabled=yes
set dccp disabled=yes
/ip route
add check-gateway=ping distance=1 gateway=10.11.1.89
add check-gateway=ping distance=2 gateway=10.156.97.161
add check-gateway=ping distance=1 dst-address=45.170.129.97/32 gateway=\
    10.156.97.161
/routing ospf network
add area=backbone network=192.168.16.0/24
add area=backbone network=192.168.11.0/24
/system clock
set time-zone-name=America/Asuncion
/system identity
set name=RouterOS
/system routerboard settings
set boot-os=router-os
