# Design: v1-core — Architecture and Technical Decisions

## High-Level Architecture

```
┌─────────────────────────────────────────────┐
│                  Flet GUI                     │
│  (main.py, views/, widgets/)                 │
├─────────────────────────────────────────────┤
│              Core Logic Layer                 │
│  (storage_manager.py, spkg_handler.py,       │
│   livery_handler.py, config_manager.py)      │
├─────────────────────────────────────────────┤
│         Python Standard Library               │
│  (pathlib, zipfile, json, shutil, os)        │
└─────────────────────────────────────────────┘
```

## Key Decisions

### Decision 1: Core + GUI separation
Core logic lives in pure Python modules with zero GUI imports. This enables:
- Unit testing without Flet
- Future CLI mode without changes to business logic
- Swap Flet for PySide6 (or another GUI) if Flet proves insufficient

### Decision 2: StorageManager as I/O abstraction
All filesystem operations go through `StorageManager`, which wraps `pathlib` and `shutil`. The game base path is injected at construction time. In tests, a `TempStorageManager` subclass uses a temporary directory.

### Decision 3: Config in XDG/config directory (not game dir)
Config file goes to `~/.config/ACE_GUI/config.json` on Linux and `%APPDATA%/ACE_GUI/config.json` on Windows. This prevents accidental deletion when the user clears game data and keeps config separate from game state.

### Decision 4: Flet for GUI — with escape hatch
Flet is the primary GUI framework due to Flutter's modern rendering and cross-platform consistency. However, the GUI layer is thin (< 500 loc). If Flet blocks a critical feature (e.g., native folder picker, drag-and-drop), switching to PySide6 requires only rewriting the `views/` directory.

### Decision 5: SPKG format probe
Before any extraction, the system checks the magic bytes. This single check determines copy-vs-extract behavior. No speculative extraction.

## Rollback Strategy

- Before any destructive operation (delete mod, delete livery), the system creates a timestamped backup in `{ACE_PATH}/.ace_gui_backups/{timestamp}/`
- On success, the backup is deleted
- On failure, the system restores from backup and logs the event
- User can also trigger "Undo last install" from a history panel (post-MVP)

## Data Flow

```
User drops .zip ──→ Type detection ──→ Livery flow
                    ├── .spkg ──→ Mod flow
                    └── other ──→ Error

Livery flow:
  .zip → extract to temp/ → scan for JSON config
  → read garage (saved_cars) → show modal → user picks car
  → inject GUID → move to External Liveries/<guid>/ → cleanup temp/

Mod flow:
  .spkg → probe magic bytes → ZIP? extract : copy
  → copy to Mods/ → confirm
```
