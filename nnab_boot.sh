#!/bin/bash
tmux kill-session -t nnab 2>/dev/null
tmux new-session -d -s nnab
tmux set-option -t nnab status-position top
tmux split-window -v -l 20
tmux send-keys -t nnab:0.1 "while true; do python3 nnab_core.py 2> nnab_crash.log; if [ \$? -ne 0 ]; then python3 nnab_healer.py; sleep 2; else break; fi; done; exit" C-m
tmux send-keys -t nnab:0.0 "cd ~/OmegaCore/SHADOW_REALM; clear; echo SYSTEM READY" C-m
tmux attach -t nnab
