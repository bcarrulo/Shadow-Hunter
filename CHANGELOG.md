# Shadow Hunter - Changelog

## v1.1 - The "Recon & Profile" Update
- **Auto-Discovery**: Added `[0]` Auto-Recon option.
    - Automatically detects local IP interface.
    - Assumes /24 subnet for quick scanning.
- **New Scan Profiles**:
    - `[1] FAST`: Top 1000 ports (Standard).
    - `[2] DEEP`: All 65535 ports + OS Detect + Scripts.
    - `[3] VULN`: Targeted vulnerability scan (`--script vuln`).
    - `[4] STEALTH`: TCP SYN Scan (`-sS`) - **Requires Root**.
    - `[5] AGGRESSIVE`: `-T5 -A -v` (Noisy).
    - `[6] LEVE`: Ping Sweep only (`-sn`).
- **Engine Improvements**:
    - Imported `socket` for network auto-detection.
    - Fixed cross-platform clear screen.
