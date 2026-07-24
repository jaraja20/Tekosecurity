# jul/20/2026 16:28:15 by RouterOS 6.49.10
# software id = PV47-1I5C
#
# model = RB760iGS
# serial number = HE508QTHVAZ
/interface ethernet
set [ find default-name=ether5 ] comment="ponto a ponto" l2mtu=1598 \
    mac-address=D4:CA:6D:16:38:9B name="ether2 - mikrotik a mikrotik" speed=\
    100Mbps
set [ find default-name=ether4 ] comment="REDE WIRELESS VISITANTE" l2mtu=1598 \
    mac-address=D4:CA:6D:16:38:9C name="ether3 - REDE WIRELESS VISITANTE" \
    speed=100Mbps
set [ find default-name=ether3 ] l2mtu=1598 mac-address=D4:CA:6D:16:38:9D \
    name=ether4 speed=100Mbps
set [ find default-name=ether2 ] l2mtu=1598 mac-address=D4:CA:6D:16:38:9E \
    name="ether5-Internet Giganet" speed=100Mbps
/interface pppoe-client
add add-default-route=yes disabled=no interface="ether5-Internet Giganet" \
    name="Internet Giganet" password=6233 use-peer-dns=yes user=7057
/interface l2tp-server
add name=Hernandarias user=Hernandarias
add name="Recapadora KM 28" user=RecapadoraKM28
add name=YpaneNasser user=YpaneNasser
add name=Ypanekm28 user=Ypanekm28
add name="Zona Franca" user=zonafranca
/interface pptp-server
add name="Nasser Centro" user=NasserCentro
add name=RecapadoraKM28 user=RecapadoraKM28
add name=RecapadoraKM285 user=RecapadoraKM285
add name=km7 user=km7
add name=nasser user=nasser
/interface ethernet switch port
set 0 default-vlan-id=0
set 1 default-vlan-id=0
set 2 default-vlan-id=0
set 3 default-vlan-id=0
set 5 default-vlan-id=0
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=Nasser-Tigo
/ip hotspot profile
add dns-name=nasserdns.dns.com hotspot-address=192.168.1.1 html-directory=\
    flash/hotspot http-cookie-lifetime=1d name=hsprof1
/ip ipsec proposal
set [ find default=yes ] enc-algorithms=3des
/ip pool
add name=dhcp_pool1 ranges=192.168.10.20-192.168.10.254
add name=dhcp_pool2 ranges=192.168.19.2-192.168.19.254
add name=dhcp_pool3 ranges=\
    192.168.13.1-192.168.13.99,192.168.13.101-192.168.13.199
/ip dhcp-server
add address-pool=dhcp_pool1 authoritative=after-2sec-delay disabled=no \
    interface="ether3 - REDE WIRELESS VISITANTE" lease-time=1d name=dhcp1
add address-pool=dhcp_pool2 disabled=no interface=ether4 lease-time=3d10m \
    name=dhcp2
add address-pool=dhcp_pool3 disabled=no interface=ether1 lease-time=3d10m \
    name=dhcp3
/ip hotspot
add address-pool=dhcp_pool1 addresses-per-mac=1 disabled=no idle-timeout=3m \
    interface="ether3 - REDE WIRELESS VISITANTE" name=hotspot1 profile=\
    hsprof1
/ip hotspot user profile
add address-pool=dhcp_pool1 mac-cookie-timeout=1d name=128k rate-limit=\
    128k/128k shared-users=10 transparent-proxy=yes
add address-pool=dhcp_pool1 mac-cookie-timeout=1d name=127k rate-limit=\
    128k/128k shared-users=5 transparent-proxy=yes
/ppp profile
add change-tcp-mss=yes dns-server=8.8.8.8,8.8.4.4 name=comdns use-encryption=\
    yes
/queue simple
add max-limit=4M/4M name=queue2 target=192.168.19.254/32
add max-limit=564k/564k name=queue1 target=192.168.13.90/32
/queue type
add kind=pcq name=PCQ-Subida pcq-classifier=src-address
add kind=pcq name=PCQ-Bajada pcq-classifier=dst-address
/queue simple
add disabled=yes max-limit=20M/130M name=Ecualizador_Red_13 queue=\
    PCQ-Subida/PCQ-Bajada target=192.168.13.0/24
add disabled=yes max-limit=20M/130M name=Ecualizador_Hotspot_10 queue=\
    PCQ-Subida/PCQ-Bajada target=192.168.10.0/24
