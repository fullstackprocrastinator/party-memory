# Familiar Faces

**Remember the people you adventure with.**

Ever finish a great dungeon run and forget the name of the healer who saved it, the tank who explained the bosses, or the companion who made questing fun? Familiar Faces keeps a personal adventure journal so good company is easier to find again.

## Your adventure journal

- Automatically records dungeon and outdoor parties, including player names, realms, classes, dates and locations.
- Keeps one entry for a continuous party, with member changes and dungeon visits recorded inside it. Forming a party, entering a dungeon and leaving together do not create three separate entries.
- Browse the **Adventures** tab to see activity, location, party size and recorded duration.
- Select an adventure to see its companions and location timeline, then select a player to view their profile.
- Add a private adventure note, such as First Deadmines clear, and find it again through search.
- Pin memorable adventures to keep them above other entries, or use the Pins filter to browse only pinned runs.

## Remember your companions

- Browse the **Companions** tab with class-coloured names, shared-adventure counts, last adventure and last-seen dates.
- Search player names, realms, places, your characters and personal notes.
- Save a private nickname such as Westfall quest buddy; nicknames are searchable too.
- Identify current party members with a green party marker, or use the In your party filter to focus on them.
- Narrow your journal to the last 7 or 30 days, then clear filters to return to everything.
- Filter by activity, class, favourites or players with notes, and click column headings to sort.
- Keep favourites at the top with the optional **Favourites first** setting.
- View a companion's shared adventures and jump back into an entry.
- Open **Recent companions** to see everyone recorded in your latest party, even after the group ends. This shortcut clears the other filters.
- See how you met: first saved adventure, latest adventure and total recorded parties together.
- Add private **Helpful guide**, **Quest buddy** and **Run again** tags. Toggle them in Private tags, filter by tag or search their text.
- Write personal notes, or use **Helpful**, **Patient** and **Great company** prompts. Prompts add to the note field; click **Save note** to keep your changes.
- Save note saves both the note and nickname. Unsaved changes offer Save, Discard or Cancel when switching companions or closing the journal, including Escape. Incoming roster updates keep your draft intact.
- Mark favourites, open a whisper or invite a selected companion using the game's normal social functions. Invites depend on the game's usual restrictions.

## A familiar face joins the party

Optional **reunion notices** show a quiet chat message when you group with someone from your saved history. The message includes your previous adventure and saved note, when available.

Each companion gets at most one notice per party during the current addon session. Repeated roster updates and dungeon transitions do not repeat it. Toggle notices in the journal or with `/ff notices`. Notices and favourites-first sorting are enabled by default and your preferences are saved.

## Keep the memories you want

- **Forget adventure** removes one entry and updates companion encounter counts while keeping their notes and favourites.
- **Forget companion** removes that person's notes, favourite and appearances from your saved history. Other companions remain; an adventure with no remaining companions is removed.
- Both actions ask for confirmation. Forgotten companions can be recorded in a future party. Removing an active adventure suppresses recording for that party until it ends, so the entry does not immediately return.
- Pause or resume recording whenever you like, or clear the entire journal with an explicit confirmation command.

## Made for your adventures

A stylised gold title, teal panels, native game icons and a movable, resizable window make the journal feel at home in your travels. The journal remembers its size and position across reloads. An optional minimap button opens the journal; drag it around the minimap or hide it with the journal toggle. Click **Created by SqueezyLemons** to copy a link to more addons.

The journal scales down to fit smaller screens. Long names remain available in hover details. Tab moves between search and note/nickname fields; Enter opens the first search result or saves detail edits. Escape cancels an unsaved-change prompt.

## Keep a backup

Choose **Export backup** or type `/ff export` to copy a text snapshot of your complete saved journal and settings. The export includes adventures, members, locations, notes, nicknames, tags, pins and preferences. It is a saved-data Lua text archive for safekeeping, with no automatic import button.

Large backups are split into numbered parts. Copy every part into one text file in order, without adding separators or extra characters. Export contains private player names and personal notes; keep it somewhere private. Unsaved edits use the Save/Discard/Cancel prompt before the snapshot is created.

## Commands

| Command | Action |
| --- | --- |
| `/ff` or `/familiarfaces` | Open or close the journal. |
| `/ff pause` | Pause recording. |
| `/ff resume` | Resume recording. |
| `/ff notices` | Toggle reunion chat notices. |
| `/ff minimap` | Show or hide the minimap button. |
| `/ff reset window` | Reset the journal's position and size. |
| `/ff export` | Open the copyable journal backup. |
| `/ff clear` | Show instructions for clearing saved data. |
| `/ff clear confirm` | Erase all saved history, notes and favourites. |

## Compatibility and privacy

This package targets **WoW Forever 1.60.1**, interface **16001**. History begins when the addon is installed; earlier parties cannot be recovered. Outdoor parties are labelled Questing. Raid, battleground and arena groups are excluded.

Your journal is saved locally in your WoW account. Familiar Faces does not collect chat messages, send telemetry or automatically share your notes, nicknames or tags with other players. No other addons are required. Existing Familiar Faces history, notes and favourites are preserved when updating. Recorded parties and durations do not verify dungeon completion, and first/latest summaries reflect the history you have kept.

Created by **SqueezyLemons** · [More addons](https://www.curseforge.com/members/squeezylemons/projects) · [Source and issues](https://github.com/fullstackprocrastinator/party-memory)
