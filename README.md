<p align="center">
  <img src="assets/branding/github-header.svg" alt="Familiar Faces — Remember the people you adventure with." width="100%">
</p>

<p align="center">
  <a href="#getting-started">Get started</a> ·
  <a href="#features">Features</a> ·
  <a href="#commands">Commands</a> ·
  <a href="https://github.com/fullstackprocrastinator/party-memory/issues">Report an issue</a>
</p>

<p align="center"><strong>WoW Forever 1.60.1</strong> · Version 0.2.1 · MIT licensed · No addon dependencies</p>

---

## A great party shouldn't be forgotten

Maybe it was the healer who saved the run, the tank who explained the boss, or someone who made a long quest chain fun. **Familiar Faces** keeps a personal journal of your party companions, so you can find them again.

Join a party and the addon remembers who was there, when you played, and where you went. Add a note, mark a favourite, and pick up the adventure another day.

## Features

| | What you can do |
| :--- | :--- |
| **Remember your party** | Browse persistent history with player names, realms, dates, locations and dungeon difficulty. |
| **Keep the adventure together** | Entering or leaving a dungeon updates the same continuous party entry. Member changes retain everyone who joined. |
| **Find familiar faces** | Search by player, your character, location or personal note; filter dungeon groups, questing groups and favourites. |
| **Make it personal** | Keep notes and favourites for each player, shared across your characters in the same account/client. |
| **Reconnect** | Select a player to open a whisper or send an invitation through the game's normal social functions. |
| **Read at a glance** | Class-coloured names, with pages for previous players and visited locations. |

## Getting started

### Download

Install packages are available as artifacts from successful [Test and package workflow runs](https://github.com/fullstackprocrastinator/party-memory/actions/workflows/ci.yml). Open a completed run, download **FamiliarFaces-install-packages**, then extract the artifact archive to find the client ZIPs. GitHub may require you to sign in to download artifacts.

For WoW Forever, choose **`FamiliarFaces-0.2.1-Forever.zip`**. GitHub's **Code → Download ZIP** contains the source repository, rather than a ready-to-install addon.

### Install

1. Close WoW.
2. Extract the client ZIP and place its **`PartyMemory`** folder into your game's **`Interface/AddOns`** directory.
3. Restart the game and enable **Familiar Faces** in the character-selection AddOns menu.
4. Log in, type **`/ff`**, and join a party. Recording starts automatically; allow up to 15 seconds for the next periodic capture.

```text
Interface/
└── AddOns/
    └── PartyMemory/
        ├── PartyMemory.toc
        ├── Core.lua
        ├── Store.lua
        └── UI.lua
```

**Upgrading?** Replace the files inside the existing `PartyMemory` folder. The addon was previously named Party Memory; its internal folder and saved-data name remain unchanged so history, notes and favourites survive the rename. Do not rename the folder or install a second copy.

### Use it

Select a group, then select a player to save a note, favourite them, whisper or invite. Use **More players** and **More locations** to explore the whole entry. Invitations and whispers remain subject to the game's permissions, online status and cross-realm restrictions.

## Commands

| Command | Action |
| :--- | :--- |
| `/ff` or `/familiarfaces` | Open or close the window. |
| `/ff pause` | Pause recording. |
| `/ff resume` | Resume recording. |
| `/ff clear` | Show instructions for clearing saved data. |
| `/ff clear confirm` | Erase all saved history, notes and favourites. |

The older `/pm` and `/partymemory` commands still work.

## How party history works

- **One continuous party, one entry.** Members and locations can change without creating another entry.
- **Dungeon visits stay remembered.** Once the party enters a dungeon, the entry keeps the latest dungeon name even after returning outdoors.
- **Outdoor-only parties stay Questing.** This label describes an outdoor group; it does not verify quest completion.
- **Leaving or disbanding ends the entry.** The next party starts another. Reloading the UI or pausing/resuming recording also starts a fresh entry.
- **Earlier records stay intact.** Old duplicates are preserved because earlier versions did not record enough information to safely merge them.

Raid, arena and battleground groups are excluded. History begins when the addon is installed; previous adventures cannot be recovered. Capture waits for unknown or restricted player information and defers unit reads during combat, so very brief parties may be missed. Player encounter counts describe recorded entries, rather than completed dungeons.

## Your journal stays local

Familiar Faces includes **no chat logging, telemetry or automatic data sharing**. It stores character names, realms, group dates, locations, your notes and favourites locally in WoW's account SavedVariables.

WoW writes this data on normal logout or reload. To back it up, copy:

```text
WTF/Account/<account>/SavedVariables/PartyMemory.lua
```

Keep that file private when reporting bugs. The distribution ZIP contains code and the license, not your personal history. History stays until you clear it; very large journals can take more memory and time to search.

## Compatibility

| Package | Target | Validation |
| :--- | :--- | :--- |
| **Forever** | WoW Forever 1.60.1 · interface `16001` | UI loading and party recording observed in-game; full release checklist remains available below. |
| Retail | Interface `120007` | Packaging target; not yet verified in-game. |
| 335 | Legacy 3.3.5 · interface `30300` | Packaging target; not yet verified in-game. |

Use the Forever package for WoW Forever. Do not assume compatibility with a different client just because its package builds successfully.

## Development

The addon uses Lua with no bundled libraries. Build install ZIPs using PowerShell:

```powershell
./scripts/package.ps1                 # WoW Forever (default)
./scripts/package.ps1 -Client Retail
./scripts/package.ps1 -Client 335
```

Packages are written to `dist/`, with the addon folder at the ZIP root.

Run the automated Lua 5.1 tests through Python:

```shell
python -m pip install lupa==2.8
python tests/test_addon.py
```

Tests cover party continuity, member replacements, location history, saved data, filters, legacy API fallbacks and UI interactions with mocked WoW APIs. For client testing, use the [in-game checklist](docs/TESTING.md). For publishing, see the [CurseForge guide](docs/CURSEFORGE.md).

## Feedback and license

Found a problem? [Open an issue](https://github.com/fullstackprocrastinator/party-memory/issues) with your client version, steps to reproduce it and any Lua error text. Please omit account details and personal SavedVariables.

Familiar Faces is released under the [MIT License](LICENSE).

---

<p align="center"><em>Good company is worth remembering.</em></p>