/routing ospf instance
set [ find default=yes ] router-id=192.168.13.1
/snmp community
set [ find default=yes ] addresses=0.0.0.0/0
add addresses=::/0 name=zabbix
/system logging action
set 0 memory-lines=100
set 1 disk-file-name=log disk-lines-per-file=100
/ip firewall connection tracking
set enabled=yes tcp-established-timeout=5m
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface l2tp-server server
set allow-fast-path=yes caller-id-type=number enabled=yes ipsec-secret=\
    ipsecnasser use-ipsec=yes
/interface pptp-server server
set enabled=yes
/ip address
add address=192.168.13.100/24 comment="Rede Principal Nasser" interface=\
    ether1 network=192.168.13.0
add address=192.168.10.1/24 comment="Wireless Visitante" interface=\
    "ether3 - REDE WIRELESS VISITANTE" network=192.168.10.0
add address=192.168.199.2/24 comment="IP Tigo Internet" interface=\
    "ether2 - mikrotik a mikrotik" network=192.168.199.0
add address=192.168.11.1/24 comment=VPNS interface="ether5-Internet Giganet" \
    network=192.168.11.0
add address=192.168.13.254/24 comment="Rede Principal Nasser" interface=\
    ether1 network=192.168.13.0
add address=192.168.19.1/24 interface=ether4 network=192.168.19.0
/ip arp
add address=192.168.13.118 mac-address=04:18:D6:A8:48:A3
/ip dhcp-server lease
add address=192.168.19.248 client-id=1:74:da:88:30:19:9b mac-address=\
    74:DA:88:30:19:9B server=dhcp2
add address=192.168.19.237 client-id=1:d4:5d:64:3c:1a:46 mac-address=\
    D4:5D:64:3C:1A:46 server=dhcp2
/ip dhcp-server network
add address=192.168.10.0/24 dns-server=192.168.10.1 gateway=192.168.10.1 \
    netmask=24
add address=192.168.13.0/24 dns-server=8.8.8.8 gateway=192.168.13.100
add address=192.168.19.0/24 dns-server=8.8.8.8,1.1.1.1 gateway=192.168.19.1
/ip dns
set allow-remote-requests=yes servers=8.8.8.8
/ip dns static
add address=192.168.1.1 name=nasserdns.dns.com
add address=190.128.241.94 name=www.vue.org.py
add address=190.128.241.95 name=estadisticas.vue.org.py
add address=192.168.11.4 name=unifi
add address=192.168.5.200 name=contab-pc
/ip firewall filter
add action=accept chain=forward src-address=192.168.9.0/24
add action=accept chain=forward src-address=192.168.16.0/24
add action=accept chain=output protocol=udp src-address=192.168.13.121
add action=accept chain=input dst-address=192.168.13.121 protocol=udp
add action=accept chain=forward dst-address=192.168.15.0/24
add action=drop chain=input comment="dropping port scanners" \
    src-address-list="port scanners"
add action=drop chain=input comment="drop ssh brute forcers" protocol=tcp \
    src-address-list=ssh_blacklist
add action=accept chain=input dst-address=190.128.138.66 dst-port=161 \
    protocol=tcp src-address=45.228.137.178
add action=accept chain=input dst-address=190.128.138.66 dst-port=161 \
    protocol=udp src-address=45.228.137.178
add action=drop chain=input dst-port=53 in-interface="Internet Giganet" \
    protocol=tcp
add action=drop chain=input dst-port=53 in-interface="Internet Giganet" \
    protocol=udp
add action=drop chain=forward dst-address=192.168.5.0/24 src-address=\
    192.168.10.0/24
add action=accept chain=forward src-address=192.168.13.169-192.168.13.170
add action=accept chain=input src-address=192.168.13.169-192.168.13.170
add action=accept chain=output src-address=192.168.13.169-192.168.13.170
add action=passthrough chain=unused-hs-chain comment=\
    "place hotspot rules here" disabled=yes
add action=drop chain=forward disabled=yes in-interface=\
    "ether3 - REDE WIRELESS VISITANTE" out-interface=*1
add action=drop chain=input comment="Drop Invalid connections" \
    connection-state=invalid disabled=yes
add action=accept chain=input comment="Allow Established connections" \
    connection-state=established
