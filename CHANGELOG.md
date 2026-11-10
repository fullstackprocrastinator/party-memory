# Changelog

## 0.8.0 — Little Comforts

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

## 0.7.0 — Good Company

- Added optional player hover reminders with recorded adventures together, the last meeting and favourite status. Private notes can be included separately in Settings and are off by default. Hover reminders defer restricted reads during combat.
- Added optional end-of-adventure recaps with quick favourite buttons and shortcuts to companion or adventure notes. Recaps wait until combat and loading screens end, support larger historical rosters, and can be dismissed. Enable them in Settings.
- Added recovery of a recent active adventure after a UI reload or brief reconnect. Recovery requires the same character and exact party roster within five minutes of the last recorded checkpoint. Observed party endings, changed rosters and expired checkpoints start a new adventure. Time away is excluded from the recorded duration, and reunion notices are not repeated for a resumed party.
- Added up to 20 custom companion tags alongside the three presets. Create, rename, apply, search and filter your tags. Removing a custom tag requires confirmation and removes it from all companions.
- Added a Character filter to Adventures and Companions. Companion profiles, notes and favourites remain shared across your characters in the same saved journal.
- Added a dedicated Settings panel for recording, reunion notices, favourites-first sorting, hover reminders, private tooltip notes, recaps and the minimap button. Open it from the journal or `/ff settings`.
- Preserved existing adventures, notes, nicknames, favourites, pins, preset tags and preferences. Forgotten active parties and companions remain suppressed when a matching party is recovered after a reload.

Target: WoW Forever 1.60.1, interface 16001. Automated Lua tests cover the new features and existing behaviour; live-client verification of 0.7.0 is still required. Promotional images are labelled demonstrations rendered from the addon Lua with fictional sample data.

## 0.6.2 — Forever launch

- Packaged Familiar Faces for the live WoW Forever client, version 1.60.1 (interface 16001).
- Added a direct install ZIP and instructions for bringing a beta journal into the live client.
- Preserved party tracking, saved history, notes, and settings. No saved-data migration is needed when upgrading within the same installation.

Launch client metadata checked against build 70755. Live realm gameplay has not yet been verified.

## 0.6.1

- Reviewed against Blizzard's October 15 beta development notes and installed WoW Forever version metadata 1.60.1.70450.
- Fixed recording same-realm players when UnitName returns no realm, including the current character.
- Deferred restricted and incomplete player names safely until usable roster information is available.
- Preserved an active adventure during loading-screen world transfers. Briefly empty rosters receive a five-second grace period after entering the world.
- Kept the Forever package interface at 16001 and preserved existing saved history and settings.

Validation: all 26 Lua 5.1 tests pass. This is an automated compatibility review, not an in-game verification on build 70450.

## 0.6.0

- Added Recent companions, a shortcut to everyone recorded in your most recent party, independent of pinned sorting.
- Added private Helpful guide, Quest buddy and Run again tags, with tag filtering and search.
- Added adventure notes alongside individual companion notes. Adventure drafts use the existing Save, Discard and Cancel protection.
- Added pinned adventures, sorted above other entries, and a Pins filter.
- Added how-we-met profiles showing first saved adventure, latest adventure and total recorded parties.
- Added a complete journal-and-settings text export through Export backup or `/ff export`. Large backups use ordered copyable parts with safe Unicode boundaries.
- Added automatic journal scaling to fit smaller screens, single-line labels and full hover details for long names.
- Added keyboard navigation: Tab moves between search and detail fields; Enter opens the first search result or saves detail edits. Escape cancels the unsaved-change prompt.
- Preserved existing saved history, notes, nicknames, favourites and settings.

Validation: 23 deterministic Lua 5.1 tests pass, including adventure draft protection, tag filtering, recent-party selection, first/latest meetings, backup round trips, multipart copying, small-screen fitting and keyboard editing. In-game validation remains required.

## 0.5.0

- Added saved journal size and position, restored when you reopen the addon or reload the UI.
- Added Save, Discard and Cancel choices for unsaved notes and nicknames when switching companions, opening another adventure, forgetting an entry or closing the journal, including Escape.
- Kept note drafts intact during incoming roster and location updates.
- Added current-party markers and an In your party filter. Party membership updates even when recording is paused.
- Added Last 7 days and Last 30 days history filters, with Clear filters restoring the full journal.
- Added private companion nicknames, included in name and note searches. Save note saves both fields.
- Added a draggable minimap journal button, a saved hide preference and `/ff minimap` to toggle it.
- Added `/ff reset window` to restore the default journal placement and dimensions.
- Preserved existing history, notes, favourites and settings.

Validation: 19 deterministic Lua 5.1 tests pass, including draft protection, Escape/cancel, geometry restoration, nickname and time filters, and minimap dragging/toggling. In-game validation remains required. Feature images use labelled sample data.

## 0.4.0

- Added optional reunion chat notices with a previous adventure and saved note, once per companion per party during the addon session.
- Added a Last adventure column and profile detail, with full date details in companion tooltips.
- Added a saved Favourites first preference, keeping favourites above other companions when sorting.
- Added Helpful, Patient and Great company note prompts. Click Save note to save a draft.
- Added confirmed Forget adventure and Forget companion actions, with encounter counts updated after removal.
- Preserved companion notes and favourites when an adventure is removed. Forgotten entries are not immediately recreated by the active party.
- Added `/ff notices` and saved reunion-notice preferences.
- Existing history, notes and favourites remain compatible.

Validation: 15 deterministic Lua 5.1 tests pass; in-game validation of the new features remains required. Demonstration images use labelled sample data.

## 0.3.2

- Added a stylised gold Familiar Faces title graphic.

## 0.3.1

- Added teal journal panels, gold borders, native icons and clearer selection highlights.
- Added Created by SqueezyLemons with a copyable CurseForge projects link.
