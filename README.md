# Synchroscope Simulator

Educational Tkinter simulator for synchronizing an incoming generator with a 50 Hz BUS.

## Run

```bash
python app.py
```

Requirements: Python 3.x + Tkinter

## Controls

- **SLOW / FAST** — generator frequency ±0.01 Hz
- **Hold SLOW / FAST** — continuous frequency adjustment
- **Frequency slider** — set frequency directly
- **EXCITATION / - / +** — adjust generator voltage
- **AUTO AVR** — automatic voltage adjustment
- **CLOSE BREAKER / SPACE** — close breaker when sync conditions are met
- **RESET** — restore initial state


<img width="2534" height="1449" alt="image" src="https://github.com/user-attachments/assets/aaef13ed-5267-440b-a56d-1ccf7f44a68b" />



## Sync conditions

Breaker closes only when:

- Phase error ≤ **10°**
- Frequency difference < **0.067 Hz**
- Generator voltage is **0% to +5% above BUS**

Voltage difference:

```
ΔV% = (Generator voltage - BUS voltage) / BUS voltage × 100
```

## Constants

Main simulation constants are in **config.py**.

To change frequency:

```python
BUS_FREQUENCY = 50.00
INITIAL_GEN_FREQUENCY = 49.80
FREQUENCY_STEP = 0.01
FREQUENCY_MIN = 49.0
FREQUENCY_MAX = 51.0
```

To change voltage:

```python
BUS_VOLTAGE = 6.6
INITIAL_GEN_VOLTAGE = 6.51
```

Sync voltage limits are also in **config.py**:

```python
SYNC_VOLTAGE_MIN_PERCENT = 0.0
SYNC_VOLTAGE_MAX_PERCENT = 5.0
```

Other sync limits:

```python
SYNC_PHASE_LIMIT_DEG = 10.0
SYNC_FREQUENCY_LIMIT_HZ = 0.067
```