add action=accept chain=input comment="Allow ICMP" protocol=icmp
add action=accept chain=input src-address=192.168.16.0/24
add action=accept chain=input in-interface="ether3 - REDE WIRELESS VISITANTE" \
    src-address=192.168.1.0/24
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
add action=drop chain=icmp comment=" deny all other types" disabled=yes
add action=drop chain=input comment=" drop ftp brute forcers" dst-port=21 \
    protocol=tcp src-address-list=ftp_blacklist
add action=accept chain=output content=" 530 Login incorrect" dst-limit=\
    1/1m,9,dst-address/1m protocol=tcp
add action=jump chain=forward comment="SYN Flood protect" connection-state=\
    new jump-target=SYN-Protect protocol=tcp tcp-flags=syn
add action=accept chain=SYN-Protect connection-state=new limit=400,5 \
    protocol=tcp tcp-flags=syn
add action=accept chain=forward
add action=accept chain=output
add action=drop chain=SYN-Protect connection-state=new disabled=yes protocol=\
    tcp tcp-flags=syn
add action=reject chain=forward comment="Reject if in the 24-hour-list" \
    reject-with=icmp-network-unreachable src-address-list=24-hour-list
add action=drop chain=forward src-mac-address=BC:67:1C:C6:4D:BA
/ip firewall nat
add action=dst-nat chain=dstnat dst-address=45.170.129.97 dst-port=10161 \
    protocol=udp src-address=45.228.137.181 to-addresses=192.168.11.2 \
    to-ports=161
add action=dst-nat chain=dstnat dst-address=45.170.129.97 dst-port=10161 \
    protocol=udp src-address=190.128.138.66 to-addresses=192.168.11.2 \
    to-ports=161
add action=dst-nat chain=dstnat dst-address=45.170.129.97 dst-port=10162 \
    protocol=udp src-address=45.228.137.179 to-addresses=192.168.11.10 \
    to-ports=161
add action=dst-nat chain=dstnat dst-address=45.170.129.97 dst-port=10162 \
    protocol=udp src-address=190.128.138.66 to-addresses=192.168.11.10 \
    to-ports=161
add action=dst-nat chain=dstnat disabled=yes dst-address=45.170.129.97 \
    dst-port=10050 protocol=tcp src-address=45.228.137.179 to-addresses=\
    192.168.13.250 to-ports=10050
add action=dst-nat chain=dstnat disabled=yes dst-address=45.170.129.97 \
    dst-port=10050 protocol=tcp src-address=190.128.138.66 to-addresses=\
    192.168.13.250 to-ports=10050
add action=dst-nat chain=dstnat disabled=yes dst-address=45.170.129.97 \
    dst-port=10050 protocol=udp src-address=45.228.137.181 to-addresses=\
    192.168.13.250 to-ports=10050
add action=dst-nat chain=dstnat disabled=yes dst-address=45.170.129.97 \
    dst-port=10051 protocol=tcp src-address=45.228.137.181 to-addresses=\
    192.168.13.250 to-ports=10051
add action=dst-nat chain=dstnat disabled=yes dst-address=45.170.129.97 \
    dst-port=10051 protocol=udp src-address=45.228.137.181 to-addresses=\
    192.168.13.250 to-ports=10051
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    45.170.129.97 dst-port=5061 log=yes log-prefix=voip protocol=udp \
    to-addresses=192.168.13.121 to-ports=5061
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    45.170.129.97 dst-port=5061 log=yes log-prefix=voip protocol=tcp \
    to-addresses=192.168.13.121 to-ports=5061
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    45.170.129.97 dst-port=5062 log=yes log-prefix=voip protocol=udp \
    to-addresses=192.168.13.121 to-ports=5062
add action=dst-nat chain=dstnat comment="testes do voip" disabled=yes \
    dst-address=45.170.129.97 dst-port=20000-40000 log=yes log-prefix=voip \
    protocol=tcp to-addresses=192.168.13.121 to-ports=20000-40000
add action=dst-nat chain=dstnat comment="testes do voip" disabled=yes \
    dst-address=45.170.129.97 dst-port=20000-40000 log=yes log-prefix=voip \
    protocol=tcp src-address-list=Voip to-addresses=192.168.13.121 to-ports=\
    20000-40000
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    45.170.129.97 dst-port=20000-40000 log-prefix=voip protocol=udp \
    to-addresses=192.168.13.121 to-ports=20000-40000
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    190.128.138.66 dst-port=20000-40000 log-prefix=voip protocol=udp \
    to-addresses=192.168.13.121 to-ports=20000-40000
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    45.170.129.97 dst-port=20000-40000 log-prefix=voip protocol=udp \
    src-address-list=Voip to-addresses=192.168.13.121 to-ports=20000-40000
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    190.128.138.66 dst-port=20000-40000 log-prefix=voip protocol=udp \
    src-address-list=Voip to-addresses=192.168.13.121 to-ports=20000-40000
