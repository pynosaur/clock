#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-05-03

"""Curses-based UI for clock, chronometer, and timer modes."""

import curses
import time
from datetime import datetime, timezone
from .timezones import (
    parse_tz, now_in_tz, format_time,
    format_chrono, format_timer,
)


# ── Big digit font (3 lines tall, 5 chars wide) ──────────────────────────────

_DIGITS = {
    "0": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": [" ███ ", "█   █", "  ██ ", " █   ", "█████"],
    "3": [" ███ ", "█   █", "  ██ ", "█   █", " ███ "],
    "4": ["█  █ ", "█  █ ", "█████", "   █ ", "   █ "],
    "5": ["█████", "█    ", "████ ", "    █", "████ "],
    "6": [" ███ ", "█    ", "████ ", "█   █", " ███ "],
    "7": ["█████", "   █ ", "  █  ", " █   ", " █   "],
    "8": [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    "9": [" ███ ", "█   █", " ████", "    █", " ███ "],
    ":": ["     ", "  █  ", "     ", "  █  ", "     "],
    ".": ["     ", "     ", "     ", "     ", "  █  "],
    " ": ["     ", "     ", "     ", "     ", "     "],
    "-": ["     ", "     ", " ███ ", "     ", "     "],
}

_DIGIT_HEIGHT = 5
_DIGIT_WIDTH = 5
_DIGIT_GAP = 1

COLOR_LABEL = 1
COLOR_TIME = 2
COLOR_DIM = 3
COLOR_ALERT = 4
COLOR_LAP = 5
COLOR_HEADER = 6


def _init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_LABEL, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_TIME, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_DIM, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_ALERT, curses.COLOR_RED, -1)
    curses.init_pair(COLOR_LAP, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_HEADER, curses.COLOR_BLACK, curses.COLOR_WHITE)


def _safe_addstr(stdscr, row, col, text, attr=0):
    try:
        stdscr.addnstr(row, col, text, len(text), attr)
    except curses.error:
        pass


def _draw_big_text(stdscr, row, col, text, attr=0):
    """Draw text using the big digit font."""
    for line_idx in range(_DIGIT_HEIGHT):
        x = col
        for ch in text:
            glyph = _DIGITS.get(ch, _DIGITS[" "])
            _safe_addstr(stdscr, row + line_idx, x, glyph[line_idx], attr)
            x += _DIGIT_WIDTH + _DIGIT_GAP


def _big_text_width(text):
    return len(text) * (_DIGIT_WIDTH + _DIGIT_GAP) - _DIGIT_GAP


# ── Clock mode ────────────────────────────────────────────────────────────────

