# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Raspberry Pi controlled ESC/POS thermal receipt printer (USB vendor/product `0x04b8`/`0x0202`, driven via `python-escpos`). `main.py` prints a daily task/weather receipt, and — as part of that same module pipeline — prints a matching workout sheet from `workout_printer/workouts/` for any task named `"Workout - <name>"` due today.

Separately, `takeout_box_server.py` runs a small always-on Flask server that prints Takeout Box order receipts on demand, triggered by an incoming HTTP request rather than cron — see the `takeout_box_printer` section below.

## Commands

```bash
./setup.sh              # one-time: adds pi user to dialout/lp groups, creates venv, installs requirements.txt
./bin/pip install -r requirements.txt   # after adding a dependency
./bin/python3 main.py    # run for real (prints to the physical USB printer)
./bin/python3 takeout_box_server.py   # run the order webhook server for real
```

There is no linter or build step configured in this repo. `tests/` holds a couple of plain dry-run scripts (no pytest) — run directly, e.g. `python3 tests/test_takeout_box_order.py`.

`run.sh` is the production entrypoint invoked by cron/systemd on the Pi for the daily receipt: it `cd`s to `/home/pi/receipt-printer` and logs stdout/stderr to `/home/pi/logs/<date>/reciept.log`. `run_takeout_box_server.sh` is the equivalent long-running entrypoint for the order webhook server (see `takeout-box.service.example` for the systemd unit that keeps it running).

`RecieptPrinter` takes a `dry` flag (`RecieptPrinter(dry=True)`) that skips the real USB printer and just echoes to stdout — use this when iterating locally without hardware attached. `main.py` always runs with `dry=False`; for local testing, instantiate `RecieptPrinter(dry=True)` directly and pass it to `render_receipt()`.

## Architecture

**`RecieptPrinter.py`** is the single hardware abstraction (`RecieptPrinter` class) all modules render through. It wraps `escpos.printer.Usb`, exposes `set`/`set_with_default`/`text`/`cut`, and truncates any non-wrapped `text()` call to `CHAR_WIDTH` (42 chars — the printer's physical line width). When `dry=True` it never touches the USB device.

**`main.py`** is a thin orchestrator: build a `DailyContext` (all network fetching, up front), then hand one `RecieptPrinter` instance and that context to `render_receipt()`. It has no workout-specific logic of its own.

**`tasks_printer/context.py`** does all the data fetching in one place, before any printing happens. `build_context(config)` calls `TickTickAPI` and `fetch_weather` (`data_handlers/`) and returns a `DailyContext` dataclass (`projects`, `weather`, plus `ticktick_error`/`weather_error` strings). Each fetch is wrapped individually — a TickTick outage doesn't block weather, and vice versa — so `DailyContext` always has *something* usable for rendering, even if only error strings.

**`tasks_printer/printer.py`** renders the receipt as an ordered pipeline of modules (`tasks_printer/modules/`):
- `module_classes = [ModuleHeader, ModuleWeather, ModuleSeparator, ModuleTickTick, ModuleWorkout]` — each is instantiated with its own section of `config.ini` (keyed by class name, display-only config now — no fetching) and called in order via `module.render(p, context)`.
- Modules are pure renderers: no network calls, no exceptions expected — they just read `context` (checking the `*_error` fields) and write to `p`. `ModuleHeader`/`ModuleWeather`/`ModuleSeparator` write into whatever receipt is currently open; `ModuleTickTick` and `ModuleWorkout` each own a receipt boundary and call `p.cut()` themselves at the end of their `render()`.
- `ModuleWorkout` (`tasks_printer/modules/workout.py`) scans `context.projects` for today's `"Workout - <name>"` tasks and renders the matching sheet via `workout_printer.printer.render_workout(name)` for each one found — if there's no workout task today it simply returns without printing or cutting anything. This is how the two originally-separate printer packages are wired together; `workout_printer` itself has no knowledge of TickTick.
- `tasks_printer/data_handlers/` holds the actual API clients (`TickTickAPI`, `GoogleCalendarAPI`, `fetch_weather`) and shared domain models (`Event`, `Task`, `Subtask`, `Project` in `models.py`). Only `context.py` should call into these — modules should not talk to the network directly. `GoogleCalendarAPI` currently has no caller in the live pipeline — it was written for a calendar/events feature that was never wired in.

**`workout_printer`** is a standalone template renderer with no printing or hardware concerns of its own: workout sheets are plain-text Jinja2 templates in `workout_printer/workouts/*.txt` (one `{{ date }}` placeholder), named by the file's stem. `render_workout(name)` looks up `<name>.txt` and returns the rendered text, or `None` if the name doesn't match a file — printing that text is the caller's job (currently `ModuleWorkout`). `list_workouts()` enumerates available names. `workout_printer/recomp-plan.md` is personal training/diet notes, not code.

**`reciept_util.filter_emojis`** strips emoji from any user-generated text (task/event titles) before printing, since the thermal printer can't render them — used throughout `data_handlers` and `models.py` whenever a `Task`/`Event`/`TickTickTask` name is constructed.

**`takeout_box_printer`** is a standalone order-receipt renderer for the Takeout Box hardware product, structurally like `workout_printer` (no server/hardware concerns baked in) but triggered live instead of on a daily cycle:
- `models.py` — `Order`/`OrderItem` parse and validate an incoming order dict (`order_number`, `order_name`, `items[]` each with `name`, `color` ∈ `COLORS`, `handedness` ∈ `HANDEDNESS_OPTIONS`); invalid input raises `OrderValidationError`. Each item gets a random funny food note (one of `NOTE_ADJECTIVES` + one of `NOTE_FOODS`, e.g. "extra kimchi") assigned in `OrderItem.__init__` — the note is never accepted from the caller.
- `printer.py` — `render_order(p, order)` prints `res/rally-audio-header.bmp`, the order number/name, each item with its color/handedness/note, then `res/qr.bmp`, and cuts. Both bmp paths are optional (skipped via `.exists()` check) — the QR asset isn't checked in yet; drop `qr.bmp` into `takeout_box_printer/res/` to enable it.
- `server.py` — `create_app(p, auth_token)` builds the Flask app with a single `POST /orders` route: requires `Authorization: Bearer <auth_token>` (constant-time compare), validates the JSON body via `Order.from_dict`, and renders under a lock (one physical printer, serialize concurrent requests) via the shared `RecieptPrinter` instance passed in at startup.
- `takeout_box_server.py` (repo root) is the entrypoint: loads `config.ini`'s `[TakeoutBoxServer]` section for `host`/`port`/`auth_token`, builds one `RecieptPrinter(dry=...)`, and calls `app.run()`. It never touches `tasks_printer`/`workout_printer` — a fully separate pipeline from the daily cron flow.

## Config

`config.ini` (gitignored, not present in repo) provides per-module settings keyed by class name, e.g. `[ModuleTickTick] bearer_token=...`, `[ModuleWeather] latitude=... longitude=... timezone=...`, `[ModuleSeparator] pattern=...`, plus `[TakeoutBoxServer] auth_token=... host=... port=...` for the order webhook server. A module with missing required config sets its own `error_message` and degrades gracefully rather than crashing the whole run.