add action=dst-nat chain=dstnat comment="testes do voip" dst-address=\
    45.170.129.97 dst-port=5062 log=yes log-prefix=voip protocol=tcp \
    to-addresses=192.168.13.121 to-ports=5062
add action=dst-nat chain=dstnat comment="testes do voip" disabled=yes \
    dst-address=45.170.129.97 dst-port=5060 log=yes log-prefix=voip protocol=\
    udp to-addresses=192.168.13.121 to-ports=5060
add action=dst-nat chain=dstnat comment="testes do voip" disabled=yes \
    dst-address=45.170.129.97 dst-port=5060 log=yes log-prefix=voip protocol=\
    tcp to-addresses=192.168.13.121 to-ports=5060
add action=masquerade chain=srcnat out-interface=\
    "ether2 - mikrotik a mikrotik"
add action=masquerade chain=srcnat out-interface="Internet Giganet"
add action=masquerade chain=srcnat dst-address=192.168.11.39
add action=masquerade chain=srcnat dst-address=192.168.11.65
add action=masquerade chain=srcnat dst-address=192.168.16.242
add action=masquerade chain=srcnat dst-address=192.168.13.206
add action=masquerade chain=srcnat dst-address=192.168.13.168
add action=masquerade chain=srcnat dst-address=192.168.16.1
add action=masquerade chain=srcnat dst-address=192.168.13.210
add action=masquerade chain=srcnat dst-address=192.168.13.10
add action=masquerade chain=srcnat dst-address=192.168.13.31
add action=passthrough chain=unused-hs-chain comment=\
    "place hotspot rules here" disabled=yes
add action=dst-nat chain=dstnat disabled=yes dst-port=80 protocol=udp \
    to-addresses=192.168.13.161 to-ports=80
add action=masquerade chain=srcnat comment="masquerade hotspot network" \
    disabled=yes dst-address=192.168.13.240
add action=masquerade chain=srcnat comment="masquerade hotspot network" \
    src-address=192.168.10.0/24
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set irc disabled=yes
set h323 disabled=yes
set sip disabled=yes
set udplite disabled=yes
set dccp disabled=yes
/ip hotspot user
add disabled=yes name=admin password=S3ns3t
add name=nasser password=2015 profile=128k server=hotspot1
add name=nasser1 password=nasser1 profile=127k server=hotspot1
add name=abel password=5251183
/ip route
add distance=2 gateway=100.65.0.1 routing-mark=giganet
add check-gateway=ping distance=2 gateway=190.128.138.65 routing-mark=\
    "Tigo internet"
add check-gateway=ping distance=1 gateway=100.65.0.1
add check-gateway=ping distance=1 gateway=100.65.0.1
add check-gateway=ping distance=2 gateway=192.168.199.1
add check-gateway=ping disabled=yes distance=111 dst-address=8.8.4.4/32 \
    gateway=190.128.138.65
add check-gateway=ping disabled=yes distance=111 dst-address=8.8.8.8/32 \
    gateway=190.128.138.65
add check-gateway=ping comment=Familiar distance=1 dst-address=45.60.246.0/24 \
    gateway=190.128.138.65
add check-gateway=ping distance=1 dst-address=143.255.141.0/32 gateway=\
    10.11.1.89
add check-gateway=ping distance=2 dst-address=177.73.101.5/32 gateway=\
    100.64.128.1
add check-gateway=ping comment="comercios bancard pela tigo." distance=1 \
    dst-address=181.40.81.0/24 gateway=190.128.138.65
add check-gateway=ping comment="secure banco continental" distance=1 \
    dst-address=190.104.157.234/32 gateway=190.128.138.65
add check-gateway=ping distance=111 dst-address=190.128.255.146/32 gateway=\
    190.128.138.65
add check-gateway=ping distance=111 dst-address=190.128.255.226/32 gateway=\
    190.128.138.65