def run_clock(stdscr, zones):
    """Display one or more clocks. zones is a list of (label, tzinfo)."""
    curses.curs_set(0)
    _init_colors()
    stdscr.timeout(100)

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if len(zones) == 1:
            label, tz = zones[0]
            now = now_in_tz(tz)
            time_str = format_time(now)
            date_str = now.strftime("%Y-%m-%d %A")

            # Big centered clock
            tw = _big_text_width(time_str)
            cx = max(0, (max_x - tw) // 2)
            cy = max(0, (max_y - _DIGIT_HEIGHT) // 2 - 2)

            _safe_addstr(
                stdscr, cy, max(0, (max_x - len(label)) // 2),
                label,
                curses.color_pair(COLOR_LABEL) | curses.A_BOLD,
            )
            _draw_big_text(
                stdscr, cy + 2, cx, time_str,
                curses.color_pair(COLOR_TIME) | curses.A_BOLD,
            )
            _safe_addstr(
                stdscr, cy + 2 + _DIGIT_HEIGHT + 1,
                max(0, (max_x - len(date_str)) // 2),
                date_str,
                curses.color_pair(COLOR_DIM),
            )
        else:
            # Multiple clocks: list them
            start_y = max(0, (max_y - len(zones) * 3) // 2)
            for i, (label, tz) in enumerate(zones):
                now = now_in_tz(tz)
                time_str = format_time(now)
                row = start_y + i * 3

                line = f"{label:>12}  {time_str}"
                cx = max(0, (max_x - len(line)) // 2)

                _safe_addstr(
                    stdscr, row, cx, f"{label:>12}",
                    curses.color_pair(COLOR_LABEL) | curses.A_BOLD,
                )
                _safe_addstr(
                    stdscr, row, cx + 14, time_str,
                    curses.color_pair(COLOR_TIME) | curses.A_BOLD,
                )

                date_str = now.strftime("%Y-%m-%d")
                _safe_addstr(
                    stdscr, row + 1, cx + 14, date_str,
                    curses.color_pair(COLOR_DIM),
                )

        _safe_addstr(
            stdscr, max_y - 1, 0, " q:quit",
            curses.A_DIM,
        )
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord("q") or key == 27:
            break


# ── Chronometer mode ──────────────────────────────────────────────────────────

def run_chrono(stdscr):
    """Run a stopwatch with lap support (spacebar)."""
    curses.curs_set(0)
    _init_colors()
    stdscr.timeout(50)

    running = False
    start_time = None
    elapsed = 0.0
    laps = []

    while True:
        if running:
            elapsed = time.monotonic() - start_time

        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        time_str = format_chrono(elapsed)

        # Big centered chrono
        tw = _big_text_width(time_str)
        cx = max(0, (max_x - tw) // 2)
        cy = max(1, min(4, (max_y - _DIGIT_HEIGHT) // 4))

        title = "STOPWATCH"
        _safe_addstr(
            stdscr, cy - 1, max(0, (max_x - len(title)) // 2),
            title,
            curses.color_pair(COLOR_LABEL) | curses.A_BOLD,
        )

        color = COLOR_TIME if running else COLOR_DIM
        _draw_big_text(
            stdscr, cy + 1, cx, time_str,
            curses.color_pair(color) | curses.A_BOLD,
        )

        # Laps
        lap_start_y = cy + 1 + _DIGIT_HEIGHT + 2
        visible_laps = max(0, max_y - lap_start_y - 2)
        show_laps = laps[-visible_laps:] if visible_laps > 0 else []

        for i, (lap_num, lap_time, lap_split) in enumerate(show_laps):
            row = lap_start_y + i
            split_str = format_chrono(lap_split)
            total_str = format_chrono(lap_time)
            line = f"  Lap {lap_num:<3}  {split_str:>12}  {total_str:>12}"
            _safe_addstr(
                stdscr, row, max(0, (max_x - len(line)) // 2),
                line,
                curses.color_pair(COLOR_LAP),
            )

        # Help
        if running:
            help_text = " space:lap  s:stop  r:reset  q:quit"
        elif elapsed > 0:
            help_text = " space:start  r:reset  q:quit"
        else:
            help_text = " space:start  q:quit"

        _safe_addstr(stdscr, max_y - 1, 0, help_text, curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()
        if key == -1:
            continue

        if key == ord("q") or key == 27:
            return elapsed

        elif key == ord(" "):
            if not running:
                if elapsed > 0:
                    # Resume
                    start_time = time.monotonic() - elapsed
                else:
                    # Fresh start
                    start_time = time.monotonic()
                    laps.clear()
                running = True
            else:
                # Lap
                prev = laps[-1][1] if laps else 0.0
                lap_split = elapsed - prev
                laps.append((len(laps) + 1, elapsed, lap_split))

        elif key == ord("s"):
            if running:
                elapsed = time.monotonic() - start_time
                running = False

        elif key == ord("r"):
            if not running:
                elapsed = 0.0
                start_time = None
                laps.clear()


# ── Timer mode ────────────────────────────────────────────────────────────────

def run_timer(stdscr, minutes):
    """Countdown timer for N minutes."""
    curses.curs_set(0)
    _init_colors()
    stdscr.timeout(100)

    duration = minutes * 60.0
    start_time = time.monotonic()
    paused = False
    pause_elapsed = 0.0
    pause_start = None

    while True:
        if paused:
            elapsed = pause_elapsed
        else:
            elapsed = time.monotonic() - start_time

        remaining = duration - elapsed
        finished = remaining <= 0

        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        if finished:
            time_str = "00:00"
        else:
            time_str = format_timer(remaining)

        tw = _big_text_width(time_str)
        cx = max(0, (max_x - tw) // 2)
        cy = max(1, min(4, (max_y - _DIGIT_HEIGHT) // 4))

        total_str = format_timer(duration)
        title = f"TIMER  {total_str}"
        _safe_addstr(
            stdscr, cy - 1, max(0, (max_x - len(title)) // 2),
            title,
            curses.color_pair(COLOR_LABEL) | curses.A_BOLD,
        )

        if finished:
            color = COLOR_ALERT
            # Flash effect
            tick = int(time.monotonic() * 4) % 2
            attr = curses.color_pair(color) | curses.A_BOLD
            if tick:
                attr |= curses.A_REVERSE
            _draw_big_text(stdscr, cy + 1, cx, time_str, attr)

            done_msg = "TIME'S UP!"
            _safe_addstr(
                stdscr, cy + 1 + _DIGIT_HEIGHT + 1,
                max(0, (max_x - len(done_msg)) // 2),
                done_msg,
                curses.color_pair(COLOR_ALERT) | curses.A_BOLD | curses.A_BLINK,
            )
        else:
            color = COLOR_TIME if not paused else COLOR_DIM
            _draw_big_text(
                stdscr, cy + 1, cx, time_str,
                curses.color_pair(color) | curses.A_BOLD,
            )

            # Progress bar
            bar_y = cy + 1 + _DIGIT_HEIGHT + 1
            bar_w = min(40, max_x - 4)
            if bar_w > 4:
                ratio = max(0.0, min(1.0, elapsed / duration))
                filled = int(ratio * bar_w)
                bar = "█" * filled + "░" * (bar_w - filled)
                pct = f" {int(ratio * 100)}%"
                bx = max(0, (max_x - bar_w - len(pct)) // 2)
                _safe_addstr(
                    stdscr, bar_y, bx, bar,
                    curses.color_pair(COLOR_TIME),
                )
                _safe_addstr(
                    stdscr, bar_y, bx + bar_w, pct,
                    curses.color_pair(COLOR_DIM),
                )

        if finished:
            help_text = " r:restart  q:quit"
        elif paused:
            help_text = " space:resume  r:restart  q:quit"
        else:
            help_text = " space:pause  r:restart  q:quit"

        _safe_addstr(stdscr, max_y - 1, 0, help_text, curses.A_DIM)
        stdscr.refresh()

        key = stdscr.getch()
        if key == -1:
            continue

        if key == ord("q") or key == 27:
            break

        elif key == ord(" "):
            if finished:
                pass
            elif paused:
                start_time = time.monotonic() - pause_elapsed
                paused = False
                pause_start = None
            else:
                pause_elapsed = time.monotonic() - start_time
                paused = True

        elif key == ord("r"):
            start_time = time.monotonic()
            paused = False
            pause_elapsed = 0.0
            pause_start = None


# ── Pipe chronometer (non-curses) ────────────────────────────────────────────

def run_pipe_chrono(stdin_lines):
    """Read stdin lines, pass them through, then print elapsed time.
    Used for: some_command | clock -c"""
    import sys

    start = time.monotonic()
    for line in stdin_lines:
        sys.stdout.write(line)
        sys.stdout.flush()
    elapsed = time.monotonic() - start

    # Print timing summary
    sys.stderr.write(f"\n⏱  {format_chrono(elapsed)}\n")
