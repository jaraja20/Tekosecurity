# TEKOSECURE - Leer Configuración Actual (SIN MODIFICAR NADA)

⚠️ **IMPORTANTE:** Estos comandos SOLO LEEN. No modifican nada.

---

## 🔍 Comandos para Auditar (LECTURA PURA)

### MATRIZ KM6 (192.168.13.100)

```bash
ssh nasserti@192.168.13.100

# Una vez conectado, ejecuta SOLO estos comandos (copiar uno por uno):

/system identity print
/system package print
/ip address print
/ip route print
/ip firewall filter print
/ip firewall nat print
/ip dns print
/ip dhcp-server print
/interface print
/snmp print
/system ntp client print
```

**Guarda el output en un archivo:**
```bash
# Desde tu PC, redirecciona a archivo:
ssh nasserti@192.168.13.100 "/system identity print; /ip address print; /ip firewall filter print" > MATRIZ_KM6_config.txt
```

---

### OASIS (192.128.255.226)

```bash
ssh nasserti@192.128.255.226

# Comandos de lectura:
/system identity print
/ip address print
/ip firewall filter print
/ip firewall nat print
/ip dns print
/interface print
```

---

### KM12 (192.168.15.1)

```bash
ssh nasserti@192.168.15.1

# Comandos de lectura:
/system identity print
/ip address print
/ip firewall filter print
/ip firewall nat print
/ip dns print
/interface print
```

---

### HERNANDARIAS (192.168.11.69)

```bash
ssh nasserti@192.168.11.69

# Comandos de lectura:
/system identity print
/ip address print
/ip firewall filter print
/ip firewall nat print
/ip dns print
/interface print
```

---

## 📋 Qué Verificar (SIN CAMBIAR)

✅ **Identidad** - Nombre actual del MK
✅ **IPs** - Qué direcciones tiene asignadas
✅ **Firewall** - Qué reglas ya existen
✅ **NAT** - Qué reglas de traducción tiene
✅ **DNS** - Servidores configurados
✅ **Interfaces** - Estado de conexiones
✅ **Rutas** - Cómo enruta el tráfico

---

## 🛡️ ¿Por qué solo lectura?

1. **No cortamos internet** - Sin cambios = sin riesgo
2. **Documentamos estado actual** - Base para cambios futuros
3. **Comparamos después** - Vemos qué cambió
4. **Rollback seguro** - Si algo sale mal, sabemos cómo estaba

---

## 📊 Guardar Resultados

Para cada MK, ejecuta esto desde tu PC:

```bash
# MATRIZ
ssh nasserti@192.168.13.100 "
echo '=== IDENTIDAD ==='; /system identity print;
echo '=== DIRECCIONES IP ==='; /ip address print;
echo '=== FIREWALL FILTER ==='; /ip firewall filter print;
echo '=== FIREWALL NAT ==='; /ip firewall nat print;
echo '=== DNS ==='; /ip dns print;
echo '=== INTERFACES ==='; /interface print;
" > scripts/audit_results/MATRIZ_KM6_actual.txt

# OASIS
ssh nasserti@192.128.255.226 "
echo '=== IDENTIDAD ==='; /system identity print;
echo '=== DIRECCIONES IP ==='; /ip address print;
echo '=== FIREWALL FILTER ==='; /ip firewall filter print;
echo '=== FIREWALL NAT ==='; /ip firewall nat print;
echo '=== DNS ==='; /ip dns print;
echo '=== INTERFACES ==='; /interface print;
" > scripts/audit_results/OASIS_actual.txt

# KM12
ssh nasserti@192.168.15.1 "
echo '=== IDENTIDAD ==='; /system identity print;
echo '=== DIRECCIONES IP ==='; /ip address print;
echo '=== FIREWALL FILTER ==='; /ip firewall filter print;
echo '=== FIREWALL NAT ==='; /ip firewall nat print;
echo '=== DNS ==='; /ip dns print;
echo '=== INTERFACES ==='; /interface print;
" > scripts/audit_results/KM12_actual.txt

# HERNANDARIAS
ssh nasserti@192.168.11.69 "
echo '=== IDENTIDAD ==='; /system identity print;
echo '=== DIRECCIONES IP ==='; /ip address print;
echo '=== FIREWALL FILTER ==='; /ip firewall filter print;
echo '=== FIREWALL NAT ==='; /ip firewall nat print;
echo '=== DNS ==='; /ip dns print;
echo '=== INTERFACES ==='; /interface print;
" > scripts/audit_results/HERNANDARIAS_actual.txt
```

---

## ✅ Checklist Seguro

- [ ] Leo configuración de MATRIZ
- [ ] Leo configuración de OASIS
- [ ] Leo configuración de KM12
- [ ] Leo configuración de HERNANDARIAS
- [ ] Guardo archivos de resultado
- [ ] Verifico que todo funciona (ping, internet, etc.)
- [ ] Documentación está lista
- [ ] **NADA FUE MODIFICADO**

---

## 🚀 Próximo Paso (DESPUÉS de leer)

Una vez que tengamos la configuración actual documentada:

1. Analizamos qué reglas ya existen
2. Creamos un plan de cambios SEGUROS
3. Hacemos cambios **UNO A LA VEZ** (no todos juntos)
4. Verificamos que internet sigue funcionando
5. Si algo falla, revertimos (sabemos cómo estaba)

---

**TEKOSECURE v1.0** 🔐
**Estado: Auditoría Segura (SOLO LECTURA)**
