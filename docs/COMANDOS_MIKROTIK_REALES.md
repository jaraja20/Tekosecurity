# TEKOSECURE - Comandos Reales por Sucursal

## ✅ IPs y Credenciales Confirmadas

| Sucursal | IP | Usuario | Contraseña |
|---|---|---|---|
| **MATRIZ** | 192.168.13.100 | nasserti | NasserTi73491654 |
| **OASIS** | 192.128.255.226 | nasserti | NasserTi73491654 |
| **KM12** | 192.168.15.1 | nasserti | NasserTi73491654 |
| **HERNANDARIAS** | 192.168.11.69 | nasserti | NasserTi73491654 |

---

## 🚀 COMANDO 1: MATRIZ (192.168.13.100)

**Opción A: Terminal SSH (copiar línea por línea)**

```bash
# Conectar
ssh nasserti@192.168.13.100

# En Terminal Mikrotik, ejecutar:
/system identity set name="TEKOSECURE-MATRIZ_KM6"
/ip dns set servers=8.8.8.8,8.8.4.4 allow-remote-requests=yes
/system ntp client set enabled=yes server-dns-names=pool.ntp.org
/ip address add address=192.168.13.1/24 interface=ether2 comment="LAN MATRIZ_KM6"
/ip dhcp-client add interface=ether1 disabled=no
/ip firewall filter add action=accept chain=input protocol=icmp comment="Allow ping"
/ip firewall filter add action=accept chain=input connection-state=established,related comment="Allow established"
/ip firewall filter add action=accept chain=input in-interface=ether2 comment="Allow from LAN"
/ip firewall filter add action=drop chain=input comment="Drop input default"
/ip firewall filter add action=accept chain=forward connection-state=established,related
/ip firewall filter add action=accept chain=forward in-interface=ether1 out-interface=ether2
/ip firewall filter add action=accept chain=forward in-interface=ether2 out-interface=ether1
/ip firewall filter add action=accept chain=forward protocol=tcp dst-port=22
/ip firewall filter add action=drop chain=forward connection-state=invalid
/ip firewall nat add action=masquerade chain=srcnat out-interface=ether1
/snmp set enabled=yes trap-enabled=yes trap-community=public
```

**Opción B: Subir archivo RSC completo**

```bash
# Desde tu PC
scp scripts/rsc/MATRIZ_KM6_config.rsc nasserti@192.168.13.100:/

# SSH a Matriz
ssh nasserti@192.168.13.100

# En Terminal Mikrotik
/import MATRIZ_KM6_config.rsc
```

---

## 🚀 COMANDO 2: OASIS (192.128.255.226)

**Terminal SSH:**

```bash
# Conectar
ssh nasserti@192.128.255.226

# En Terminal Mikrotik, ejecutar:
/system identity set name="TEKOSECURE-OASIS"
/ip dns set servers=8.8.8.8,8.8.4.4 allow-remote-requests=yes
/system ntp client set enabled=yes server-dns-names=pool.ntp.org
/ip address add address=192.128.255.1/24 interface=ether2 comment="LAN OASIS"
/ip dhcp-client add interface=ether1 disabled=no
/ip firewall filter add action=accept chain=input protocol=icmp comment="Allow ping"
/ip firewall filter add action=accept chain=input connection-state=established,related
/ip firewall filter add action=accept chain=input in-interface=ether2 comment="Allow from LAN"
/ip firewall filter add action=drop chain=input comment="Drop input default"
/ip firewall filter add action=accept chain=forward connection-state=established,related
/ip firewall filter add action=accept chain=forward in-interface=ether1 out-interface=ether2
/ip firewall filter add action=accept chain=forward in-interface=ether2 out-interface=ether1
/ip firewall filter add action=accept chain=forward protocol=tcp dst-port=22,80,443
/ip firewall filter add action=drop chain=forward connection-state=invalid
/ip firewall nat add action=masquerade chain=srcnat out-interface=ether1
/snmp set enabled=yes trap-enabled=yes trap-community=public
```

**O RSC:**

```bash
scp scripts/rsc/OASIS_config.rsc nasserti@192.128.255.226:/
ssh nasserti@192.128.255.226
# En Terminal: /import OASIS_config.rsc
```

---

## 🚀 COMANDO 3: KM12 (192.168.15.1)

**Terminal SSH:**

