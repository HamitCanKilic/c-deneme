#!/usr/bin/env python3
"""Raspberry Pi mini demo: LED toggle + temperature card via web UI."""

from __future__ import annotations

import random
from datetime import datetime

from flask import Flask, render_template


class MockLED:
    """Fallback LED implementation for non-Raspberry Pi environments."""

    def __init__(self) -> None:
        self._is_lit = False

    @property
    def is_lit(self) -> bool:
        return self._is_lit

    def on(self) -> None:
        self._is_lit = True

    def off(self) -> None:
        self._is_lit = False


try:
    from gpiozero import LED  # type: ignore

    led = LED(17)
    gpio_mode = "real"
except Exception:  # pragma: no cover - fallback for development environments
    led = MockLED()
    gpio_mode = "mock"

app = Flask(__name__)


@app.get("/")
def index() -> str:
    return render_template("index.html", gpio_mode=gpio_mode)


@app.get("/api/status")
def status() -> tuple[dict[str, object], int]:
    return (
        {
            "led_on": led.is_lit,
            "gpio_mode": gpio_mode,
            "temperature": round(random.uniform(23.0, 31.0), 1),
            "last_update": datetime.now().strftime("%H:%M:%S"),
        },
        200,
    )


@app.post("/api/led/toggle")
def toggle_led() -> tuple[dict[str, object], int]:
    if led.is_lit:
        led.off()
    else:
        led.on()

    return ({"led_on": led.is_lit}, 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
