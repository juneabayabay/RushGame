"""Pick a game from this repository and start it."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from games.catalog import GAMES

ROOT = Path(__file__).resolve().parent


def launch(game: dict) -> int:
    if "module" in game:
        command = [sys.executable, "-m", game["module"]]
        folder = ROOT
    else:
        folder = ROOT / "games" / game["folder"]
        command = [sys.executable, game["script"]]
    print(f"\nStarting {game['name']}...\n")
    return subprocess.call(command, cwd=folder)


def main() -> None:
    print("Games")
    print("-----")
    for index, game in enumerate(GAMES, start=1):
        print(f"  {index}. {game['name']}")
    print("  q. Quit")

    while True:
        choice = input("\nPick a game: ").strip().lower()
        if choice in {"q", "quit", ""}:
            return
        if choice.isdigit() and 1 <= int(choice) <= len(GAMES):
            launch(GAMES[int(choice) - 1])
            return
        print(f"Type a number from 1 to {len(GAMES)}, or q to quit.")


if __name__ == "__main__":
    main()
