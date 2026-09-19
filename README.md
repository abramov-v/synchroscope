# Synchroscope Simulator

Educational Tkinter simulator for synchronizing an incoming generator with a 50 Hz grid.

## Features

- 50 Hz BUS / GRID reference
- Incoming generator with adjustable frequency
- 0.01 Hz frequency steps and direct frequency slider
- Generator voltage control
- Optional automatic AVR
- Relative phase visualization
- Synchroscope with sync window
- Voltage waveform
- Sync-check before breaker closing
- Animated breaker
- Live measurements
- Keyboard shortcuts

## Requirements

- Python 3.x
- Tkinter
- No third-party Python packages

## Run

    python app.py

## Controls

- SPEED UP / SPEED DOWN — change generator frequency by 0.01 Hz
- Up / Down — same adjustment from the keyboard
- Frequency slider — directly set generator frequency
- Voltage slider — set generator voltage
- AUTO AVR — move generator voltage toward bus voltage
- SPACE — attempt to close the breaker
- RESET — restore the initial generator state

## Synchronization check

The breaker can close only when all conditions are satisfied:

- Phase error <= 10 degrees
- Frequency difference < 0.067 Hz
- Voltage difference <= 1.0 kV

This is an educational visualization, not a substitute for real protection,
synchronization, or control equipment.