```bash
# Conectar
ssh nasserti@192.168.15.1

# En Terminal Mikrotik, ejecutar:
/system identity set name="TEKOSECURE-KM12"
/ip dns set servers=8.8.8.8,8.8.4.4 allow-remote-requests=yes
/system ntp client set enabled=yes server-dns-names=pool.ntp.org
/ip address add address=192.168.15.1/24 interface=ether2 comment="LAN KM12"
/ip dhcp-client add interface=ether1 disabled=no
/ip firewall filter add action=accept chain=input protocol=icmp comment="Allow ping"
/ip firewall filter add action=accept chain=input connection-state=established,related
/ip firewall filter add action=accept chain=input in-interface=ether2 comment="Allow from LAN"
/ip firewall filter add action=drop chain=input comment="Drop input default"
/ip firewall filter add action=accept chain=forward connection-state=established,related
/ip firewall filter add action=accept chain=forward in-interface=ether1 out-interface=ether2
/ip firewall filter add action=accept chain=forward in-interface=ether2 out-interface=ether1
/ip firewall filter add action=accept chain=forward protocol=tcp dst-port=22,80,443
/ip firewall filter add action=drop chain=forward connection-state=invalid
/ip firewall nat add action=masquerade chain=srcnat out-interface=ether1
/snmp set enabled=yes trap-enabled=yes trap-community=public
```

**O RSC:**

```bash
scp scripts/rsc/KM12_config.rsc nasserti@192.168.15.1:/
ssh nasserti@192.168.15.1
# En Terminal: /import KM12_config.rsc
```

---

## 🚀 COMANDO 4: HERNANDARIAS (192.168.11.69)

**Terminal SSH:**

```bash
# Conectar
ssh nasserti@192.168.11.69

# En Terminal Mikrotik, ejecutar:
/system identity set name="TEKOSECURE-HERNANDARIAS"
/ip dns set servers=8.8.8.8,8.8.4.4 allow-remote-requests=yes
/system ntp client set enabled=yes server-dns-names=pool.ntp.org
/ip address add address=192.168.11.1/24 interface=ether2 comment="LAN HERNANDARIAS"
/ip dhcp-client add interface=ether1 disabled=no
/ip firewall filter add action=accept chain=input protocol=icmp comment="Allow ping"
/ip firewall filter add action=accept chain=input connection-state=established,related
/ip firewall filter add action=accept chain=input in-interface=ether2 comment="Allow from LAN"
/ip firewall filter add action=drop chain=input comment="Drop input default"
/ip firewall filter add action=accept chain=forward connection-state=established,related
/ip firewall filter add action=accept chain=forward in-interface=ether1 out-interface=ether2
/ip firewall filter add action=accept chain=forward in-interface=ether2 out-interface=ether1
/ip firewall filter add action=accept chain=forward protocol=tcp dst-port=22,80,443
/ip firewall filter add action=drop chain=forward connection-state=invalid
/ip firewall nat add action=masquerade chain=srcnat out-interface=ether1
/snmp set enabled=yes trap-enabled=yes trap-community=public
```

**O RSC:**

```bash
scp scripts/rsc/HERNANDARIAS_config.rsc nasserti@192.168.11.69:/
ssh nasserti@192.168.11.69
# En Terminal: /import HERNANDARIAS_config.rsc
```

---

## ✅ VERIFICAR CONFIGURACIÓN

Después de aplicar en cada MK, ejecuta esto para verificar:

```bash
# Ver identidad (nombre del MK)
/system identity print

# Ver IPs
/ip address print

# Ver reglas firewall (debe haber ~10 nuevas)
/ip firewall filter print

# Ver NAT
/ip firewall nat print

# Ver SNMP
/snmp print

# Ver logs
/system logging print
```

---

## 🔐 ACCIONES AUTOMÁTICAS QUE EJECUTARÁ TEKOSECURE

Una vez configurados, cuando detecte un ataque, TEKOSECURE hará:

### **Bloquear IP en TODAS las sucursales**

```bash
# Automático desde TEKOSECURE
ssh nasserti@192.168.13.100
ssh nasserti@192.128.255.226
ssh nasserti@192.168.15.1
ssh nasserti@192.168.11.69

# En cada uno ejecutar:
/ip firewall filter add action=drop chain=input src-address=192.168.1.50 comment="BLOCKED: Brute Force"
/ip firewall filter add action=drop chain=forward src-address=192.168.1.50 comment="BLOCKED: Brute Force"
```

### **Limitar BW de atacante**

```bash
/queue simple add name="limit_192.168.1.50" target-address=192.168.1.50 max-limit=64k/64k comment="Rate limit"
```

### **Crear regla temporal (auto-expira en 24h)**

```bash
/ip firewall filter add action=drop chain=input src-address=192.168.1.50 disabled-time=24h comment="Temporary - 24h"
```

---

## 📊 INTEGRACIÓN TEKOSECURE

El `backend/mikrotik_actions.py` ahora conectará con:
- ✅ nasserti @ 192.168.13.100
- ✅ nasserti @ 192.128.255.226
- ✅ nasserti @ 192.168.15.1
- ✅ nasserti @ 192.168.11.69

Y ejecutará acciones automáticamente cuando:
- Se detecte ataque CRITICAL
- Operador haga click en "Bloquear IP"
- Sistema ejecute playbooks

---

**TEKOSECURE v1.0 - Centro de Seguridad Operacional** 🔐
