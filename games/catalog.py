"""The list of games this repository can launch.

Add the next game in two steps:

1. Create a folder under games/, for example games/my_game/.
2. Append one entry below.

Easiest shape is a script game: a main.py inside that folder that
starts the game when you run it. Flat imports such as `from hero import ...`
keep working, because the launcher runs the script from inside the folder.

    {"name": "My Game", "folder": "my_game", "script": "main.py"}

A package game is a folder with __main__.py, launched as a module:

    {"name": "My Game", "module": "games.my_game"}
"""

GAMES = [
    {"name": "Gravity Rush Racing", "module": "games.rush"},
    {"name": "Spring Crack", "folder": "crack_platform", "script": "main.py"},
]