add distance=110 dst-address=192.168.4.0/24 gateway=192.168.11.37 scope=20
add distance=110 dst-address=192.168.8.0/24 gateway=192.168.11.10 scope=20
add distance=110 dst-address=192.168.14.140/30 gateway=192.168.11.10 scope=20
add distance=110 dst-address=192.168.20.0/24 gateway=192.168.11.17 scope=20
add distance=110 dst-address=192.168.21.0/24 gateway=192.168.11.17 scope=20
add distance=110 dst-address=192.168.27.0/24 gateway=192.168.11.17 scope=20
add distance=110 dst-address=192.168.59.0/24 gateway=192.168.11.15 scope=20
add distance=110 dst-address=192.168.99.0/24 gateway=192.168.11.10 scope=20
add distance=110 dst-address=192.168.161.0/24 gateway=192.168.11.68 scope=20
add check-gateway=ping comment=Familiar distance=1 dst-address=200.85.35.0/24 \
    gateway=190.128.138.65
add check-gateway=ping comment="Banco continental." distance=1 dst-address=\
    200.85.43.0/24 gateway=190.128.138.65
add check-gateway=ping comment="Banco vision" distance=1 dst-address=\
    200.85.47.0/24 gateway=190.128.138.65
add check-gateway=ping comment=Regional distance=1 dst-address=\
    200.124.120.0/24 gateway=190.128.138.65
add check-gateway=ping comment="COPACO servers" distance=2 dst-address=\
    201.217.53.0/24 gateway=190.128.138.65
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set api disabled=yes
set winbox address="192.168.13.0/24,45.228.137.178/32,45.228.137.179/32,45.228\
    .137.181/32,192.168.11.0/24,192.168.88.0/24,192.168.15.0/24"
set api-ssl disabled=yes
/ip smb shares
set [ find default=yes ] directory=/pub
/ip socks
set port=4145
/ip ssh
set allow-none-crypto=yes forwarding-enabled=remote
/ppp secret
add local-address=192.168.11.104 name=abel password=5251183 profile=\
    default-encryption remote-address=192.168.11.4
add local-address=192.168.11.102 name=Hernandarias password=Nasserttxs2251 \
    profile=default-encryption remote-address=192.168.11.2
add local-address=192.168.11.103 name=NasserCentro password=\
    "&<+@[nhX4o!x\?(UYE>@E4TpZ+" profile=default-encryption remote-address=\
    192.168.11.3
add local-address=192.168.11.105 name=centrovpn password=centrovpn123 \
    profile=default-encryption remote-address=192.168.11.5
add local-address=192.168.11.106 name=zonafranca password=Nasserttxs2251 \
    profile=default-encryption remote-address=192.168.11.6
add local-address=192.168.11.110 name=RecapadoraKM28 password=RecapadoraKM28 \
    profile=default-encryption remote-address=192.168.11.10
add local-address=192.168.11.115 name=Ypanekm28 password=Ypanekm28 profile=\
    default-encryption remote-address=192.168.11.15
add local-address=192.168.11.120 name=nasser password=Nasser135 profile=\
    default-encryption remote-address=192.168.11.20
add local-address=192.168.11.117 name=RecapadoraKM285 password=\
    RecapadoraKM285 profile=default-encryption remote-address=192.168.11.17
add local-address=192.168.11.1 name=nassernb1 password=nasservpn1 profile=\
    comdns remote-address=192.168.11.50
add local-address=192.168.11.131 name=samianote password=samia321 profile=\
    default-encryption remote-address=192.168.11.31
add local-address=192.168.11.132 name=samiacasa password=samiasunset123 \
    profile=default-encryption remote-address=192.168.11.32
add local-address=192.168.11.130 name=abelcasa password=5251183 profile=\
    default-encryption remote-address=192.168.11.30
add local-address=192.168.11.139 name=abelcasa2 password=abelcasa2123 \
    profile=default-encryption remote-address=192.168.11.39
add local-address=192.168.11.149 name=soraia password=soraia1144 profile=\
    default-encryption remote-address=192.168.11.49
add local-address=192.168.11.155 name=nelly password=nelly321 profile=\
    default-encryption remote-address=192.168.11.55
add local-address=192.168.11.157 name=km7 password=sunsetkm7 profile=\
    default-encryption remote-address=192.168.11.57
add local-address=192.168.11.136 name=Luiscentro password=Luiscentro321 \
    profile=default-encryption remote-address=192.168.11.36
add local-address=192.168.11.122 name=Abdo password=Abdo123 profile=\
    default-encryption remote-address=192.168.11.22
add local-address=192.168.11.158 name=YpaneNasser password=YpaneNasser5251183 \
    profile=default-encryption remote-address=192.168.11.58 service=l2tp
add local-address=192.168.11.159 name=raquel password=raquel5599 \
    remote-address=192.168.11.59
