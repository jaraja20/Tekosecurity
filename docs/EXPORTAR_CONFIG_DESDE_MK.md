# TEKOSECURE - Exportar Configuración DESDE Mikrotik

**Mejor que generar comandos genéricos: Extraer la configuración REAL de cada MK**

Similar al archivo que pasaste: `AuditoriaCompleta.rsc`

---

## 🔍 MATRIZ KM6 (192.168.13.100)

### Paso 1: Conectar

```bash
ssh nasserti@192.168.13.100
# Password: NasserTi73491654
```

### Paso 2: Exportar (SOLO LECTURA - No modifica nada)

```bash
/export terse
```

Este comando genera TODA la configuración actual en formato RSC.

### Paso 3: Guardar

**Opción A: Copiar output a archivo (en tu PC)**

```bash
# Desde tu PC, ejecuta:
ssh nasserti@192.168.13.100 "/export terse" > MATRIZ_KM6_config_actual.rsc

# Espera a que termine (puede tomar 5-10 segundos)
```

**Opción B: Copiar desde terminal**

1. En terminal Mikrotik, ejecuta: `/export terse`
2. Selecciona TODO el output (Ctrl+A)
3. Copia (Ctrl+C)
4. Pega en archivo: `MATRIZ_KM6_config_actual.rsc`

---

## 🔍 OASIS (192.128.255.226)

### Paso 1: Conectar

```bash
ssh nasserti@192.128.255.226
```

### Paso 2: Exportar

```bash
/export terse
```

### Paso 3: Guardar

```bash
ssh nasserti@192.128.255.226 "/export terse" > OASIS_config_actual.rsc
```

---

## 🔍 KM12 (192.168.15.1)

### Paso 1: Conectar

```bash
ssh nasserti@192.168.15.1
```

### Paso 2: Exportar

```bash
/export terse
```

### Paso 3: Guardar

```bash
ssh nasserti@192.168.15.1 "/export terse" > KM12_config_actual.rsc
```

---

## 🔍 HERNANDARIAS (192.168.11.69)

### Paso 1: Conectar

```bash
ssh nasserti@192.168.11.69
```

### Paso 2: Exportar

```bash
/export terse
```

### Paso 3: Guardar

```bash
ssh nasserti@192.168.11.69 "/export terse" > HERNANDARIAS_config_actual.rsc
```

---

## 📁 Organizar Archivos

Crea carpeta y guarda:

```
scripts/config_exports/
├── MATRIZ_KM6_config_actual.rsc
├── OASIS_config_actual.rsc
├── KM12_config_actual.rsc
└── HERNANDARIAS_config_actual.rsc
```

---

## 🔎 Ver Diferencias

Compara con el archivo que pasaste:

```bash
diff AuditoriaCompleta.rsc MATRIZ_KM6_config_actual.rsc

# Ver solo líneas diferentes:
diff AuditoriaCompleta.rsc MATRIZ_KM6_config_actual.rsc | grep "^<\|^>"
```

---

## 📊 Analizar Configuración

### Ver solo interfaces
```bash
grep "^/interface" MATRIZ_KM6_config_actual.rsc
```

### Ver solo direcciones IP
```bash
grep "^/ip address" MATRIZ_KM6_config_actual.rsc
```

### Ver solo firewall
```bash
grep "^/ip firewall" MATRIZ_KM6_config_actual.rsc
```

### Ver solo DHCP
```bash
grep "^/ip dhcp" MATRIZ_KM6_config_actual.rsc
```

### Ver solo queues/ancho de banda
```bash
grep "^/queue" MATRIZ_KM6_config_actual.rsc
```

### Ver solo routing
```bash
grep "^/ip route" MATRIZ_KM6_config_actual.rsc
```

---

## ✅ Beneficios de Este Método

✓ **Configuración REAL** - No genérica
✓ **100% seguro** - Solo lectura, no modifica
✓ **Documentación actual** - Baseline para comparaciones
✓ **Auditoría completa** - Ve todo: interfaces, rutas, firewall, etc.
✓ **Detección de cambios** - Compara antes vs después
✓ **Rollback seguro** - Tienes copia de configuración original

---

## 🛠️ Script Automático (Opcional)

Si tienes `sshpass` instalado:

```bash
#!/bin/bash

# Crear carpeta
mkdir -p scripts/config_exports

# Exportar todos
ssh nasserti@192.168.13.100 "/export terse" > scripts/config_exports/MATRIZ_KM6_config_actual.rsc
ssh nasserti@192.128.255.226 "/export terse" > scripts/config_exports/OASIS_config_actual.rsc
ssh nasserti@192.168.15.1 "/export terse" > scripts/config_exports/KM12_config_actual.rsc
ssh nasserti@192.168.11.69 "/export terse" > scripts/config_exports/HERNANDARIAS_config_actual.rsc

# Ver resultado
ls -lh scripts/config_exports/
```

---

## 📋 Checklist

- [ ] Exportar MATRIZ KM6
- [ ] Exportar OASIS
- [ ] Exportar KM12
- [ ] Exportar HERNANDARIAS
- [ ] Guardar en `scripts/config_exports/`
- [ ] Comparar diferencias con Matriz
- [ ] Analizar cambios necesarios
- [ ] Documentar estado actual

---

**Esto es mucho más seguro y preciso que cambios genéricos.**

TEKOSECURE will read your actual config, not guess it. 🔐
