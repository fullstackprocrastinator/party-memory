# In-game test checklist

- Enable Lua errors (`/console scriptErrors 1`), reload and open `/pm`. Check dragging, close, Escape and reopening.
- Join an outdoor party. Verify all other members' realm-qualified names, your character, zone and date. Wait 15 seconds; check that no duplicate roster is added.
- Add/remove a player; verify the same entry retains all members, marking departed players. Rotate through more than four companions and use More players. Disband and reform the same party; verify a fresh entry.
- Enter a dungeon, change zones, exit it together and complete a run. Verify one entry, retaining the dungeon label and difficulty outdoors. Browse all visited zones with More locations, and search by an earlier outdoor location. An outdoor-only party must remain Questing.
- Search by name, realm, location, your character and a saved note. Toggle activity and favourite filters. Verify pagination with more than nine records.
- Test Adventures and Companions tabs, each sortable column in both directions, class cycling, notes-only and Clear filters. Companion filters should apply to that player's notes/class, rather than another member of the party.
- Select a companion, follow a shared adventure link, then select another party member. Verify the correct notes and whisper target. Clear history while a detail is selected; verify stale actions disappear.
- Drag the Resize control, checking minimum size, header alignment, row widths, pagination and the detail panel. Hover clipped notes and party rows to check tooltips.
- Select each player, save a note, favourite them, reload and log out/in. Verify history, notes and favourites persist. Switch characters and check account-wide history.
- Whisper and invite via clicks outside combat. Check full groups, offline people and cross-realm restrictions produce normal game behaviour.
- Join a raid or battleground: check no new records. Return to a normal party: recording resumes.
- Change roster during combat: verify no Lua errors and capture after combat ends. Test loading-screen/unknown-member retries.
- Pause, change party, resume: verify no paused records. Use `/pm clear`; verify it only gives instructions. `/pm clear confirm` should remove history, notes and favourites.
- Test separately on every client advertised in the release. Report client/build and error text without uploading personal SavedVariables.
