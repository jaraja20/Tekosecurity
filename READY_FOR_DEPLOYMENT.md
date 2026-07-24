# ✅ TEKOSECURE - LISTO PARA DESPLIEGUE

**Status:** Phase 1 (MVP) + Phase 2 (Acciones Reales) LISTOS

---

## 📦 QUÉ ESTÁ LISTO

### **Mikrotik RSC Scripts**
```
scripts/rsc/
├── MATRIZ_KM6_config.rsc
├── OASIS_config.rsc
├── KM12_config.rsc
└── HERNANDARIAS_config.rsc
```

✅ **IPs y credenciales actualizadas:**
- MATRIZ: 192.168.13.100 (nasserti / NasserTi73491654)
- OASIS: 192.128.255.226 (nasserti / NasserTi73491654)
- KM12: 192.168.15.1 (nasserti / NasserTi73491654)
- HERNANDARIAS: 192.168.11.69 (nasserti / NasserTi73491654)

---

## 🎯 PRÓXIMOS PASOS (Orden recomendado)

### **PASO 1: Desplegar en Mikrotik (15 min)**
```bash
# Opción A: Copiar y pegar comandos (más seguro, verifica línea por línea)
Ver: docs/COMANDOS_MIKROTIK_REALES.md

# Opción B: Subir RSC completo (más rápido)
scp scripts/rsc/MATRIZ_KM6_config.rsc nasserti@192.168.13.100:/
ssh nasserti@192.168.13.100
/import MATRIZ_KM6_config.rsc
# Repetir para OASIS, KM12, HERNANDARIAS
```

**Verificar:**
```bash
ssh nasserti@192.168.13.100
/ip firewall filter print
# Debe mostrar ~10 nuevas reglas
```

---

### **PASO 2: Actualizar backend FastAPI (10 min)**

Reemplazar en `backend/server.py`:

```python
from mikrotik_actions import MikrotikActionManager
import json

# Cargar config
with open('config/mikrotik_config.json') as f:
    mk_config = json.load(f)

# Crear manager
mk_manager = MikrotikActionManager(
    {
        "MATRIZ_KM6": mk_config['mikrotiks'][0],
        "OASIS": mk_config['mikrotiks'][1],
        "KM12": mk_config['mikrotiks'][2],
        "HERNANDARIAS": mk_config['mikrotiks'][3],
    }
)

@app.post("/api/actions/block-ip-real")
async def block_ip_real(payload: BlockIPRequest, authorization: str = Header()):
    token = authorization.replace("Bearer ", "")
    user = await _verify_supabase_token(token)
    
    # Conectar a todos los MK
    mk_manager.connect_all()
    
    # Bloquear en todas las sucursales
    result = mk_manager.block_ip_all_locations(
        source_ip=payload.source_ip,
        reason=f"TEKOSECURE: {payload.attack_type}",
        temporary=True
    )
    
    mk_manager.disconnect_all()
    
    # Registrar acción
    supabase.log_action({
        'actor': user['email'],
        'action': 'BLOCK_IP',
        'ip': payload.source_ip,
        'result': str(result)
    })
    
    return {"success": True, "blocked_in": len(result), "details": result}
```

---

### **PASO 3: Actualizar Frontend Emergent (5 min)**

En el botón "Bloquear IP":

```javascript
// Antes (simulado)
const blockIP = async (alertId, sourceIP) => {
  const response = await fetch('/api/actions/block-ip-simulated', {
    method: 'POST',
    body: JSON.stringify({ attack_id: alertId, source_ip: sourceIP })
  });
  // ...
}

// Ahora (REAL)
const blockIP = async (alertId, sourceIP) => {
  const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/actions/block-ip-real`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ attack_id: alertId, source_ip: sourceIP })
  });
  
  const result = await response.json();
  
  if (result.success) {
    toast.success(`✓ IP bloqueada en ${result.blocked_in} sucursales`);
    // Mostrar detalles
    console.log(result.details);
  }
};
```

---

### **PASO 4: Probar (10 min)**

**En Emergent App:**
1. Login: admin@gmail.com / Tekosecure2026!
2. Ir a Alertas
3. Hacer click en "Bloquear IP"
4. Confirmar
5. Ver mensaje: "✓ IP bloqueada en 4 sucursales"

**Verificar en Mikrotik:**
```bash
ssh nasserti@192.168.13.100
/ip firewall filter print
# Debe mostrar la IP bloqueada con tu IP de origen
```

---

## 📊 ESTADO POR COMPONENTE

| Componente | Status | Detalles |
|---|---|---|
| **Frontend** | ✅ MVP | Dashboard, Alertas, NVRs, Realtime |
| **Backend FastAPI** | ⚠️ Mock → Real | Listo migrar a ejecutor de Mikrotik |
| **Supabase** | ✅ Completo | Todas las tablas, datos, realtime |
| **Mikrotik Config** | ✅ RSCs Ready | 4 scripts listos para desplegar |
| **Python Monitoring** | ✅ Operativo | Mikrotik, Hikvision, Ataques, Alertas |
| **Auditoría** | ❌ TODO | Registrar acciones en tabla `audit_log` |
| **Notificaciones** | ❌ TODO | WhatsApp, Slack, Email |
| **Gráficos** | ❌ TODO | Charts Recharts |

---

## 🚀 COMANDOS FINALES

**Generar RSCs nuevamente si cambias config:**
```bash
python scripts/generate_mikrotik_rsc.py --all
```

**Probar conexión a un MK:**
```bash
ssh nasserti@192.168.13.100
```

**Ver todos los RSCs generados:**
```bash
ls -la scripts/rsc/
```

**Ver configuración actual de MK:**
```bash
cat config/mikrotik_config.json | jq '.mikrotiks[] | {name, ip, username}'
```

---

## 📞 SOPORTE

**Si algo falla:**

1. **No conecta SSH a MK:**
   - Verifica IP: `ping 192.168.13.100`
   - Verifica user/pass: `ssh nasserti@192.168.13.100`
   - Verifica SSH habilitado: `/ip service print`

2. **RSC no aplica:**
   - Verifica sintaxis: `/import scripts/rsc/MATRIZ_KM6_config.rsc`
   - Revisa errors: `system logging print`
   - Copia línea por línea manualmente

3. **Backend no bloquea:**
   - Verifica archivo: `backend/mikrotik_actions.py`
   - Test: `python -m pytest backend/tests/`
   - Verifica credenciales en `config/mikrotik_config.json`

---

## ✅ CHECKLIST FINAL

- [ ] Desplegar RSCs en 4 MK
- [ ] Verificar firewall rules en cada MK
- [ ] Actualizar `backend/server.py` con executor real
- [ ] Actualizar frontend con nuevo endpoint
- [ ] Probar bloqueo de IP desde dashboard
- [ ] Verificar que IP queda bloqueada en todos los MK
- [ ] Registrar acción en audit log
- [ ] Tests pasando (19/19 frontend, 8/8 backend)
- [ ] Documentar en wikis

---

**TEKOSECURE está listo para convertir de "Centro de Monitoreo" a "Centro de Acción Completo"** 🔐🚀

¿Cuál es tu siguiente paso?
