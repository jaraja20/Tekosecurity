# jul/20/2026 16:26:20 by RouterOS 6.49.15
# software id = PDZX-SLNV
#
# model = RouterBOARD 750G r2
# serial number = 64FC05811D16
/interface bridge
add fast-forward=no name="Nasser Centro"
add name=vpn
/interface ethernet
set [ find default-name=ether1 ] comment="INTERNET TIGO" speed=100Mbps
set [ find default-name=ether2 ] name="ether2- Giganet" speed=100Mbps
set [ find default-name=ether3 ] comment="Rel\F3gio ponto , porta 3" speed=\
    100Mbps
set [ find default-name=ether4 ] speed=100Mbps
set [ find default-name=ether5 ] speed=100Mbps
/interface pppoe-client
add add-default-route=yes default-route-distance=5 disabled=no interface=\
    "ether2- Giganet" name="Internet Giganet" password=22660 use-peer-dns=yes \
    user=24429
/interface pptp-client
add connect-to=190.128.138.66 disabled=no name="Nasser KM6" password=\
    "&<+@[nhX4o!x\?(UYE>@E4TpZ+" user=NasserCentro
add connect-to=45.170.129.97 disabled=no name="VPn via giganet" password=\
    "&<+@[nhX4o!x\?(UYE>@E4TpZ+" user=NasserCentro
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=dhcp_pool0 ranges=192.168.12.20-192.168.12.254
/ip dhcp-server
add address-pool=dhcp_pool0 disabled=no interface="Nasser Centro" lease-time=\
    3d10m name=dhcp1
/snmp community
add addresses=::/0 name=zabbix
/user group
set full policy="local,telnet,ssh,ftp,reboot,read,write,policy,test,winbox,pas\
    sword,web,sniff,sensitive,api,romon,dude,tikapp"
/interface bridge port
add bridge="Nasser Centro" interface=ether4 trusted=yes
add bridge="Nasser Centro" interface=ether5 trusted=yes
add bridge="Nasser Centro" interface=ether3
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface pptp-server server
set enabled=yes
/ip address
add address=190.128.255.226/30 interface=ether1 network=190.128.255.224
add address=192.168.12.1/24 interface="Nasser Centro" network=192.168.12.0
add address=192.168.199.1/24 interface=vpn network=192.168.199.0
add address=192.168.1.1/24 interface="Nasser Centro" network=192.168.1.0
/ip dhcp-client
add disabled=no interface="ether2- Giganet"
/ip dhcp-server lease
add address=192.168.12.250 client-id=1:7c:8b:ca:8e:4:12 mac-address=\
    7C:8B:CA:8E:04:12 server=dhcp1
add address=192.168.12.252 client-id=1:0:25:ab:f:0:b0 mac-address=\
    00:25:AB:0F:00:B0 server=dhcp1
add address=192.168.12.253 client-id=1:dc:e:a1:9d:64:19 mac-address=\
    DC:0E:A1:9D:64:19 server=dhcp1
add address=192.168.12.249 client-id=1:a0:b3:cc:9e:d0:5a mac-address=\
    A0:B3:CC:9E:D0:5A server=dhcp1
add address=192.168.12.248 client-id=1:0:27:22:f2:99:f5 mac-address=\
    00:27:22:F2:99:F5 server=dhcp1
add address=192.168.12.246 comment="relogio ponto" mac-address=\
    08:14:14:A3:9D:B6 server=dhcp1
add address=192.168.12.251 client-id=1:0:25:ab:f:0:6f mac-address=\
    00:25:AB:0F:00:6F server=dhcp1
add address=192.168.12.247 client-id=1:a8:1e:84:15:8f:c1 mac-address=\
    A8:1E:84:15:8F:C1 server=dhcp1
add address=192.168.12.245 client-id=1:9c:b7:d:af:6b:b3 mac-address=\
    9C:B7:0D:AF:6B:B3 server=dhcp1
add address=192.168.12.244 client-id=1:0:12:16:e4:5f:f2 mac-address=\
    00:12:16:E4:5F:F2 server=dhcp1
add address=192.168.12.215 client-id=1:9c:b7:d:af:26:28 mac-address=\
    9C:B7:0D:AF:26:28 server=dhcp1
add address=192.168.12.238 client-id=1:0:e9:3a:a1:11:1 mac-address=\
    00:E9:3A:A1:11:01 server=dhcp1
add address=192.168.12.47 client-id=1:0:b:82:7a:63:10 comment="VOIP APARELHO" \
    mac-address=00:0B:82:7A:63:10 server=dhcp1
add address=192.168.12.21 client-id=1:0:b:82:7a:6c:79 comment="VOIP APARELHO" \
    mac-address=00:0B:82:7A:6C:79 server=dhcp1
add address=192.168.12.23 client-id=1:0:b:82:4e:c1:75 comment="VOIP APARELHO" \
    mac-address=00:0B:82:4E:C1:75 server=dhcp1
