# Party Memory

Remember the people you adventure with. Party Memory automatically records dungeon and outdoor parties, so you can find that helpful healer or questing companion again.

## Features

- Persistent, account-wide history of party rosters, with your character, date, location and dungeon difficulty.
- Search by player, your character, location or personal note.
- Dungeon and questing filters, favourites and player notes.
- Click a recorded player to open a whisper or send a party invitation.
- Pause recording and explicitly clear your history when wanted.
- No dependencies, chat logging, telemetry or external data transmission.

## Install and use

Download an install ZIP from Releases, or build one with `pwsh -File scripts/package.ps1`. Extract the `PartyMemory` folder into your game's `Interface/AddOns` directory and restart WoW. Open the browser with `/pm` or `/partymemory`. Join a party to start recording; existing historical groups cannot be recovered.

Select a group on the left, then a player on the right to save a note or favourite them. Whisper and Invite act only when clicked and remain subject to the game's normal permissions and cross-realm restrictions.

Commands: `/pm pause`, `/pm resume`, `/pm clear` (shows confirmation instructions), `/pm clear confirm` (erases all history, notes and favourites).

## Client compatibility and limitations

The default TOC targets Retail interface 120007. Verify your installed client's interface with `/dump select(4, GetBuildInfo())`; update the TOC when needed. A legacy 3.3.5 package can be built with `pwsh -File scripts/package.ps1 -Client 335` (interface 30300). The exact WoW Forever client has not yet been confirmed. These are compatibility targets, not claims of in-game certification. Private-server modifications may require adjustments.

Outdoor parties are labelled **Questing**; the addon does not infer whether quests are actually being completed. Each roster or location change creates a new entry, and revisiting a roster creates another. Counts measure recorded rosters, not unique dungeon completions. Raid, arena and battleground groups are excluded. Names are stored with realms; same-named characters on different realms remain separate.

Recording defers during combat and retries afterwards. Brief parties that begin and end entirely during combat may be missed. Unknown or restricted player data is retried rather than saved. Recording runs on roster and zone events and every 15 seconds. A reload starts a fresh session. The addon keeps all history until explicitly cleared; a large history will use more memory and search time.

Data lives in WoW's account SavedVariables `PartyMemoryDB`, shared across your characters in that account/client. WoW writes it on normal logout or reload; a crash may lose recent changes. Back up `WTF/Account/<account>/SavedVariables/PartyMemory.lua` to preserve history. Do not include this personal history in public bug reports or distributions.

## Testing

Install Python and `lupa`, then run `python tests/test_addon.py`. Tests execute Lua 5.1 with mocked WoW APIs, covering persistence, roster changes, filters, legacy/modern capture, combat deferral and UI actions. They cannot replace testing in the game. See [the manual test checklist](docs/TESTING.md) before publishing a release.

## Distribution

MIT licensed. See [CurseForge submission instructions](docs/CURSEFORGE.md). Packaging produces a ZIP with `PartyMemory/PartyMemory.toc` directly inside its addon folder; GitHub's automatically generated source ZIP is not an install package.
