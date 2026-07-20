# Proposal: v1-core — Path Detection, Installation, and Removal

## Why

The ACE modding workflow is entirely manual: users must navigate hidden OS directories, manually edit JSON files to set car GUIDs, and risk corrupting their game data when removing content. A GUI tool that automates path detection, installation, and clean removal eliminates the primary friction points for the ACE modding community.

## What

Deliver a working desktop application (MVP) that:

1. Auto-detects the ACE save directory on Windows and Linux/Proton
2. Installs `.spkg` car mods by copying/extracting to `Mods/`
3. Installs `.zip` liveries by extracting to `External Liveries/` with automatic car GUID injection
4. Removes installed mods and liveries cleanly with rollback support
5. Persists configuration across sessions
6. Provides a modern Flet-based GUI

## What's Out of Scope (v1)

- Overtake.gg / RaceDepartment API integration (post-MVP)
- In-app preview of liveries (post-MVP)
- Auto-updater (post-MVP)
- Backup/restore of entire ACE profile (post-MVP)

## Approach

- Core logic in pure Python (pathlib, zipfile, json, shutil) — testable without GUI
- Flet wraps the core as a desktop GUI
- All filesystem operations go through an abstraction layer (`StorageManager` class) so the game path and I/O can be mocked in tests
- CAREFUL: `.spkg` format validation — first task is to experimentally determine if it's ZIP or proprietary
