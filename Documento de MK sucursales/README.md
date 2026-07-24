# TEKOSECURE - Documentación Mikrotik por Sucursal

## 📁 Estructura

```
Documento de MK sucursales/
├── MATRIZ_KM6/
│   ├── 1_CONECTAR.txt      (SSH credentials y cómo conectar)
│   ├── 2_COMANDOS.txt      (Comandos para copiar y pegar)
│   └── 3_VERIFICAR.txt     (Verificar que la config quedó bien)
│
├── OASIS/
│   ├── 1_CONECTAR.txt
│   ├── 2_COMANDOS.txt
│   └── 3_VERIFICAR.txt
│
├── KM12/
│   ├── 1_CONECTAR.txt
│   ├── 2_COMANDOS.txt
│   └── 3_VERIFICAR.txt
│
└── HERNANDARIAS/
    ├── 1_CONECTAR.txt
    ├── 2_COMANDOS.txt
    └── 3_VERIFICAR.txt
```

---

## 🚀 CÓMO USAR

### Para cada sucursal, sigue estos 3 pasos:

**PASO 1: Conectar**
- Abre `1_CONECTAR.txt`
- Lee las credenciales
- Conecta: `ssh nasserti@IP`
- Ingresa la contraseña

**PASO 2: Ejecutar comandos**
- Abre `2_COMANDOS.txt`
- Copia UNO de los comandos
- Pega en la terminal Mikrotik
- Presiona ENTER
- Repite con el siguiente comando

**PASO 3: Verificar**
- Abre `3_VERIFICAR.txt`
- Ejecuta cada comando de verificación
- Confirma que los valores coinciden

---

## 📋 IPs y Credenciales

| Sucursal | IP | Usuario | Password |
|---|---|---|---|
| **MATRIZ_KM6** | 192.168.13.100 | nasserti | NasserTi73491654 |
| **OASIS** | 192.128.255.226 | nasserti | NasserTi73491654 |
| **KM12** | 192.168.15.1 | nasserti | NasserTi73491654 |
| **HERNANDARIAS** | 192.168.11.69 | nasserti | NasserTi73491654 |

---

## ✅ Flujo Recomendado

1. **Matriz KM6** (principal)
   ```
   MATRIZ_KM6/1_CONECTAR.txt → 2_COMANDOS.txt → 3_VERIFICAR.txt
   ```

2. **Oasis**
   ```
   OASIS/1_CONECTAR.txt → 2_COMANDOS.txt → 3_VERIFICAR.txt
   ```

3. **KM12**
   ```
   KM12/1_CONECTAR.txt → 2_COMANDOS.txt → 3_VERIFICAR.txt
   ```

4. **Hernandarias**
   ```
   HERNANDARIAS/1_CONECTAR.txt → 2_COMANDOS.txt → 3_VERIFICAR.txt
   ```

---

## 🔐 Qué se configura

✅ **Identidad** - Nombre identificador del MK
✅ **DNS** - Servidores (8.8.8.8, 8.8.4.4)
✅ **NTP** - Sincronización de hora
✅ **Interfaces** - IPs LAN/WAN
✅ **Firewall Input** - Protege acceso al MK
✅ **Firewall Forward** - Protege tráfico interno
✅ **NAT** - Enrutamiento de tráfico
✅ **SNMP** - Monitoreo remoto
✅ **SSH** - Acceso seguro (puerto 22)

---

## 🛡️ Acciones que ejecutará TEKOSECURE

Una vez configurados, cuando detecte ataques, TEKOSECURE podrá:

- ✅ **Bloquear IP** en firewall (automático en todas las sucursales)
- ✅ **Limitar BW** del atacante
- ✅ **Desconectar sesiones** SSH comprometidas
- ✅ **Crear reglas temporales** (auto-expira en 24h)
- ✅ **Registrar acciones** en audit log

---

## 🆘 Troubleshooting

### "No puedo conectar SSH"
```bash
# Verifica que SSH está habilitado
ping 192.168.13.100
ssh nasserti@192.168.13.100  # Intenta manualmente
```

### "Comando no funciona / Error"
- Copia línea por línea (no bloques enteros)
- Espera a que aparezca el prompt `>` antes de pegar el siguiente
- Revisa spelling exacto

### "¿Cómo vuelvo atrás si algo va mal?"
```bash
# Ver configuración actual
/ip firewall filter print
# Eliminar una regla (por número)
/ip firewall filter remove 5
```

### "¿Cómo hago backup antes?"
```bash
/system backup save name=backup-antes-tekosecure
# Archivo quedará guardado en el MK
```

---

## 📞 Soporte

Si algo falla:
1. Verifica credenciales en `1_CONECTAR.txt`
2. Revisa comandos en `2_COMANDOS.txt`
3. Compara con verificación en `3_VERIFICAR.txt`
4. Consulta con: admin@nasser.com

---

**TEKOSECURE v1.0** 🔐
**Estado: Listo para despliegue en 4 sucursales**
