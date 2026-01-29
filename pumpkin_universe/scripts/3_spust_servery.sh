#!/bin/bash
echo "[OMEGA] Fáze 3: Zahajuji nasazení serverů..."

SITES_DIR="../generated_sites"
LOGS_DIR="../logs"
PIDS_FILE="../pids.txt"
STARTING_PORT=8001

> "$PIDS_FILE"
cd "$SITES_DIR" || { echo "[ERROR] Adresář $SITES_DIR neexistuje."; exit 1; }

CURRENT_PORT=$STARTING_PORT
for site in */; do
    site_name=${site%/}
    echo "[OMEGA] Spouštím server pro '$site_name' na portu $CURRENT_PORT..."
    cd "$site_name"
    python3 -m http.server $CURRENT_PORT > "${LOGS_DIR}/${site_name}.log" 2>&1 &
    echo $! >> "$PIDS_FILE"
    cd ..
    ((CURRENT_PORT++))
done

echo "[OMEGA] Všechny servery byly spuštěny na pozadí."
echo "[OMEGA] Přístupové adresy: http://localhost:8001 až http://localhost:8050"
echo "[OMEGA] Fáze 3 dokončena."
