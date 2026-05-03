#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-05-03

import unittest
import sys
from pathlib import Path
from datetime import timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.timezones import (
    parse_tz, format_time, format_chrono, format_timer, now_in_tz,
)


class TestParseTimezone(unittest.TestCase):
    def test_utc(self):
        label, tz = parse_tz("UTC")
        self.assertEqual(label, "UTC")
        self.assertEqual(tz, timezone.utc)

    def test_gmt(self):
        label, tz = parse_tz("GMT")
        self.assertEqual(label, "GMT")
        self.assertEqual(tz, timezone.utc)

    def test_utc_minus_3(self):
        label, tz = parse_tz("UTC-3")
        self.assertEqual(label, "UTC-3")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-3))

    def test_gmt_plus_5_30(self):
        label, tz = parse_tz("GMT+5:30")
        self.assertEqual(label, "GMT+5:30")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=5, minutes=30))

    def test_named_est(self):
        label, tz = parse_tz("EST")
        self.assertEqual(label, "EST")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-5))

    def test_named_jst(self):
        label, tz = parse_tz("JST")
        self.assertEqual(label, "JST")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=9))

    def test_named_brt(self):
        label, tz = parse_tz("BRT")
        self.assertEqual(label, "BRT")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-3))

    def test_case_insensitive(self):
        label, tz = parse_tz("utc-3")
        self.assertEqual(tz.utcoffset(None), timedelta(hours=-3))

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            parse_tz("FAKE")


class TestFormatChrono(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_chrono(0), "00:00.00")

    def test_seconds(self):
        self.assertEqual(format_chrono(5.25), "00:05.25")

    def test_minutes(self):
        self.assertEqual(format_chrono(125.5), "02:05.50")

    def test_hours(self):
        self.assertEqual(format_chrono(3661.0), "01:01:01.00")


class TestFormatTimer(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_timer(0), "00:00")

    def test_minutes(self):
        self.assertEqual(format_timer(300), "05:00")

    def test_hours(self):
        self.assertEqual(format_timer(3661), "01:01:01")

    def test_negative(self):
        self.assertEqual(format_timer(-5), "00:00")


class TestFormatTime(unittest.TestCase):
    def test_now_in_utc(self):
        dt = now_in_tz(timezone.utc)
        result = format_time(dt)
        self.assertRegex(result, r"^\d{2}:\d{2}:\d{2}$")


if __name__ == "__main__":
    unittest.main()
