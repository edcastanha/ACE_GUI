# Tasks: v1-core

## Phase 1 — Foundation & Validation

- [ ] **T1.1** Validate `.spkg` format experimentally: download an ACE car mod, inspect magic bytes, confirm if it's ZIP or proprietary
- [ ] **T1.2** Set up Python project structure: `src/ace_gui/`, `tests/`, `pyproject.toml` with dependencies (flet, pytest)
- [ ] **T1.3** Implement `ConfigManager` — read/write JSON config in XDG path, default values, corruption recovery

## Phase 2 — Path Detection

- [ ] **T2.1** Implement `WindowsPathDetector` — read `%USERPROFILE%\Saved Games\ACE`, validate existence
- [ ] **T2.2** Implement `LinuxProtonPathDetector` — scan compatdata/1548780 under default and custom Steam libraries, handle Flatpak
- [ ] **T2.3** Implement `StorageManager` — wraps pathlib/shutil, injectable base path, create missing dirs
- [ ] **T2.4** Implement `ManualPathSelector` — native folder picker via Flet `FilePicker` or fallback to `tkinter.filedialog`

## Phase 3 — Installation

- [ ] **T3.1** Implement `SpkgHandler` — probe magic bytes, extract (if ZIP) or copy (if binary), overwrite confirmation with backup
- [ ] **T3.2** Implement `LiveryHandler` — extract ZIP to temp, find JSON config, inject GUID via `json` module, move to External Liveries
- [ ] **T3.3** Implement `GarageReader` — scan `profile_data/*/saved_cars/*.json`, extract name+GUID, deduplicate

## Phase 4 — Removal

- [ ] **T4.1** Implement `Uninstaller` — remove mod/livery files, clean up empty parent dirs, rollback on failure
- [ ] **T4.2** Implement `BackupManager` — create timestamped backup before destructive ops, restore on failure, cleanup on success

## Phase 5 — GUI (Flet)

- [ ] **T5.1** Build main window layout: sidebar (mods list, liveries list), central panel, status bar
- [ ] **T5.2** Build setup screen (first launch): show detected path, manual override button
- [ ] **T5.3** Build mod installation view: drag-drop zone or file picker button, progress indicator
- [ ] **T5.4** Build livery installation modal: car selection list with search, GUID preview
- [ ] **T5.5** Wire all GUI actions to Core Logic layer
- [ ] **T5.6** Add confirmation dialogs for all destructive actions

## Phase 6 — Testing & Polish

- [ ] **T6.1** Unit tests for `StorageManager`, `ConfigManager`, `SpkgHandler`, `LiveryHandler`, `GarageReader`, `Uninstaller`
- [ ] **T6.2** Integration test: full install and uninstall cycle with mock game directory
- [ ] **T6.3** Manual test on Windows (real ACE install)
- [ ] **T6.4** Manual test on Linux Proton (real ACE install)
- [ ] **T6.5** Handle edge cases: corrupted files, permission errors, disk full, concurrent access
