#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-05-03

"""Timezone parsing and time formatting utilities."""

import re
import time
from datetime import datetime, timezone, timedelta


def parse_tz(spec):
    """Parse a timezone spec like UTC, UTC-3, GMT+5:30, EST, etc.
    Returns (label, tzinfo) or raises ValueError."""
    spec = spec.strip()

    aliases = {
        "EST": -5, "EDT": -4,
        "CST": -6, "CDT": -5,
        "MST": -7, "MDT": -6,
        "PST": -8, "PDT": -7,
        "CET": 1, "CEST": 2,
        "EET": 2, "EEST": 3,
        "IST": 5.5,
        "JST": 9,
        "KST": 9,
        "AEST": 10, "AEDT": 11,
        "NZST": 12, "NZDT": 13,
        "BRT": -3,
    }

    upper = spec.upper()

    # Plain UTC / GMT
    if upper in ("UTC", "GMT"):
        return spec.upper(), timezone.utc

    # UTC+N, UTC-N, GMT+N, GMT-N  (including half-hour offsets)
    m = re.match(
        r'^(UTC|GMT)\s*([+-])\s*(\d{1,2})(?::(\d{2}))?$',
        spec, re.IGNORECASE,
    )
    if m:
        prefix = m.group(1).upper()
        sign = 1 if m.group(2) == '+' else -1
        hours = int(m.group(3))
        minutes = int(m.group(4) or 0)
        offset = sign * (hours * 60 + minutes)
        td = timedelta(minutes=offset)
        label = f"{prefix}{m.group(2)}{hours}"
        if minutes:
            label += f":{m.group(4)}"
        return label, timezone(td)

    # Named alias
    if upper in aliases:
        offset_h = aliases[upper]
        td = timedelta(hours=offset_h)
        return upper, timezone(td)

    raise ValueError(f"Unknown timezone: {spec}")


def now_in_tz(tz):
    """Get current datetime in the given timezone."""
    return datetime.now(tz)


def format_time(dt):
    """Format as HH:MM:SS."""
    return dt.strftime("%H:%M:%S")


def format_chrono(elapsed):
    """Format elapsed seconds as HH:MM:SS.cc (centiseconds)."""
    total_cs = int(elapsed * 100)
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"
    return f"{m:02d}:{s:02d}.{cs:02d}"


def format_timer(remaining):
    """Format remaining seconds as HH:MM:SS or MM:SS."""
    if remaining < 0:
        remaining = 0
    total_s = int(remaining)
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