/ip dhcp-server network
add address=192.168.12.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.12.1
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4
/ip firewall address-list
add address=0.0.0.0/8 comment=RFC6890 list=NotPublic
add address=10.0.0.0/8 comment=RFC6890 list=NotPublic
add address=100.64.0.0/10 comment=RFC6890 list=NotPublic
add address=127.0.0.0/8 comment=RFC6890 list=NotPublic
add address=169.254.0.0/16 comment=RFC6890 list=NotPublic
add address=172.16.0.0/12 comment=RFC6890 list=NotPublic
add address=192.0.0.0/24 comment=RFC6890 list=NotPublic
add address=192.0.2.0/24 comment=RFC6890 list=NotPublic
add address=192.168.0.0/16 comment=RFC6890 list=NotPublic
add address=192.88.99.0/24 comment=RFC3068 list=NotPublic
add address=198.18.0.0/15 comment=RFC6890 list=NotPublic
add address=198.51.100.0/24 comment=RFC6890 list=NotPublic
add address=203.0.113.0/24 comment=RFC6890 list=NotPublic
add address=224.0.0.0/4 comment=RFC4601 list=NotPublic
add address=240.0.0.0/4 comment=RFC6890 list=NotPublic
/ip firewall filter
add action=accept chain=forward dst-port=5060 log=yes protocol=udp
add action=accept chain=forward dst-port=5060 protocol=tcp
add action=accept chain=output
add action=drop chain=forward content=windowsupdate.microsoft.com
add action=drop chain=input content=windowsupdate.com
add action=drop chain=forward content=windowsupdate.com disabled=yes
add action=drop chain=forward content=update.microsoft.com disabled=yes
add action=drop chain=forward content=windowsupdate.com disabled=yes
add action=accept chain=input dst-address=190.128.255.226 dst-port=161 \
    protocol=tcp src-address=45.228.137.178
add action=accept chain=input dst-address=190.128.255.226 dst-port=161 \
    protocol=udp src-address=45.228.137.178
add action=drop chain=forward src-address=192.168.1.78
add action=drop chain=input dst-port=53 protocol=tcp
add action=drop chain=input dst-port=53 protocol=udp
add action=drop chain=forward comment="drop invalid connections" \
    connection-state=invalid disabled=yes protocol=tcp
add action=accept chain=forward connection-state=established
add action=accept chain=forward comment="allow related connections" \
    connection-state=related
add action=drop chain=forward src-address=0.0.0.0/8
add action=drop chain=forward dst-address=0.0.0.0/8
add action=drop chain=forward src-address=127.0.0.0/8
add action=drop chain=forward dst-address=127.0.0.0/8
add action=drop chain=forward src-address=224.0.0.0/3
add action=drop chain=forward dst-address=224.0.0.0/3
add action=drop chain=forward comment="drop invalid connections" \
    connection-state=invalid disabled=yes protocol=tcp
add action=accept chain=forward connection-state=established
add action=accept chain=forward comment="allow related connections" \
    connection-state=related
add action=drop chain=forward comment="drop invalid connections" \
    connection-state=invalid disabled=yes protocol=tcp
add action=accept chain=forward connection-state=established
add action=accept chain=forward comment="allow related connections" \
    connection-state=related
add chain=input comment="Accept established and related packets" \
    connection-state=established,related
add action=drop chain=input comment="Drop invalid packets" connection-state=\
    invalid disabled=yes
add action=drop chain=input comment=\
    "Drop all packets which are not destined to routes IP address" disabled=\
    yes dst-address-type=!local
add action=drop chain=input comment=\
    "Drop all packets which does not have unicast source IP address" \
    disabled=yes log=yes src-address-type=!unicast
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1
add action=masquerade chain=srcnat out-interface="ether2- Giganet"
add action=masquerade chain=srcnat out-interface="Internet Giganet"
add action=masquerade chain=srcnat disabled=yes dst-address=192.168.12.246
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set irc disabled=yes
set h323 disabled=yes
set sip disabled=yes
set udplite disabled=yes
set dccp disabled=yes
/ip route
add distance=1 gateway=100.65.0.1
add distance=2 gateway=190.128.255.225
add distance=1 dst-address=172.20.99.0/24 gateway=192.168.199.2
add distance=110 dst-address=192.168.88.0/24 gateway=192.168.11.103 scope=20
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh disabled=yes
set api disabled=yes
set api-ssl disabled=yes
/ip ssh
set allow-none-crypto=yes forwarding-enabled=remote
/ppp secret
add local-address=192.168.199.1 name=testeabel123 password=testeabel123 \
    profile=default-encryption remote-address=192.168.199.2
/routing ospf network
add area=backbone network=192.168.12.0/24
add area=backbone network=192.168.11.0/24
/snmp
set contact="nasser centro" enabled=yes location="nasser centro" \
    trap-community=zabbix trap-version=2
/system clock
set time-zone-name=America/Asuncion
/system identity
set name=Nasser-Oasis
/system leds
add interface=ether1 leds="" type=interface-status
/system package update
set channel=upgrade
