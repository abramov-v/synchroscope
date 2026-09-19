# Synchroscope Simulator

Educational Tkinter simulator for synchronizing an incoming generator with a 50 Hz grid.

## Features

- 50 Hz BUS / GRID reference
- Incoming generator with adjustable frequency
- 0.01 Hz frequency steps and direct frequency slider
- Manual excitation control with smooth generator-voltage response
- Optional automatic AVR
- Relative phase visualization
- Synchroscope with sync window and FAST / SLOW / HOLD indication
- BUS and generator voltage waveforms
- Sync-check before breaker closing
- Failed sync-check diagnostics with the blocking reason
- Electrical single-line breaker diagram with animated opening/closing blade
- Live measurements
- Keyboard shortcuts

## Requirements

- Python 3.x
- Tkinter
- No third-party Python packages

## Run

    python app.py

## Controls

- SLOW / FAST — change generator frequency by 0.01 Hz
- Hold SLOW / FAST — continuously adjust frequency
- Up / Down — same one-step frequency adjustment from the keyboard
- Frequency slider — directly set generator frequency
- EXCITATION slider / - / + — manually adjust generator excitation
- AUTO AVR — automatically adjust excitation toward BUS voltage
- SPACE / CLOSE BREAKER — attempt to close the breaker
- RESET — restore the initial generator state

## Synchronization check

The breaker can close only when all conditions are satisfied:

- Phase error <= 10 degrees
- Frequency difference < 0.067 Hz
- Generator voltage difference is from 0% to +5% relative to BUS voltage
- Generator voltage may not be below BUS voltage for synchronization

The voltage synchronization criterion is calculated as:

    ΔV% = (Generator voltage - BUS voltage) / BUS voltage × 100

With the default 6.6 kV BUS:

- 0% = 6.60 kV
- +5% = 6.93 kV

## Breaker behavior

The breaker is physically blocked when synchronization conditions are not met. A failed close attempt shows which condition is outside its allowed range.

When synchronization is ready, the interface indicates CLOSE NOW and the breaker can be closed with the button or SPACE.

## Educational scope

This is an educational visualization and control simulation. It is not a substitute for real protection, synchronization, AVR, or generator control equipment.
