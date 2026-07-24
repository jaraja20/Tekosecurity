#!/bin/bash

###############################################################################
# TEKOSECURE - Auditoría de Configuración (SOLO LECTURA - NO MODIFICA NADA)
# Lee la configuración actual de cada Mikrotik para documentar el estado
###############################################################################

set -e

USER="nasserti"
PASSWORD="NasserTi73491654"

declare -A MK_IPS=(
    ["MATRIZ_KM6"]="192.168.13.100"
    ["OASIS"]="192.128.255.226"
    ["KM12"]="192.168.15.1"
    ["HERNANDARIAS"]="192.168.11.69"
)

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para LEER (sin modificar)
read_mk_config() {
    local MK_NAME=$1
    local MK_IP=$2

    echo -e "${BLUE}Leyendo configuración de ${MK_NAME} (${MK_IP})...${NC}"

    COMMANDS="
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
"

    # Ejecutar SOLO lectura
    OUTPUT=$(echo "$COMMANDS" | sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${USER}@${MK_IP}" 2>&1)

    # Guardar resultado
    OUTPUT_FILE="scripts/audit_results/${MK_NAME}_config.txt"
    mkdir -p scripts/audit_results

    cat > "$OUTPUT_FILE" << EOF
===============================================================================
TEKOSECURE - AUDITORÍA DE CONFIGURACIÓN
===============================================================================
Sucursal: ${MK_NAME}
IP: ${MK_IP}
Fecha: $(date)
Usuario: ${USER}

⚠️  SOLO LECTURA - NO SE MODIFICÓ NADA

===============================================================================
IDENTIDAD DEL SISTEMA
===============================================================================
$(echo "$OUTPUT" | grep -A 50 "Flags:" | head -5)

===============================================================================
DIRECCIONES IP
===============================================================================
$(echo "$OUTPUT" | grep -A 100 "Flags: . . ." | grep -A 20 "address" | head -15)

===============================================================================
RUTAS
===============================================================================
$(echo "$OUTPUT" | grep -A 50 "dst-address" | head -10)

===============================================================================
REGLAS FIREWALL (FILTER)
===============================================================================
$(echo "$OUTPUT" | grep -A 100 "chain" | head -30)

===============================================================================
REGLAS NAT
===============================================================================
$(echo "$OUTPUT" | grep -A 50 "nat" | head -15)

===============================================================================
CONFIGURACIÓN DNS
===============================================================================
$(echo "$OUTPUT" | grep -A 10 "servers" | head -5)

===============================================================================
ESTADO COMPLETO
===============================================================================
$OUTPUT

===============================================================================
REPORTE GENERADO: $(date)
===============================================================================
EOF

    echo -e "${GREEN}✓ ${MK_NAME} - Guardado en: $OUTPUT_FILE${NC}\n"
}

###############################################################################
# MAIN
###############################################################################

echo -e "${YELLOW}"
echo "================================================================================"
echo "TEKOSECURE - AUDITORÍA DE CONFIGURACIÓN ACTUAL"
echo "================================================================================"
echo "⚠️  MODO SOLO LECTURA - NO SE MODIFICARÁ NADA"
echo "================================================================================"
echo -e "${NC}"

# Verificar sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "Instalando sshpass..."
    apt-get update && apt-get install -y sshpass > /dev/null 2>&1
fi

echo -e "${BLUE}Leyendo configuración de 4 sucursales...${NC}\n"

# Leer cada Mikrotik
for MK_NAME in "${!MK_IPS[@]}"; do
    MK_IP=${MK_IPS[$MK_NAME]}
    read_mk_config "$MK_NAME" "$MK_IP"
    sleep 2
done

echo -e "${YELLOW}================================================================================"
echo "✓ AUDITORÍA COMPLETADA"
echo "================================================================================"
echo "Resultados guardados en: scripts/audit_results/"
echo -e "${NC}"

# Listar archivos generados
echo "Archivos generados:"
ls -lh scripts/audit_results/

echo ""
echo "Para revisar cada resultado:"
echo "  cat scripts/audit_results/MATRIZ_KM6_config.txt"
echo "  cat scripts/audit_results/OASIS_config.txt"
echo "  cat scripts/audit_results/KM12_config.txt"
echo "  cat scripts/audit_results/HERNANDARIAS_config.txt"
