# clock

Terminal clock, stopwatch, and timer with curses TUI.

Version: 0.1.4

## Features

- **Clock**: Display current time with big digit font
- **Timezones**: Show any timezone (UTC-3, GMT+5:30, EST, JST, etc.)
- **Multiple clocks**: Compare timezones side by side
- **Stopwatch**: Chronometer with lap tracking
- **Timer**: Countdown timer with progress bar
- **Pipe timing**: Time any command via pipe

## Usage

```bash
# Show local time
clock

# Show a specific timezone
clock UTC-3
clock GMT+5:30

# Compare multiple timezones
clock UTC-3 UTC JST

# Stopwatch (space=start/lap, s=stop, r=reset, q=quit)
clock -c

# Time a command via pipe
ls -R / | clock -c
long_running_script.sh | clock -c

# Countdown timer (minutes)
clock -t 5          # 5 minute timer
clock -t 0.5        # 30 second timer
clock -t 25         # Pomodoro timer
```

## Keybindings

| Mode | Key | Action |
|------|-----|--------|
| Clock | q/Esc | Quit |
| Stopwatch | space | Start / Lap |
| Stopwatch | s | Stop |
| Stopwatch | r | Reset |
| Stopwatch | q/Esc | Quit |
| Timer | space | Pause / Resume |
| Timer | r | Restart |
| Timer | q/Esc | Quit |

## Supported Timezones

- UTC, GMT (with offsets: UTC-3, GMT+5:30)
- Named: EST, EDT, CST, CDT, MST, MDT, PST, PDT
- European: CET, CEST, EET, EEST
- Asia/Pacific: IST, JST, KST, AEST, AEDT, NZST, NZDT
- South America: BRT

## Installation

### Build from source
```bash
git clone https://github.com/pynosaur/clock.git
cd clock
bazel build //:clock_bin
cp bazel-bin/clock ~/.local/bin/
```

### With pget
```bash
pget install clock
```
