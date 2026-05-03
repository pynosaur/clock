#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-05-03

import curses
import sys
import os
from pathlib import Path
from datetime import timezone

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app import __version__
from app.core.timezones import parse_tz
from app.core.ui import run_clock, run_chrono, run_timer, run_pipe_chrono
from app.utils.doc_reader import read_app_doc


def print_help():
    doc = read_app_doc('clock')

    desc = doc.get('description', 'Terminal clock, stopwatch, and timer')
    usage = doc.get('usage', ['clock [OPTIONS] [TIMEZONE...]'])
    options = doc.get('options', [])
    examples = doc.get('examples', [])

    print(f"clock - {desc}")
    print("\nUSAGE:")
    for u in usage:
        print(f"    {u}")

    if options:
        print("\nOPTIONS:")
        for opt in options:
            print(f"    {opt}")

    if examples:
        print("\nEXAMPLES:")
        for ex in examples:
            print(f"    {ex}")


def print_version():
    doc = read_app_doc('clock')
    print(doc.get('version', __version__))


def main():
    args = sys.argv[1:]

    if not args:
        # Default: show local clock
        try:
            from datetime import datetime
            local_tz = datetime.now().astimezone().tzinfo
            local_name = datetime.now().astimezone().strftime("%Z")
            zones = [(local_name, local_tz)]
            curses.wrapper(lambda stdscr: run_clock(stdscr, zones))
        except KeyboardInterrupt:
            pass
        return 0

    # Parse flags
    if args[0] in ("-h", "--help", "help"):
        print_help()
        return 0

    if args[0] in ("-v", "--version"):
        print_version()
        return 0

    # Chronometer mode
    if args[0] == "-c":
        # Check if stdin is a pipe (not a terminal)
        if not os.isatty(sys.stdin.fileno()):
            run_pipe_chrono(sys.stdin)
            return 0
        # Interactive stopwatch
        try:
            curses.wrapper(run_chrono)
        except KeyboardInterrupt:
            pass
        return 0

    # Timer mode
    if args[0] == "-t":
        if len(args) < 2:
            print("clock: -t requires minutes argument", file=sys.stderr)
            print("Usage: clock -t <minutes>", file=sys.stderr)
            return 1
        try:
            minutes = float(args[1])
        except ValueError:
            print(f"clock: invalid minutes value: {args[1]}", file=sys.stderr)
            return 1
        if minutes <= 0:
            print("clock: minutes must be positive", file=sys.stderr)
            return 1
        try:
            curses.wrapper(lambda stdscr: run_timer(stdscr, minutes))
        except KeyboardInterrupt:
            pass
        return 0

    # Timezone clock mode: clock UTC-3 UTC GMT+5:30
    zones = []
    for spec in args:
        try:
            label, tz = parse_tz(spec)
            zones.append((label, tz))
        except ValueError as e:
            print(f"clock: {e}", file=sys.stderr)
            return 1

    if not zones:
        print("clock: no valid timezones specified", file=sys.stderr)
        return 1

    try:
        curses.wrapper(lambda stdscr: run_clock(stdscr, zones))
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
