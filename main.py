import json
import random
import threading
import time
from typing import Dict, List
from datetime import datetime, timezone
import websocket
from rich.console import Console
from rich.progress import Progress
import os
import argparse

console = Console()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_info(msg, theme="cyan"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"{timestamp} [CloudNine] {msg}", style=theme)

def log_error(msg, theme="red"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"{timestamp} [CloudNine] {msg}", style=theme)

class CloudNinePresence:
    def __init__(self, db_dir="db", retry_delay=5):
        self.tokens = []
        self.activities = {}
        self.console = Console()
        self.db_dir = db_dir
        self.retry_delay = retry_delay
        self._load_configs()
        self.ack = json.dumps({"op": 1, "d": None})

    def _load_configs(self):
        with Progress() as progress:
            task = progress.add_task("[cyan]Initializing CloudNine...", total=100)
            time.sleep(0.5)  # Simulate some startup work
            progress.update(task, advance=20)

            try:
                with open(f"{self.db_dir}/spotify songs.json", "r", encoding="utf-8") as f:
                    self.songs = json.load(f)
                progress.update(task, advance=20)
                with open(f"{self.db_dir}/config.json", "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                progress.update(task, advance=20)
                with open(f"{self.db_dir}/custom status.txt", "r", encoding="utf-8") as f:
                    self.status = [line.strip() for line in f]
                progress.update(task, advance=20)
                with open(f"{self.db_dir}/tokens.txt", "r", encoding="utf-8") as f:
                    raw_tokens = [line.strip().split(":")[0] if ":" in line else line.strip() for line in f]
                    self.tokens = [t for t in raw_tokens if len(t) > 50]
                    if len(self.tokens) != len(raw_tokens):
                        log_error(f"Skipped {len(raw_tokens) - len(self.tokens)} invalid tokens")
                progress.update(task, advance=20)
            except FileNotFoundError as e:
                log_error(f"Configuration file not found: {e}")
                raise
            except json.JSONDecodeError as e:
                log_error(f"Invalid JSON in configuration: {e}")
                raise

    def _nonce(self):
        now = datetime.now(timezone.utc)
        unix_ts = int(now.timestamp() * 1000)
        return str((unix_ts - 1420070400000) * 4194304)

    def _rand_time(self):
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        return now - random.randint(100000, 10000000)

    def _pick_weighted(self, stuff):
        total = sum(stuff.values())
        weights = [v / total for v in stuff.values()]
        return random.choices(list(stuff.keys()), weights=weights, k=1)[0]

    def _make_payload(self, token):
        status_type = self._pick_weighted(self.config["status"])
        activities23 = []

        if status_type == "playing":
            game = self._pick_weighted(self.config["games"])
            activities23.append({"type": 0, "timestamps": {"start": self._rand_time()}, "name": game})
        elif status_type == "spotify":
            song = random.choice(self.songs)
            activities23.append({
                "id": "spotify:1",
                "type": 2,
                "flags": 48,
                "name": "Spotify",
                "state": song["artists"][0]["name"],
                "details": song["name"],
                "timestamps": {
                    "start": int(datetime.now(timezone.utc).timestamp() * 1000),
                    "end": int(datetime.now(timezone.utc).timestamp() * 1000) + random.randint(100000, 300000)
                },
                "party": {"id": f"spotify:{self._nonce()}"},
                "assets": {"large_image": f"spotify:{song['images'][0]['url'].split('https://i.scdn.co/image/')[1]}"}
            })
        elif status_type == "visual_studio":
            workspace = random.choice(self.config["visual_studio"]["workspaces"])
            filename = random.choice(self.config["visual_studio"]["names"])
            activities23.append({
                "type": 0,
                "name": "Visual Studio Code",
                "state": f"Workspace: {workspace}",
                "details": f"Editing {filename}",
                "application_id": "383226320970055681",
                "timestamps": {"start": self._rand_time()},
                "assets": {
                    "small_text": "Visual Studio Code",
                    "small_image": "565945770067623946",
                    "large_image": self.config["visual_studio"]["images"][filename.split(".")[1]]
                }
            })

        if self.config["update_status"] and self._pick_weighted(self.config["custom_status"]) == "yes":
            custom = random.choice(self.status)
            activities23.append({"type": 4, "state": custom, "name": "Custom Status", "id": "custom", "emoji": {"id": None, "name": "😃", "animated": False}})

        payload = json.dumps({
            "op": 3,
            "d": {
                "since": 0,
                "activities": activities23,
                "status": random.choice(["online", "dnd", "idle"]),
                "afk": False
            }
        })
        self.activities[token] = payload
        log_info(f"Updated presence for {token[:32]} to {status_type}")
        return payload

    def connect(self, token, retries=0, max_retries=5):
        ws = None
        try:
            ws = websocket.WebSocket()
            ws.connect("wss://gateway.discord.gg/?v=6&encoding=json")
            data = json.loads(ws.recv())
            heartbeat = data["d"]["heartbeat_interval"]

            device = self._pick_weighted({"Discord iOS": 25, "Windows": 75})
            ws.send(json.dumps({
                "op": 2,
                "d": {"token": token, "properties": {"$os": device, "$browser": device, "$device": device}},
                "s": None,
                "t": None
            }))

            ws.send(self._make_payload(token))

            def rotate_status():
                time.sleep(300)
                ws.send(self._make_payload(token))

            threading.Thread(target=rotate_status, daemon=True).start()

            while True:
                time.sleep(heartbeat / 1000)
                ws.send(self.ack)
                ws.send(self.activities[token])
        except Exception as e:
            if retries < max_retries:
                delay = min(self.retry_delay * (2 ** retries), 60)
                log_error(f"Connection failed for {token[:32]}: {e}, retrying in {delay}s ({retries+1}/{max_retries})")
                time.sleep(delay)
                self.connect(token, retries + 1, max_retries)
            else:
                log_error(f"Max retries reached for {token[:32]}: {e}")
        finally:
            if ws:
                ws.close()

    def start(self):
        hosted_count = 0
        total_tokens = len(self.tokens)

        with Progress() as progress:
            task = progress.add_task("[cyan]Hosting accounts...", total=total_tokens)
            for token in self.tokens:
                t = threading.Thread(target=self.connect, args=(token,), daemon=True)
                t.start()
                hosted_count += 1
                progress.update(task, advance=1, description=f"[cyan]Hosting accounts: {hosted_count}/{total_tokens}")
                log_info(f"Started thread for {token[:32]}")
                time.sleep(0.1)

        clear_console()
        banner = """
        ┌──────────────────────────────┐
        │  CloudNine Presence v1.0     │
        └──────────────────────────────┘
          Hosted: {hosted_count}/{total_tokens}  |  {date}
        """.format(hosted_count=hosted_count, total_tokens=total_tokens, date=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'))
        self.console.print(banner, style="bold cyan")

def parse_args():
    parser = argparse.ArgumentParser(description="CloudNine Discord Presence Manager")
    parser.add_argument("--db-dir", default="db", help="Directory for config files")
    parser.add_argument("--retry-delay", type=int, default=5, help="Initial retry delay in seconds")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    try:
        cloudnine = CloudNinePresence(db_dir=args.db_dir, retry_delay=args.retry_delay)
        cloudnine.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_info("Shutting down CloudNine")
    except Exception as e:
        log_error(f"Fatal error: {e}")