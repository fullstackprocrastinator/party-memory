# In-game test checklist

- Enable Lua errors (`/console scriptErrors 1`), reload and open `/pm`. Check dragging, close, Escape and reopening.
- Join an outdoor party. Verify all other members' realm-qualified names, your character, zone and date. Wait 15 seconds; check that no duplicate roster is added.
- Add/remove a player; verify a new roster and preservation of the old one. Disband and reform the same party; verify a fresh entry.
- Enter a dungeon, change zones, exit it and complete a run. Check activity labels and difficulty.
- Search by name, realm, location, your character and a saved note. Toggle activity and favourite filters. Verify pagination with more than nine records.
- Select each player, save a note, favourite them, reload and log out/in. Verify history, notes and favourites persist. Switch characters and check account-wide history.
- Whisper and invite via clicks outside combat. Check full groups, offline people and cross-realm restrictions produce normal game behaviour.
- Join a raid or battleground: check no new records. Return to a normal party: recording resumes.
- Change roster during combat: verify no Lua errors and capture after combat ends. Test loading-screen/unknown-member retries.
- Pause, change party, resume: verify no paused records. Use `/pm clear`; verify it only gives instructions. `/pm clear confirm` should remove history, notes and favourites.
- Test separately on every client advertised in the release. Report client/build and error text without uploading personal SavedVariables.
