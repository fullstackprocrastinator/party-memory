# Familiar Faces 0.7.0 live-client checks

Automated tests use Lua 5.1 and mocked WoW APIs. The promotional images execute the addon Lua with fictional data; they are not screenshots captured in a live WoW session.

Before publishing, install the Forever ZIP in `_forever_/Interface/AddOns`, retain your SavedVariables, enable Lua errors with `/console scriptErrors 1`, and run these checks:

1. Open `/ff` and `/ff settings`. Confirm old adventures, notes, nicknames, favourites, pins and preset tags remain. Check the window on your normal resolution and UI scale.
2. Hover a previously recorded player outside combat. Confirm adventure count, last meeting and favourite status. Enable private tooltip notes and hover again. Switch hover reminders off and check another hover. Test unit frames and world hover; check no repeated lines or Lua errors.
3. Enable recaps, join an outdoor party, then leave it. Favourite a companion and open a note from the recap. Save it in the journal. Dismiss a subsequent recap with Escape. Leave during combat and confirm the recap waits until combat ends. Repeat with a dungeon party.
4. While still grouped, wait for capture, run `/reload`, then open `/ff`. Confirm one adventure and no extra encounter or reunion notice. Repeat after entering and leaving a dungeon. Disconnect briefly if practical, reconnect within five minutes and check the same behaviour.
5. Disband and reform while online: confirm a new adventure. Reconnect with a different roster, after more than five minutes, or on another character: confirm no merge. A crash only retains what WoW previously saved.
6. Create and apply a custom tag. Search and filter it. Rename it and verify existing companions use the new label. Begin removal, cancel by closing the tag panel, then remove with confirmation. Verify presets remain available. Create more than six tags and check pagination.
7. Record parties on two characters. Cycle Character in both journal tabs and clear filters. Verify the correct lists; companion profiles and counts intentionally remain account-wide.
8. Edit a note without saving, then use a recap note shortcut. Test Save, Discard and Cancel. Also open Settings and custom tags, and check your note draft remains intact.
9. Forget an active adventure or companion and reload in the same party. Confirm it is not immediately recreated. Leave and form a new party: recording may start again.
10. Export a backup and verify custom tags and preferences are present. Restart the client and confirm settings persist.

Target: WoW Forever 1.60.1 / interface 16001. Report failures with client build and Lua error text; do not upload private SavedVariables.

Tooltip integration was checked against the Forever branch of Blizzard's [TooltipDataHandler source](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_SharedXMLGame/Tooltip/TooltipDataHandler.lua), using its post-processing hook with a legacy fallback.
