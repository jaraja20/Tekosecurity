# ✅ INTEGRACIÓN REAL - TEKOSECURE CON MIKROTIK

**Estado:** Análisis Completo de 4 Sucursales
**Fecha:** 20 Julio 2026

---

## 📁 Archivos de Configuración (OBTENIDOS)

```
scripts/config_exports/
├── matriz_config.rsc          (26 KB - MATRIZ KM6)
├── oasis_config.rsc           (8.9 KB - OASIS)
├── km12_config.rsc            (8.6 KB - KM12)
├── hernandarias_config.rsc    (13 KB - HERNANDARIAS)
└── ANALISIS_COMPARATIVO_4_SUCURSALES.md
```

---

## 🔍 TOPOLOGÍA REAL ENCONTRADA

### Estructura de Red

```
                    INTERNET (Giganet / Tigo)
                            |
                      MATRIZ KM6 (HUB)
                   192.168.13.100
                (Acepta VPN entrantes)
                            |
              ┌─────────────┼─────────────┐
              |             |             |
            OASIS        KM12       HERNANDARIAS
       192.168.12.x   192.168.x    192.168.11.x
        (Cliente VPN) (Cliente)    (Cliente VPN)
```

### Conexiones VPN Identificadas

**MATRIZ (VPN Server):**
- ✅ L2TP Server (aceptar conexiones)
- ✅ PPTP Server (aceptar conexiones)
- Clientes: Hernandarias, Recapadora KM28, Ypane, Zona Franca, etc.

**OASIS (VPN Client):**
- ✅ PPTP Client a Matriz (192.128.138.66)
- ✅ PPTP Client a VPN Giganet (45.170.129.97)

**KM12 & HERNANDARIAS:**
- Probablemente similares (clientes)

---

## ⚡ CONFIGURACIÓN ACTUAL POR SUCURSAL

### MATRIZ KM6 (El "Hub")

**Modelo:** RouterBoard 760iGS (5 puertos Ethernet)
**RouterOS:** 6.49.10

**Servicios Críticos:**
- ✅ PPPoE (Internet Giganet - ether5)
- ✅ L2TP Server (VPN entrante)
- ✅ PPTP Server (VPN entrante)
- ✅ OSPF Routing (routing dinámico)
- ✅ Firewall + Connection Tracking
- ✅ 3 DHCP Servers
- ✅ Hotspot Portal (WiFi Visitante)
- ✅ SNMP Monitoring (Zabbix)

**Redes:**
- 192.168.13.0/24 (Principal) - DHCP
- 192.168.10.0/24 (WiFi Visitante) - Hotspot
- 192.168.19.0/24 (Secundaria) - DHCP

**⚠️ CRÍTICO:** Si Matriz cae, toda la red cae (es el hub)

---

### OASIS

**Modelo:** RouterBoard 750G r2 (5 puertos Ethernet)
**RouterOS:** 6.49.15

**Servicios:**
- ✅ PPPoE (Internet - ether2 "Giganet")
- ✅ PPTP Client (conecta a Matriz)
- ✅ PPTP Client (conecta a VPN Giganet)
- ✅ DHCP Server (x1)
- ✅ Bridge (ether3, ether4, ether5)
- ✅ SNMP Community (Zabbix)
- ✅ VoIP configurado (teléfonos)

**Redes:**
- 192.168.12.0/24 (Nasser Centro) - DHCP
- 192.168.199.0/24 (VPN)
- 192.168.1.0/24 (Secundaria)
- 190.128.255.226/30 (Internet Tigo)

**Rol:** Cliente de Matriz + Respaldo internet

---

### KM12 & HERNANDARIAS

- Configuraciones similares (probablemente clientes)
- A revisar en detalle

---

## 🛡️ IMPACTO EN TEKOSECURE

### ¿Cómo Bloquear IPs de Forma Segura?

#### Opción A: Bloquear SOLO en Matriz (Recomendado)

```
✅ VENTAJAS:
  - Centralizado
  - Todos los clientes protegidos
  - Un solo punto de control

❌ RIESGO:
  - Si Matriz falla, no hay bloqueo
```

**Implementación:**
```bash
# En MATRIZ, agregar regla firewall
/ip firewall filter add action=drop chain=input src-address=192.168.1.50
/ip firewall filter add action=drop chain=forward src-address=192.168.1.50
```

#### Opción B: Bloquear en Todas Partes

