# 📊 ANÁLISIS COMPARATIVO - 4 SUCURSALES

**Fecha:** 20 Jul 2026
**Archivos:** matriz_config.rsc, oasis_config.rsc, km12_config.rsc, hernandarias_config.rsc

---

## 🏢 RESUMEN EJECUTIVO

| Parámetro | MATRIZ | OASIS | KM12 | HERNANDARIAS |
|---|---|---|---|---|
| **Modelo** | RB760iGS | 750G r2 | ? | ? |
| **RouterOS** | 6.49.10 | 6.49.15 | ? | ? |
| **Internet** | PPPoE (ether5) | PPPoE (ether2) | ? | ? |
| **Red Principal** | 192.168.13.x | 192.168.12.x | ? | ? |
| **VPN Servers** | L2TP + PPTP | PPTP Client | ? | ? |
| **DHCP** | 3 pools | 1 pool | ? | ? |
| **Hotspot** | Sí | No | ? | ? |
| **OSPF** | Sí (Router) | No | ? | ? |
| **Tamaño Config** | 26 KB | 8.9 KB | 8.6 KB | 13 KB |

---

## 🌐 TOPOLOGÍA DE RED

```
                    INTERNET (Giganet)
                          |
                    ┌─────┴─────┐
                    |           |
              MATRIZ KM6    OASIS
            (192.168.13.x) (192.168.12.x)
                    |           |
                    └─────┬─────┘
                          |
            ┌─────────────┼─────────────┐
            |             |             |
          KM12      HERNANDARIAS    (OTROS)
      (192.168.x) (192.168.11.x)
```

---

## 📡 CONECTIVIDAD ENTRE SUCURSALES

### MATRIZ KM6
- **VPN Servers:** L2TP + PPTP
- **Conexiones aceptadas de:**
  - Hernandarias (L2TP)
  - Recapadora KM28 (L2TP + PPTP)
  - Ypane (L2TP)
  - Zona Franca (L2TP)

### OASIS
- **VPN Clients:** PPTP
- **Conexiones a:**
  - Matriz KM6 (connect-to: 190.128.138.66)
  - VPN via Giganet (connect-to: 45.170.129.97)
- **Rol:** Cliente de VPN (recibe del Matriz)

### KM12
- Configuración: TBD (revisar archivo)

### HERNANDARIAS
- Configuración: TBD (revisar archivo)

---

## 🔒 Seguridad & Firewall

### MATRIZ
```
✓ Connection Tracking: HABILITADO
  - TCP Timeout: 5 minutos
  - Estados: established, related, invalid tracked
✓ Firewall Rules: Presentes (ver archivo)
```

### OASIS
```
- Sin firewall rules documentadas
- Solo bridges y routing
```

---

## 📍 Redes Locales Detectadas

### MATRIZ
- **192.168.13.0/24** (Red Principal Nasser)
  - DHCP: 192.168.13.1-99, 101-199
  - Lease: 3d10m
  
- **192.168.10.0/24** (WiFi Visitante - Hotspot)
  - DHCP: 192.168.10.20-254
  - Lease: 1d
  - Hotspot Profile: hsprof1
  
- **192.168.19.0/24** (Secundaria)
  - DHCP: 192.168.19.2-254
  - Lease: 3d10m

### OASIS
- **192.168.12.0/24** (Nasser Centro - PRINCIPAL)
  - DHCP: 192.168.12.20-254
  - Lease: 3d10m
  - IP Reservadas: 245-254 (dispositivos específicos)
  - VoIP: 192.168.12.21, 192.168.12.47

- **192.168.199.0/24** (VPN)
  - Red virtual para túneles VPN

- **192.168.1.0/24** (Secundaria)
  - Red adicional en Nasser Centro

- **190.128.255.226/30** (Internet - Tigo)
  - IP pública del enlace internet

---

## 🔌 Interfaces & Conexiones

