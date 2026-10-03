# Familiar Faces

Previously called Party Memory. Open with `/ff` or `/familiarfaces`; `/pm` and `/partymemory` still work. The internal `PartyMemory` folder and SavedVariables name are retained so upgrading preserves your history, notes and favourites. Replace the files in your existing addon folder; do not rename it or install a second copy.

Remember the people you adventure with. Familiar Faces automatically records dungeon and outdoor parties, so you can find that helpful healer or questing companion again.

## Features

- Persistent, account-wide history of party rosters, with your character, date, location and dungeon difficulty.
- Search by player, your character, location or personal note.
- Dungeon and questing filters, favourites and player notes.
- Player names use your client's class colours in history, member buttons and player details.
- Click a recorded player to open a whisper or send a party invitation.
- Pause recording and explicitly clear your history when wanted.
- No dependencies, chat logging, telemetry or external data transmission.

## Install and use

Download an install ZIP from Releases, or build one with `pwsh -File scripts/package.ps1`. Extract the `PartyMemory` folder into your game's `Interface/AddOns` directory and restart WoW. Open the browser with `/pm` or `/partymemory`. Join a party to start recording; existing historical groups cannot be recovered.

Select a group on the left, then a player on the right to save a note or favourite them. Whisper and Invite act only when clicked and remain subject to the game's normal permissions and cross-realm restrictions.

Commands: `/pm pause`, `/pm resume`, `/pm clear` (shows confirmation instructions), `/pm clear confirm` (erases all history, notes and favourites).

## Client compatibility and limitations

The default packaging command creates a **WoW Forever** ZIP for client 1.60.1, build 70205, interface **16001**, as reported by the user's client. Use this ZIP for Forever. The source TOC targets Retail interface 120007; build that package explicitly with `pwsh -File scripts/package.ps1 -Client Retail`. A legacy 3.3.5 package can be built with `pwsh -File scripts/package.ps1 -Client 335` (interface 30300). These are compatibility targets, not claims of in-game certification. Private-server modifications may require adjustments.

Each continuous party has one entry. Changing members or locations updates that entry, retaining every companion and a chronological location history. Entering a dungeon labels the entry **Dungeon** and keeps the latest dungeon name even after returning outdoors. Parties that stay outdoors are labelled **Questing**; the addon does not infer whether quests are actually being completed. Leaving/disbanding the party ends the entry; grouping again starts another. Pause/resume or reload also starts a new entry. Raid, arena and battleground groups are excluded. Names are stored with realms; same-named characters on different realms remain separate.

Use **More players** to browse everyone who joined, including members marked **(left)**. Use **More locations** to browse the location history. Existing entries from older versions are preserved as recorded: previous duplicates are not automatically merged because their true party boundaries were not saved. Encounter counts from those entries retain their original meaning; new entries count each player once per continuous party.

Recording defers during combat and retries afterwards. Brief parties that begin and end entirely during combat may be missed. Unknown or restricted player data is retried rather than saved. Recording runs on roster and zone events and every 15 seconds. A reload starts a fresh session. The addon keeps all history until explicitly cleared; a large history will use more memory and search time.

Data lives in WoW's account SavedVariables `PartyMemoryDB`, shared across your characters in that account/client. WoW writes it on normal logout or reload; a crash may lose recent changes. Back up `WTF/Account/<account>/SavedVariables/PartyMemory.lua` to preserve history. Do not include this personal history in public bug reports or distributions.

## Testing

Install Python and `lupa`, then run `python tests/test_addon.py`. Tests execute Lua 5.1 with mocked WoW APIs, covering persistence, roster changes, filters, legacy/modern capture, combat deferral and UI actions. They cannot replace testing in the game. See [the manual test checklist](docs/TESTING.md) before publishing a release.

## Distribution

MIT licensed. See [CurseForge submission instructions](docs/CURSEFORGE.md). Packaging produces a ZIP with `PartyMemory/PartyMemory.toc` directly inside its addon folder; GitHub's automatically generated source ZIP is not an install package.
