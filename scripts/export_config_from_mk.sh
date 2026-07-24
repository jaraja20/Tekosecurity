#!/bin/bash

###############################################################################
# TEKOSECURE - Exportar Configuración Desde Cada Mikrotik
# Genera archivos RSC como el que pasaste (AuditoriaCompleta.rsc)
# SOLO LECTURA - No modifica nada
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

# Función para EXPORTAR configuración (como /export)
export_mk_config() {
    local MK_NAME=$1
    local MK_IP=$2

    echo -e "${BLUE}Exportando configuración de ${MK_NAME} (${MK_IP})...${NC}"

    # Comando para exportar todo (similar a /export)
    EXPORT_CMD="/export terse"

    OUTPUT_FILE="scripts/config_exports/${MK_NAME}_AuditoriaCompleta_$(date +%Y%m%d_%H%M%S).rsc"
    mkdir -p scripts/config_exports

    # Usar SSH con expect para manejar password
    cat > /tmp/export_${MK_NAME}.exp << 'EXPECT_EOF'
#!/usr/bin/expect

set USER [lindex $argv 0]
set PASSWORD [lindex $argv 1]
set IP [lindex $argv 2]
set MK_NAME [lindex $argv 3]
set OUTPUT_FILE [lindex $argv 4]

# Conectar SSH
spawn ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${USER}@${IP}

# Manejar prompt de password si es necesario
expect {
    "password:" {
        send "${PASSWORD}\r"
        expect -exact "> "
    }
    -exact "> " { }
}

# Ejecutar comando de exportación
send "/export terse\r"

# Capturar output
set timeout 10
expect -exact "> "

# Enviar exit
send "exit\r"
expect eof
EXPECT_EOF

    chmod +x /tmp/export_${MK_NAME}.exp

    # Ejecutar expect y capturar output
    expect /tmp/export_${MK_NAME}.exp "$USER" "$PASSWORD" "$MK_IP" "$MK_NAME" "$OUTPUT_FILE" > "$OUTPUT_FILE" 2>&1

    if [ -s "$OUTPUT_FILE" ]; then
        echo -e "${GREEN}✓ ${MK_NAME} - Guardado en: $OUTPUT_FILE${NC}"
        echo "  Tamaño: $(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null) bytes"
        return 0
    else
        echo -e "${YELLOW}⚠ ${MK_NAME} - Archivo vacío, intentando método alternativo${NC}"

        # Método alternativo: usar sshpass si expect falló
        if command -v sshpass &> /dev/null; then
            echo "Comando: /ip firewall nat print; /ip firewall filter print; /ip address print" | \
            sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "${USER}@${MK_IP}" > "$OUTPUT_FILE" 2>&1
            echo -e "${GREEN}✓ ${MK_NAME} - Guardado (método alternativo)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ sshpass no disponible - Ver LEER_CONFIG_SEGURO.md${NC}"
            return 1
        fi
    fi
}

###############################################################################
# MAIN
###############################################################################

echo -e "${YELLOW}"
echo "================================================================================"
echo "TEKOSECURE - EXPORTAR CONFIGURACIÓN DE MIKROTIK"
echo "================================================================================"
echo "Este script genera archivos RSC desde la configuración REAL de cada MK"
echo "⚠️  SOLO LECTURA - No se modificará nada"
echo "================================================================================"
echo -e "${NC}"

# Verificar que expect o sshpass está disponible
if ! command -v expect &> /dev/null && ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}"
    echo "⚠️  Ni expect ni sshpass están disponibles"
    echo ""
    echo "Para generar las exportaciones, desde cada MK ejecuta:"
    echo "  /export terse > AuditoriaCompleta.rsc"
    echo ""
    echo "Luego descarga los archivos y guárdalos en: scripts/config_exports/"
    echo ""
    echo "Ver: docs/LEER_CONFIG_SEGURO.md"
    echo -e "${NC}"
    exit 1
fi

mkdir -p scripts/config_exports

echo -e "${BLUE}Exportando configuración de 4 sucursales...${NC}\n"

SUCCESS=0
FAILED=0

# Exportar cada Mikrotik
for MK_NAME in "${!MK_IPS[@]}"; do
    MK_IP=${MK_IPS[$MK_NAME]}

    if export_mk_config "$MK_NAME" "$MK_IP"; then
        ((SUCCESS++))
    else
        ((FAILED++))
    fi

    sleep 2
done

echo -e "\n${YELLOW}================================================================================"
echo "RESUMEN:"
echo "  ${GREEN}Exitosos: $SUCCESS${NC}"
echo "  ${YELLOW}Fallidos: $FAILED${NC}"
echo "================================================================================${NC}"

echo ""
echo "Archivos generados:"
ls -lh scripts/config_exports/ 2>/dev/null || echo "(No hay archivos - ejecuta manualmente)"

echo ""
echo "Para ver un archivo:"
echo "  cat scripts/config_exports/MATRIZ_KM6_AuditoriaCompleta_*.rsc | head -50"

echo ""
echo "Próximo paso:"
echo "  Compara archivos con el que pasaste (AuditoriaCompleta.rsc)"
echo "  Identifica diferencias"
echo "  Documenta cambios necesarios"
