#!/bin/bash
echo "[OMEGA] Fáze 4: Zahajuji terminaci všech serverů..."

PIDS_FILE="../pids.txt"
if [ ! -f "$PIDS_FILE" ] || [ ! -s "$PIDS_FILE" ]; then
    echo "[OMEGA] Soubor s PIDy ($PIDS_FILE) neexistuje nebo je prázdný."
    exit 0
fi

PIDS=$(cat "$PIDS_FILE")
kill $PIDS
sleep 2
if kill -0 $PIDS 2>/dev/null; then
    echo "[OMEGA] Některé procesy se nepodařilo standardně ukončit. Používám SIGKILL."
    kill -9 $PIDS
fi
> "$PIDS_FILE"
echo "[OMEGA] Všechny servery projektu TÝKVOVÉ UNIVERZUM byly ukončeny."
echo "[OMEGA] Fáze 4 dokončena."
