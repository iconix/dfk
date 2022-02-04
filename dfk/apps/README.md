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

### Run Tests

```bash
$ poetry run pytest dfk/tests
```
