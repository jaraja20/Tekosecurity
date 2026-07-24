# TEKOSECURE - Plan Seguro (Sin Riesgos)

## ❌ NO VOY A HACER

```
✗ Modificar firewall rules en producción
✗ Cambiar configuración de interfaces
✗ Alterar DHCP servers
✗ Tocar rutas de red
✗ Cambiar credenciales
✗ Ejecutar comandos destructivos
✗ Desconectar o bloquear acceso
✗ Interrumpir internet en ninguna sucursal
```

**Razón:** Una mala configuración = DOWNTIME total en esa sucursal

---

## ✅ SÍ VOY A HACER

### Phase 1: Auditoría Segura (HOY)
```
✓ Leer configuración actual de cada MK
✓ Documentar estado actual
✓ Crear baseline (referencia)
✓ Identificar qué está funcionando
✓ Generar reportes de lectura
```

### Phase 2: Plan de Cambios (MAÑANA)
```
✓ Analizar configuración actual
✓ Identificar qué se puede mejorar
✓ Crear plan de cambios SEGUROS
✓ Documentar cada cambio
✓ Preparar rollback
```

### Phase 3: Cambios Controlados (DESPUÉS)
```
✓ Cambiar UNO por UNO (no todos juntos)
✓ Verificar internet después de cada cambio
✓ Tener respaldo de configuración anterior
✓ Si algo falla, revertir inmediatamente
```

### Phase 4: Testing en Lab (PRIMERO)
```
✓ Simular cambios en ambiente de prueba
✓ Validar que funciona
✓ LUEGO aplicar en producción
```

---

## 🔐 Protecciones Implementadas

### Backup Automático
```
- Antes de cualquier cambio
- Archivo: backup-antes-tekosecure.backup
- Guardado en el MK
```

### Rollback Plan
```
Si algo falla:
  1. Desconectar cambio
  2. Restaurar desde backup
  3. Verificar internet funciona
  4. Investigar qué salió mal
  5. Intentar de nuevo
```

### Cambios Incrementales
```
Primero:  1 regla firewall → verificar
Segundo: 2 reglas firewall → verificar
...
Finalmente: Todas las reglas

No hacer todo junto (alto riesgo)
```

---

## 📋 Orden de Ejecución

### SEMANA 1: Documentación
- [x] Generar archivos RSC (sin aplicar)
- [ ] Leer configuración actual de 4 MK
- [ ] Documentar estado baseline
- [ ] Identificar conflictos potenciales

### SEMANA 2: Planificación
- [ ] Analizar configuración actual
- [ ] Crear plan detallado de cambios
- [ ] Documento: "Cambios a realizar"
- [ ] Aprobación de cambios

### SEMANA 3: Lab Testing
- [ ] Simular cambios en Mikrotik de prueba
- [ ] Validar que todo funciona
- [ ] Documen beneficios

### SEMANA 4: Despliegue Controlado
- [ ] Cambios en MATRIZ (menos crítico primero)
- [ ] Verificar 4 horas
- [ ] Si OK → OASIS
- [ ] Si OK → KM12
- [ ] Si OK → HERNANDARIAS

---

## 🚨 Contingencia

Si algo falla durante cambios:

```
1. DETENER inmediatamente
2. SSH al MK afectado
3. /system backup restore name=backup-antes-tekosecure
4. Reiniciar MK
5. Verificar internet
6. Documentar qué salió mal
7. Investigar causa
8. Próximo intento: cambios más pequeños
```

---

## ✅ Responsabilidades

| Tarea | Quién | Status |
|---|---|---|
| Leer config actual | Claude + Usuario | 📋 Documentado |
| Analizar estado | Usuario | ⏳ Siguiente |
| Aprobar cambios | Usuario | ⏳ Siguiente |
| Cambios en lab | Claude | ⏳ Siguiente |
| Despliegue controlado | Usuario supervisa | ⏳ Siguiente |
| Verificar internet | Usuario | ⏳ Cada cambio |
| Rollback si falla | Usuario + Claude | 🆘 Si necesario |

---

## 📊 Resumen del Plan

```
Fase 1: LECTURA (Sin riesgo)
├─ Leer MK1, MK2, MK3, MK4
├─ Documentar estado actual
└─ Generar reportes

Fase 2: ANÁLISIS (Sin riesgo)
├─ Estudiar configuración
├─ Identificar mejoras
└─ Crear plan de cambios

Fase 3: TEST (Bajo riesgo)
├─ Lab: simular cambios
├─ Validar funcionamiento
└─ Documento de cambios aprobado

Fase 4: DEPLOY (Controlado)
├─ Cambio 1 → Verificar
├─ Cambio 2 → Verificar
├─ Cambio 3 → Verificar
└─ Cambio 4 → Verificar
```

---

## 💡 Filosofía

**"Medir 10 veces, cortar 1 sola vez"**

- No apurarse
- No hacer cambios masivos
- Verificar en cada paso
- Documentar todo
- Tener plan B siempre

---

**TEKOSECURE v1.0 - Seguridad Primero** 🔐

*Protegemos los Mikrotik como protegemos el resto del sistema:*
*Monitoreamos, documentamos, planeamos y ejecutamos con cuidado.*