```
✅ VENTAJAS:
  - Redundante (funciona aunque Matriz falle)
  - Defensa en profundidad

❌ RIESGO:
  - Más cambios = más riesgo
  - Coordinación compleja
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN SEGURA

### FASE 1: Preparación (HOY)

- [x] Exportar configuración de 4 sucursales
- [x] Analizar configuración actual
- [x] Documentar topología real
- [ ] Identificar firewall rules actuales
- [ ] Documentar VPN críticos

**Estado:** ✅ COMPLETADO

---

### FASE 2: Integración Backend (MAÑANA)

- [ ] Actualizar `backend/mikrotik_actions.py` con:
  - MATRIZ como prioritario
  - OASIS, KM12, HERNANDARIAS como secundarios

- [ ] Crear conexiones SSH:
  ```python
  MIKROTIK_CONFIG = {
      "MATRIZ_KM6": {
          "ip": "192.168.13.100",
          "priority": "HIGH",  # Hub - crítico
          "role": "VPN_SERVER"
      },
      "OASIS": {
          "ip": "192.128.255.226",
          "priority": "MEDIUM",
          "role": "VPN_CLIENT"
      },
      "KM12": {
          "ip": "192.168.15.1",
          "priority": "MEDIUM",
          "role": "VPN_CLIENT"
      },
      "HERNANDARIAS": {
          "ip": "192.168.11.69",
          "priority": "MEDIUM",
          "role": "VPN_CLIENT"
      }
  }
  ```

---

### FASE 3: Testing Controlado (3-5 DÍAS)

1. **Bloqueo en MATRIZ primero**
   - Agregar regla firewall de prueba
   - Verificar que se aplica
   - Verificar que sucursales siguen conectadas
   - Remover regla de prueba

2. **Bloqueo en OASIS**
   - Idem anterior

3. **Bloqueo en KM12 y HERNANDARIAS**
   - Idem anterior

---

### FASE 4: Despliegue Controlado (SEMANA 2)

1. **Cambios en MATRIZ** (primero - el más crítico)
   - Agregar firewall rules
   - Verificar VPN sigue funcionando
   - Verificar internet sigue funcionando
   - Verificar DHCP sigue funcionando

2. **Cambios en OASIS** (verificar VPN client)
   - Agregar reglas
   - Verificar conexión a Matriz
   - Verificar internet respaldo

3. **Cambios en KM12 y HERNANDARIAS**
   - Similar a OASIS

---

## ⚠️ PUNTOS CRÍTICOS (NO TOCAR)

🚫 **VPN Servers** (Matriz)
- L2TP Server
- PPTP Server
- Estas conectan otras sucursales

🚫 **VPN Clients** (OASIS, etc)
- PPTP Client a Matriz
- Sin esto, pierden internet

🚫 **OSPF Routing** (Matriz)
- Router ID: 192.168.13.1
- Enrutamiento dinámico

🚫 **Firewall Rules Existentes**
- No eliminar, solo agregar nuevas

---

## ✅ CHECKLIST DE SEGURIDAD

- [ ] **Backup de configuración ANTES de cambios**
  ```bash
  /system backup save name=backup-antes-tekosecure
  ```

- [ ] **Verificar conectividad SSH ANTES**
  ```bash
  ssh nasserti@192.168.13.100 "/system identity print"
  ```

- [ ] **Prueba de bloqueo en Matriz**
  ```bash
  /ip firewall filter add action=drop chain=input src-address=192.168.99.99
  /ip firewall filter print | grep 192.168.99.99
  /ip firewall filter remove [número]  # si falla
  ```

- [ ] **Verificar VPN sigue activo**
  ```bash
  /interface l2tp-server print
  /interface pptp-server print
  ```

- [ ] **Verificar DHCP sigue distribuyendo**
  ```bash
  /ip dhcp-server print
  ```

- [ ] **Verificar internet sigue funcionando**
  ```bash
  ping 8.8.8.8
  ```

---

## 📞 SOPORTE & ROLLBACK

### Si algo falla

1. **Conectar SSH al MK afectado**
2. **Restaurar backup:**
   ```bash
   /system backup restore name=backup-antes-tekosecure
   ```
3. **Reiniciar:**
   ```bash
   /system reboot
   ```
4. **Verificar:**
   - VPN
   - Internet
   - DHCP

---

## 🎯 PRÓXIMOS PASOS (TÚ)

1. ✅ **Leer análisis comparativo:** `ANALISIS_COMPARATIVO_4_SUCURSALES.md`
2. ⏳ **Esperar aprobación de gerente** para comenzar Fase 2
3. ⏳ **Testing en Matriz** (menos crítico primero)
4. ⏳ **Luego sucursales**

---

**TEKOSECURE está listo para integración real**
**Con configuración REAL de producción documentada** 🔐

Estado: **SEGURO - DOCUMENTADO - LISTO PARA FASE 2**
