#!/bin/bash

###############################################################################
# TEKOSECURE - Deploy Automático en Todos los Mikrotik
# Este script configura las 4 sucursales automáticamente
###############################################################################

set -e

USER="nasserti"
PASSWORD="NasserTi73491654"

# Configuración de Mikrotik
declare -A MK_IPS=(
    ["MATRIZ_KM6"]="192.168.13.100"
    ["OASIS"]="192.128.255.226"
    ["KM12"]="192.168.15.1"
    ["HERNANDARIAS"]="192.168.11.69"
)

declare -A MK_NAMES=(
    ["MATRIZ_KM6"]="TEKOSECURE-MATRIZ_KM6"
    ["OASIS"]="TEKOSECURE-OASIS"
    ["KM12"]="TEKOSECURE-KM12"
    ["HERNANDARIAS"]="TEKOSECURE-HERNANDARIAS"
)

declare -A MK_SUBNETS=(
    ["MATRIZ_KM6"]="192.168.13.1/24"
    ["OASIS"]="192.128.255.1/24"
    ["KM12"]="192.168.15.1/24"
    ["HERNANDARIAS"]="192.168.11.1/24"
)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para ejecutar comandos en Mikrotik
execute_on_mk() {
    local MK_NAME=$1
    local MK_IP=$2
    local COMMANDS=$3

    echo -e "${BLUE}Conectando a ${MK_NAME} (${MK_IP})...${NC}"

    # Usar sshpass para automatizar la autenticación
    echo "$COMMANDS" | sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${USER}@${MK_IP}" 2>&1

    local STATUS=$?
    if [ $STATUS -eq 0 ]; then
        echo -e "${GREEN}✓ ${MK_NAME} configurado exitosamente${NC}"
        return 0
    else
        echo -e "${RED}✗ Error en ${MK_NAME}${NC}"
        return 1
    fi
}

# Función para generar comandos de configuración
generate_config_commands() {
    local MK_NAME=$1
    local SUBNET=$2

    cat << EOF
/system identity set name="${MK_NAMES[$MK_NAME]}"
/ip dns set servers=8.8.8.8,8.8.4.4 allow-remote-requests=yes
/system ntp client set enabled=yes server-dns-names=pool.ntp.org
/ip address add address=$SUBNET interface=ether2 comment="LAN $MK_NAME"
/ip dhcp-client add interface=ether1 disabled=no
/ip firewall filter add action=accept chain=input protocol=icmp comment="Allow ping"
/ip firewall filter add action=accept chain=input connection-state=established,related comment="Allow established"
/ip firewall filter add action=accept chain=input in-interface=ether2 comment="Allow from LAN"
/ip firewall filter add action=drop chain=input comment="Drop input default"
/ip firewall filter add action=accept chain=forward connection-state=established,related
/ip firewall filter add action=accept chain=forward in-interface=ether1 out-interface=ether2 comment="WAN to LAN"
/ip firewall filter add action=accept chain=forward in-interface=ether2 out-interface=ether1 comment="LAN to WAN"
/ip firewall filter add action=accept chain=forward protocol=tcp dst-port=22,80,443 comment="Allow SSH/HTTP/HTTPS"
/ip firewall filter add action=drop chain=forward connection-state=invalid comment="Drop invalid"
/ip firewall nat add action=masquerade chain=srcnat out-interface=ether1 comment="Masquerade to WAN"
/snmp set enabled=yes trap-enabled=yes trap-community=public
EOF
}

# Función para generar comandos de verificación
generate_verify_commands() {
    cat << EOF
/system identity print
/ip address print
/ip firewall filter print
/ip firewall nat print
/ip dns print
/system ntp client print
/snmp print
EOF
}

###############################################################################
# MAIN
###############################################################################

echo -e "${YELLOW}"
echo "================================================================================"
echo "TEKOSECURE - DEPLOY AUTOMÁTICO EN TODOS LOS MIKROTIK"
echo "================================================================================"
echo -e "${NC}"

# Verificar que sshpass está instalado
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}sshpass no está instalado. Instalando...${NC}"
    apt-get update && apt-get install -y sshpass > /dev/null 2>&1
fi

echo -e "${BLUE}Iniciando despliegue en 4 sucursales...${NC}\n"

FAILED=0
SUCCESS=0

# Iterar sobre cada Mikrotik
for MK_NAME in "${!MK_IPS[@]}"; do
    MK_IP=${MK_IPS[$MK_NAME]}
    SUBNET=${MK_SUBNETS[$MK_NAME]}

    echo -e "${YELLOW}[$(date +'%H:%M:%S')] Procesando ${MK_NAME}${NC}"

    # Generar comandos
    CONFIG_CMDS=$(generate_config_commands "$MK_NAME" "$SUBNET")
    VERIFY_CMDS=$(generate_verify_commands)

    # Ejecutar configuración
    echo "  → Aplicando configuración..."
    execute_on_mk "$MK_NAME" "$MK_IP" "$CONFIG_CMDS"
    if [ $? -eq 0 ]; then
        ((SUCCESS++))
    else
        ((FAILED++))
        continue
    fi

    # Esperar 3 segundos
    sleep 3

    # Ejecutar verificación
    echo "  → Verificando configuración..."
    VERIFY_OUTPUT=$(echo "$VERIFY_CMDS" | sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${USER}@${MK_IP}" 2>&1)

    # Guardar resultado en archivo
    OUTPUT_FILE="scripts/deploy_results/${MK_NAME}_resultado.txt"
    mkdir -p scripts/deploy_results

    cat > "$OUTPUT_FILE" << EOF
===============================================================================
TEKOSECURE - RESULTADO DEPLOY ${MK_NAME}
===============================================================================
Fecha: $(date)
IP: $MK_IP
Usuario: $USER

CONFIGURACIÓN APLICADA:
$CONFIG_CMDS

RESULTADO DE VERIFICACIÓN:
$VERIFY_OUTPUT

STATUS: OK
===============================================================================
EOF

    echo -e "${GREEN}  ✓ Resultado guardado en: $OUTPUT_FILE${NC}"
    echo ""
done

# Resumen final
echo -e "${YELLOW}================================================================================${NC}"
echo -e "RESUMEN:"
echo -e "  ${GREEN}Exitosos: $SUCCESS${NC}"
echo -e "  ${RED}Fallidos: $FAILED${NC}"
echo -e "${YELLOW}================================================================================${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ TODOS LOS MIKROTIK CONFIGURADOS EXITOSAMENTE${NC}"
    echo ""
    echo "Archivos de resultado:"
    ls -lh scripts/deploy_results/
    exit 0
else
    echo -e "${RED}✗ ALGUNOS MIKROTIK FALLARON${NC}"
    exit 1
fi
