# Familiar Faces 0.8.0 — Little Comforts

- Replaced cycling filters with selectable menus for activity, class, character, date and tags. Added a role menu.
- Added **Remember my view**: restore the last tab, search, filters and sort order between logins. Use **Reset view** or `/ff reset view` for a fresh view.
- Expanded companion and adventure notes to a scrolling, multiline editor with a 1,000-character counter. Enter adds a line; **Save note** saves your changes. Draft protection remains in place.
- Added historical Tank, Healer, Damage and Unknown roles to adventure members and companion profiles. Role filters use each adventure's recorded role or a companion's latest recorded role. Roles are never guessed from class.
- Added mouse-wheel paging over journal rows, shared-history buttons and longer filter menus.
- Improved large-journal browsing with a shared history index, per-query search text and precomputed sort values.
- Added **Import backup** in Settings and `/ff import`. Preview changes, merge with duplicate detection, or explicitly replace the journal. Existing text wins merge conflicts; favourites, pins and tags combine. Settings are preserved.
- Imports validate data without executing pasted code. They require a complete archive, confirmation, solo play and no combat; a changed journal requires a new preview.

Existing history, notes, nicknames, favourites, tags, pins and preferences are preserved when updating. Commands remain `/ff` and `/familiarfaces`.

Target: WoW Forever 1.60.1, interface 16001. This update adds no new client-version requirement. Automated tests run against mocked WoW APIs; live-client verification of 0.8.0 is still required. Gallery images are labelled demonstrations generated from the actual addon Lua with fictional data.
