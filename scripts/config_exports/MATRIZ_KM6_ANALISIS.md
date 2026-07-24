# MATRIZ KM6 - Análisis de Configuración Actual

**Archivo analizado:** AuditoriaCompleta.rsc
**Fecha:** jul/14/2026
**Modelo:** RB760iGS
**Serial:** HE508QTHVAZ
**RouterOS:** 6.49.10

---

## 📊 RESUMEN DE CONFIGURACIÓN

### Interfaces de Red

| Nombre | Alias | Tipo | Speed | Propósito |
|---|---|---|---|---|
| ether1 | - | Ethernet | 100Mbps | Red principal (192.168.13.x) |
| ether2 | ether2 - mikrotik a mikrotik | Ethernet | 100Mbps | Punto a punto (P2P) |
| ether3 | ether3 - REDE WIRELESS VISITANTE | Ethernet | 100Mbps | Red WiFi Visitante |
| ether4 | ether4 | Ethernet | 100Mbps | Secundaria |
| ether5 | ether5-Internet Giganet | Ethernet | 100Mbps | **Internet (PPPoE) ← CRÍTICO** |

### Conexión a Internet

```
ISP: Giganet (Tigo)
Tipo: PPPoE
Interface: ether5 (Internet Giganet)
Usuario: 7057
DNS: Automático (use-peer-dns=yes)
Default Route: Distance 5
Status: ✓ ACTIVO
```

### Redes Locales

| Red | Interface | Propósito | Pool DHCP |
|---|---|---|---|
| 192.168.13.0/24 | ether1 | **Red Principal** | 192.168.13.1-192.168.13.99 y 101-199 |
| 192.168.10.0/24 | ether3 | Hotspot WiFi Visitante | 192.168.10.20-192.168.10.254 |
| 192.168.19.0/24 | ether4 | Red secundaria | 192.168.19.2-192.168.19.254 |

### DHCP Servers

| Nombre | Interface | Pool | Lease | Status |
|---|---|---|---|---|
| dhcp1 | ether3 (WiFi Visitante) | pool1 (192.168.10.x) | 1d | Activo |
| dhcp2 | ether4 | pool2 (192.168.19.x) | 3d10m | Activo |
| dhcp3 | ether1 (Principal) | pool3 (192.168.13.x) | 3d10m | Activo |

---

## 🔗 VPN Servers (Conexiones Remotas)

### L2TP Server (Tunnel Layer 2)

Túneles VPN activos para:
- Hernandarias
- Recapadora KM 28
- Ypane Nasser
- Ypane km28
- Zona Franca

### PPTP Server (Point-to-Point)

Conexiones VPN para:
- Nasser Centro
- Recapadora KM28
- Recapadora KM285
- KM7
- nasser

**Nota:** Estos son túneles VPN que conectan otras sucursales a Matriz

---

## 🔒 Firewall & Seguridad

### Connection Tracking

```
Estado: HABILITADO
TCP Established Timeout: 5 minutos
Conexiones: Trackeadas (established, related, invalid)
```

### Firewall Rules

⚠️ **NO especificadas en el archivo** - Probablemente en secciones no mostradas

---

## 📡 Routing & OSPF

### OSPF (Open Shortest Path First)

```
Router ID: 192.168.13.1
Status: Configurado
Propósito: Enrutamiento dinámico entre sucursales
```

---

## ⏱️ Control de Ancho de Banda

### Queues (Limitadores)

```
queue1: 192.168.13.90/32 → max 564k/564k
queue2: 192.168.19.254/32 → max 4M/4M

Ecualizador_Red_13: 192.168.13.0/24 → max 20M/130M (DESHABILITADO)
Ecualizador_Hotspot_10: 192.168.10.0/24 → max 20M/130M (DESHABILITADO)
```

### PCQ (Per Connection Queuing)

```
PCQ-Subida: Clasificación por IP origen
PCQ-Bajada: Clasificación por IP destino
```

---

## 🔥 Hotspot (Portal Cautivo)

```
Nombre: hotspot1
Interface: ether3 (WiFi Visitante)
Dirección: 192.168.1.1
DNS: nasserdns.dns.com
Perfiles de usuario:
  - 128k: 128k/128k limitado (10 usuarios simultáneos)
  - 127k: 128k/128k limitado (5 usuarios simultáneos)
```

---

## 📊 Monitoreo & Logging

### SNMP (Simple Network Management Protocol)

```
Community públicas:
  - default (0.0.0.0/0)
  - zabbix (::/0)
```

### Logging

```
Memory: 100 líneas
Disk: 100 líneas por archivo (log)
Topics: firewall, account, system, network
```

---

## 🔐 IPSec

```
Algoritmos de encriptación: 3DES (ANTIGUO - considerar actualizar)
```

---

## ⚠️ OBSERVACIONES IMPORTANTES

### ✓ Lo que funciona bien

1. **PPPoE activo** - Internet disponible vía Giganet
2. **VPN configurada** - Conexiones a otras sucursales establecidas
3. **DHCP funcional** - Distribución de IPs automática
4. **Routing dinámico** - OSPF permite comunicación entre sucursales
5. **Monitoreo** - SNMP configurado (Zabbix)

### ⚠️ Áreas de mejora

1. **3DES deprecado** - IPSec usa algoritmo antiguo (considerar AES)
2. **Firewall no documentado** - No se ven las reglas en este export
3. **Queues deshabilitados** - Ecualizador_Red_13 y Ecualizador_Hotspot_10 están OFF
4. **DNS hardcodeado** - nasserdns.dns.com en hotspot (¿aún válido?)
5. **Sin logging centralizado** - Solo en memory/disk del MK

---

## 🛠️ Información Técnica

### Hardware

```
Modelo: RB760iGS (Routerboard con switch integrado)
Puertos: 5 Ethernet + 1 SFP
Memoria: ~256MB RAM
```

### Software

```
RouterOS: 6.49.10
Software ID: PV47-1I5C
Licencia: Profesional (soporta L2TP, PPTP, OSPF)
```

---

## 📋 Próximos Pasos

1. **Exportar configuración de otras 3 sucursales** (OASIS, KM12, HERNANDARIAS)
2. **Comparar**: ¿Son iguales? ¿Qué es diferente?
3. **Documentar**: Qué firewall rules necesita TEKOSECURE
4. **Planificar**: Cambios seguros (sin desconectar internet)
5. **Integrar**: TEKOSECURE con configuración real

---

## 🔄 Próximo: Exportar Otras Sucursales

Ver: `docs/EXPORTAR_CONFIG_DESDE_MK.md`

```bash
ssh nasserti@192.128.255.226 "/export terse" > OASIS_config_actual.rsc
ssh nasserti@192.168.15.1 "/export terse" > KM12_config_actual.rsc
ssh nasserti@192.168.11.69 "/export terse" > HERNANDARIAS_config_actual.rsc
```

---

**TEKOSECURE - Análisis de configuración real**
**NO se modificó nada, solo se documentó.** ✓
