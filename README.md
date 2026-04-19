crontab-lint

A CLI tool to validate and explain crontab expressions with conflict detection.

---

## Installation

```bash
pip install crontab-lint
```

Or install from source:

```bash
git clone https://github.com/yourusername/crontab-lint.git
cd crontab-lint
pip install .
```

---

## Usage

Validate a crontab expression and get a human-readable explanation:

```bash
crontab-lint "*/5 * * * *"
# ✔ Valid expression
# Runs every 5 minutes
```

Check a crontab file for conflicts:

```bash
crontab-lint --file /etc/cron.d/myjobs
# ✔ No conflicts detected
# Line 3: "0 2 * * *" — Runs daily at 02:00 AM
# ⚠ Line 7 conflicts with Line 3 (overlapping schedule)
```

### Options

| Flag | Description |
|------|-------------|
| `--file`, `-f` | Path to a crontab file to lint |
| `--explain`, `-e` | Print a plain-English explanation |
| `--strict` | Exit with non-zero code on warnings |
| `--version` | Show the installed version |

---

## Features

- ✅ Validates standard and non-standard crontab expressions
- 📖 Explains schedules in plain English
- ⚠️ Detects conflicting or overlapping job schedules
- 🔧 Works as a CLI tool or importable Python library

---

## License

This project is licensed under the [MIT License](LICENSE).