add local-address=192.168.11.160 name=sharif password=sharifsunset profile=\
    default-encryption remote-address=192.168.11.60
add local-address=192.168.11.161 name=nabilissa password=nabil552 \
    remote-address=192.168.11.61
add local-address=192.168.11.107 name="Km 12 ZF deposito" password=\
    Nasserttxs2251 profile=default-encryption remote-address=192.168.11.7
add local-address=192.168.11.162 name=NasserZFdeposito password=\
    Nasserttxs2251 profile=default-encryption remote-address=192.168.11.62
add local-address=192.168.11.164 name=haiet password=haiet102030 profile=\
    default-encryption remote-address=192.168.11.64
add local-address=192.168.11.165 name=km12dep password=km12dep444 profile=\
    default-encryption remote-address=192.168.11.65
add local-address=192.168.11.168 name=haietimp password=haiet102030 profile=\
    default-encryption remote-address=192.168.11.68
add local-address=192.168.11.137 name=locadoraNew password=locadoraNew123 \
    profile=default-encryption remote-address=192.168.11.37
add local-address=192.168.11.167 name=YpaneNasser2 password=\
    YpaneNasser5251183 profile=default-encryption remote-address=\
    192.168.11.67
add local-address=192.168.11.169 name=HernardariosGiga password=\
    Nasserttxs2251 profile=default-encryption remote-address=192.168.11.69
add local-address=192.168.11.170 name=NasserZFdeposito password=\
    NasserZFdeposito123 profile=default-encryption remote-address=\
    192.168.11.70 service=l2tp
add local-address=192.168.11.171 name=samia1 password=samia123 profile=\
    default-encryption remote-address=192.168.11.71
add local-address=192.168.11.172 name=haiet2 password=haiet102030 profile=\
    default-encryption remote-address=192.168.11.72
add local-address=192.168.11.173 name=Ramon password=Ramon1235 profile=\
    default-encryption remote-address=192.168.11.73
add local-address=192.168.11.174 name=Km4torre password=Km4torre123 profile=\
    default-encryption remote-address=192.168.11.74
add local-address=192.168.11.1 name=nassernb2 password=nasservpn321 profile=\
    comdns remote-address=192.168.11.51
add local-address=192.168.11.141 name=Nasser password=Ti-nasser2930 profile=\
    default-encryption remote-address=192.168.11.41
add local-address=192.168.11.142 name=Soraia password=Ti-nasser2931 profile=\
    default-encryption remote-address=192.168.11.42
add local-address=192.168.11.143 name=Samia password=Ti-nasser2932 profile=\
    default-encryption remote-address=192.168.11.43
add local-address=192.168.11.144 name=RRHH password=Ti-nasser2933 profile=\
    default-encryption remote-address=192.168.11.44
add local-address=192.168.11.145 name="Informatica " password=Ti-nasser2934 \
    profile=default-encryption remote-address=192.168.11.45
add local-address=192.168.11.156 name=NasserLocadora password=Ti-nasser2935 \
    profile=default-encryption remote-address=192.168.11.56
add local-address=192.168.11.146 name=Samia-2 password=Ti-nasser2935 profile=\
    default-encryption remote-address=192.168.11.46
add local-address=192.168.11.152 name=nasser-3 password=Ti-nasser2936 \
    profile=default-encryption remote-address=192.168.11.52
add local-address=192.168.11.153 name=Nasser-4 password=Ti-nasser2937 \
    profile=default-encryption remote-address=192.168.11.53
add local-address=192.168.11.154 name=CCTV-N password=Ti-nasser2940 profile=\
    default-encryption remote-address=192.168.11.54
add local-address=192.168.11.163 name=Nasser-5 password=Ti-nasser2941 \
    profile=default-encryption remote-address=192.168.11.63
add local-address=192.168.11.166 name=Nasser-6 password=Ti-nasser2942 \
    profile=default-encryption remote-address=192.168.11.66
/routing ospf network
add area=backbone network=192.168.13.0/24
add area=backbone network=192.168.11.0/24
add area=backbone network=192.168.19.0/24
add area=backbone network=192.168.199.0/24
/snmp
set contact=Nasser enabled=yes location=Nasser trap-community=zabbix \
    trap-version=2
/system clock
set time-zone-name=America/Asuncion
/system identity
set name=Nasser-Tigo
/system package update
set channel=upgrade
/tool bandwidth-server
set authenticate=no enabled=no
/tool romon
set enabled=yes
