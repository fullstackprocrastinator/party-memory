# WoW Forever compatibility review - 18 October 2026

## Evidence

- Local Battle.net installation metadata identifies WoW Forever as 1.60.1.70450.
- [Blizzard's beta development notes, updated October 15](https://us.forums.blizzard.com/en/wow/t/wow-forever-beta-development-notes-%E2%80%93-updated-october-15/2360696) describe the new beta build and list world-instance transfers caused by party composition changes as a known issue.
- These notes do not announce an interface number change or removal of a party API used by Familiar Faces. The release retains its existing Forever interface target 16001. Installation metadata alone does not report the runtime interface number.

## Changes in 0.6.1

Same-realm players now correctly use the local realm when UnitName omits it. Restricted and empty player information is deferred. PLAYER_LEAVING_WORLD suspends capture until PLAYER_ENTERING_WORLD; an active party gets a five-second grace period for an empty roster after loading. A later confirmed absence still ends the adventure normally.

## Validation

All 26 deterministic Lua 5.1 tests pass, including nil-realm names, restricted/incomplete names, world transfers with empty rosters, and the existing history, UI, notes and export tests. The packaged TOC is checked for version 0.6.1 and interface 16001. Existing SavedVariables retain their names and schema.

No in-game execution on build 70450 was performed. Before publishing, confirm `/dump GetBuildInfo()` reports the expected interface, then group with a same-realm player, enter and leave a dungeon, and check that one continuous adventure is kept. Log out or reload normally to verify saved history persists.
