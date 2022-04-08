## Apps

### Prerequisites

- python 3.10+
- poetry
- [optional] pyenv
- [windows only] to successfully install the `cytoolz` dependency, I had to download the VS 2019 Installer and install "Desktop Development with C++" (Build Tools) as suggested [here](https://github.com/pytoolz/cytoolz/issues/151#issuecomment-978450797)

### Installation

```bash
$ poetry install
```

### Hero App

```bash
# hint: prepend with `LOG_LEVEL=DEBUG ` to see debug logs
$ poetry run python dfk/apps/hero.py

# OR...

$ poetry shell
$ python dfk/apps/hero.py
```

favorite filters:
```bash
# looking for affordable advanced classes
$ poetry run python dfk/apps/hero.py --max-price 100 --query-limit 1000 --limit 50 -c Paladin -c DarkKnight -c Summoner -c Ninja -c Dragoon -c Sage -c DreadKnight --order-by csAvg

# looking for advanced classes with highest magic damage
$ poetry run python dfk/apps/hero.py --query-limit 1000 --limit 50 -c Paladin -c DarkKnight -c Summoner -c Ninja -c Dragoon -c Sage -c DreadKnight --order-by magDmg

# looking for affordable miners
$ poetry run python dfk/apps/hero.py --max-price 100 --query-limit 1000 --limit 50 -c Warrior -c Knight -c Paladin -c DarkKnight -c Dragoon -p mining --order-by ps
```

### Quest App

```bash
$ poetry run python dfk/apps/quest.py
```

### Run Tests

```bash
$ poetry run pytest dfk/tests
```
