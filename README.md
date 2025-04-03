# CloudNine Discord Presence

A sleek, minimalistic tool to keep your Discord tokens online with custom rich presence statuses. Built with love by Cloudnine, and designed to flex your Discord game—whether it’s gaming, Spotify vibes, or coding in VS Code.

---

```markdown
## Features

- **Custom Presence**: Randomly cycles through playing games, Spotify tracks, or Visual Studio Code statuses.
- **Auto-Rotation**: Updates your status every 5 minutes to keep it fresh.
- **Smart Retries**: Handles connection drops with exponential backoff (up to 5 retries, capped at 60s).
- **Token Validation**: Skips invalid tokens so you don’t waste time on junk.
- **CLI Control**: Tweak the data directory and retry delay without touching the code.

---

## Requirements

- Python 3.8+
- Dependencies:
  - `rich` (for pretty console output)
  - `websocket-client` (for Discord gateway magic)

Install them with:

pip install rich websocket-client
```

---

## Setup

1. **Clone or Download**  
   Grab this bad boy from the repo or wherever you’re storing it.

2. **Dump your tokens in db/tokens.txt**

3. **Run It**  
   Fire it up with:
   
   python main.py
   ```

---

## Usage

- **Basic Run**:
  ```bash
  python main.py
  ```

- **Custom Options**:
  - Change the data folder:
    ```bash
    python main.py --db-dir my_configs
    ```
  - Set a different retry delay (in seconds):
    ```bash
    python main.py --retry-delay 10
    ```

- **Stop It**:
  Hit `Ctrl+C` to shut it down cleanly.

---

## What It Looks Like

On startup:
```
[cleared console]
[cyan]Loading configs...
┌──────────────────────────────┐
│  CloudNine Presence v1.0     │
└──────────────────────────────┘
  Tokens: 3  |  2025-04-02 12:34:56 UTC
12:34:56 [CloudNine] Started thread for abcdefghijklmnopqrstuvwxyz123456
12:34:57 [CloudNine] Updated presence for abcdefghijklmnopqrstuvwxyz123456 to spotify
```

If something goes wrong:
```
12:34:58 [CloudNine] Connection failed for abcdefghijklmnopqrstuvwxyz123456: timeout, retrying in 5s (1/5)
```

Every 5 minutes, it’ll refresh your status:
```
12:39:57 [CloudNine] Updated presence for abcdefghijklmnopqrstuvwxyz123456 to playing
```

---

## Notes

- **Tokens**: Keep `tokens.txt` safe—those are your Discord keys. Don’t share ’em.
- **Discord Limits**: Too many tokens might hit rate limits. Chill with the numbers if you see issues.
- **Customization**: Tweak `config.json` weights to favor certain statuses (e.g., more Spotify, less VS Code).

---

## Join the Community

Got questions, ideas, or just wanna vibe? Join my Discord server:  
[**Cloudnine Dev**](https://discord.gg/R9Zvw9V4hp)

---

## Credits

- Built by **@god.levi**  
- Powered by Cloudnine’s passion for clean code and Discord flexes.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
```
