#!/usr/bin/env python3
"""Telegram üzerinden değişen dış IP adresini bildiren yardımcı betik."""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_IP_SERVICE = "https://api.ipify.org"


def get_public_ip(service_url: str, timeout_seconds: int) -> str:
    with urllib.request.urlopen(service_url, timeout=timeout_seconds) as response:
        ip = response.read().decode("utf-8").strip()

    if not ip:
        raise ValueError("Dış IP servisi boş yanıt döndürdü.")

    return ip


def load_previous_ip(state_file: pathlib.Path) -> str | None:
    if not state_file.exists():
        return None

    return state_file.read_text(encoding="utf-8").strip() or None


def save_ip(state_file: pathlib.Path, ip: str) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(f"{ip}\n", encoding="utf-8")


def send_telegram_message(bot_token: str, chat_id: str, message: str, timeout_seconds: int) -> None:
    endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP hatası: {error.code} - {details}") from error

    if '"ok":true' not in body:
        raise RuntimeError(f"Telegram API beklenmeyen yanıt verdi: {body}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dış IP değiştiğinde Telegram'a bildirim gönderir."
    )
    parser.add_argument(
        "--state-file",
        default=os.environ.get("IP_STATE_FILE", ".ip_state/last_ip.txt"),
        help="Son görülen IP'nin saklanacağı dosya yolu.",
    )
    parser.add_argument(
        "--ip-service",
        default=os.environ.get("IP_SERVICE_URL", DEFAULT_IP_SERVICE),
        help="Dış IP'yi döndüren HTTP endpoint'i.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("IP_NOTIFIER_TIMEOUT", "10")),
        help="HTTP istekleri için zaman aşımı (saniye).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state_file = pathlib.Path(args.state_file)

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID ortam değişkenleri zorunludur.", file=sys.stderr)
        return 2

    try:
        current_ip = get_public_ip(args.ip_service, args.timeout)
        previous_ip = load_previous_ip(state_file)

        if current_ip != previous_ip:
            if previous_ip:
                text = (
                    "⚡ Elektrik/modem sonrası dış IP değişti.\n"
                    f"Eski IP: {previous_ip}\n"
                    f"Yeni IP: {current_ip}"
                )
            else:
                text = f"🔔 İlk IP kaydı alındı: {current_ip}"

            send_telegram_message(bot_token, chat_id, text, args.timeout)
            save_ip(state_file, current_ip)
            print(f"Bildirim gönderildi: {current_ip}")
        else:
            print(f"IP değişmedi: {current_ip}")

    except Exception as error:  # pylint: disable=broad-except
        print(f"Hata: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