### MATRIZ (5 puertos Ethernet)
- ether1: Red Principal (192.168.13.x)
- ether2: P2P a otro MK (mikrotik a mikrotik)
- ether3: WiFi Visitante (Hotspot)
- ether4-5: Uso mixto

### OASIS (5 puertos Ethernet)
- ether1: Internet Tigo (PPPoE)
- ether2: Giganet (Internet respaldo)
- ether3: Relógio ponto (P2P)
- ether4-5: Bridge (Nasser Centro)

---

## 🚀 Servicios Activos

### MATRIZ
✅ PPPoE Client (Internet Giganet)
✅ L2TP Server (VPN entrante)
✅ PPTP Server (VPN entrante)
✅ DHCP Servers (x3)
✅ Hotspot Portal
✅ OSPF Routing
✅ SNMP Monitoring
✅ Queue Management (PCQ)
✅ Connection Tracking
✅ Firewall

### OASIS
✅ PPPoE Client (Internet)
✅ PPPoE DHCPClient (respaldo?)
✅ PPTP Client (VPN saliente a Matriz)
✅ DHCP Server (x1)
✅ Bridge (Nasser Centro)
✅ SNMP Community (Zabbix)

---

## ⚠️ OBSERVACIONES IMPORTANTES

### Puntos Clave

1. **MATRIZ es el "Hub"**
   - Acepta conexiones VPN de otros puntos
   - Distribuye internet
   - Tiene OSPF (routing dinámico)

2. **OASIS es "Cliente"**
   - Se conecta a Matriz via VPN PPTP
   - Recibe internet desde Matriz
   - Distribúye a oficina local

3. **KM12 & HERNANDARIAS**
   - Probablemente similar a OASIS (clientes)
   - Están en VPN a Matriz

4. **Internet Redundante**
   - Matriz: Giganet (ether5)
   - Oasis: Giganet (ether2) + Tigo (ether1)
   - Backup entre proveedores

### Configuración de Monitoreo

- SNMP Zabbix configurado en Matriz
- SNMP Zabbix configurado en Oasis
- Probablemente en otros también

---

## 🔐 IMPLICACIONES PARA TEKOSECURE

### 1. Monitoreo

✅ SNMP ya está configurado (Zabbix)
✅ Podemos integrar con TEKOSECURE
✅ Alertas SNMP para cambios

### 2. Firewall

⚠️ MATRIZ tiene firewall activo
⚠️ Necesitamos ser cuidadoso con cambios
✅ Connection Tracking activo = seguro

### 3. Bloqueo de IPs

🟢 MATRIZ: Agregar reglas firewall ✓
🟡 OASIS: Ver si tiene firewall rules
🟡 KM12: TBD
🟡 HERNANDARIAS: TBD

### 4. VPN

⚠️ No tocar L2TP/PPTP servers
✅ Son críticos para conectar sucursales
✅ Si cae Matriz, todas las sucursales se desconectan

---

## 📋 PRÓXIMO PASO

1. ✅ Analizar completo KM12_config.rsc
2. ✅ Analizar completo HERNANDARIAS_config.rsc
3. ✅ Documentar firewall rules de cada uno
4. ✅ Crear plan de integración TEKOSECURE
5. ✅ Definir dónde agregar reglas de bloqueo

---

## 📌 RESUMEN PARA TEKOSECURE

```
MATRIZ:
  - Hub VPN (servidor)
  - Internet principal
  - Firewall activo
  → BLOQUEAR IPs: agregar en firewall filter

OASIS:
  - Cliente VPN
  - Internet secundario (respaldo)
  - Menos crítico que Matriz
  → BLOQUEAR IPs: agregar en firewall filter (si existe)

KM12:
  - Probablemente cliente
  → Revisar archivo completo

HERNANDARIAS:
  - Probablemente cliente
  → Revisar archivo completo

ESTRATEGIA SEGURA:
  - Cambios UNO por UNO
  - Matriz primero (principal)
  - Luego sucursales (clientes)
  - Verificar conectividad VPN después de cada cambio
```

---

**TEKOSECURE - Análisis Real en Producción** 🔐
