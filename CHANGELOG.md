# Changelog

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
