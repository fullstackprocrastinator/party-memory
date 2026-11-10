# Familiar Faces

**Remember the people you adventure with.**

The healer who saved the run. The tank who explained the boss. The questing companion who stayed for one more adventure.

Good company deserves more than a name you almost remember. **Familiar Faces** keeps a personal journal of your dungeon and questing parties, helping you recognise familiar players and find them again.

## New in 0.8.0: Little Comforts

- **Choose, then adventure:** activity, class, character, date, tag and role filters now open selectable menus.
- **Right where you left it:** remember your tab, search, filters and sort between logins, with a Reset view shortcut.
- **Room for the story:** multiline companion and adventure notes hold up to 1,000 characters, with a live counter and scrolling.
- **Remember their role:** see and filter Tank, Healer, Damage or Unknown, using roles actually reported by the game.
- **Browse with a scroll:** use the mouse wheel over journal rows, shared-history buttons and longer filter menus.
- **A smoother growing journal:** shared history indexing and cached sort values reduce repeated work in large collections.
- **Bring your memories along:** preview a text backup, then merge it into your journal or explicitly replace the journal.

## Every party has a story

Familiar Faces automatically records the companions you group with, including their names, realms and classes, your character, dates and locations.

One continuous party stays together in one adventure. Forming a group, entering a dungeon and leaving together updates that entry, with member changes and locations recorded inside it. Outdoor-only groups remain labelled Questing.

In the **Adventures** tab you can:

- Browse parties by date, activity, location, party size and recorded duration.
- Select an adventure to see everyone who joined and the places you visited together.
- Write a private adventure note and find it again through search.
- Pin memorable adventures above other entries, or show only pinned adventures.
- Filter by your character, activity, class, recorded role, favourites, notes, tags, current party or the last 7 or 30 days.
- Sort using column headings and clear filters whenever you want the full picture.

## Good company is worth remembering

The **Companions** tab brings your remembered players together in one searchable list, with class-coloured names, shared-adventure counts, last adventures and last-seen dates.

- Save a multiline personal note of up to 1,000 characters or a private nickname, such as Westfall quest buddy. Adventure notes have the same room.
- Use Helpful, Patient and Great company prompts to start a note, then save it.
- Mark favourite companions and optionally keep them at the top of your list.
- View the first and latest adventures you have kept with a player and browse your shared history.
- Use **Recent companions** to reopen everyone from your latest recorded party, even after it ends. This shortcut clears other filters.
- Spot current party members with a green marker or the In your party filter.
- Search names, realms, locations, your characters, notes, nicknames and tags.
- Open a whisper or invite a selected companion through the game's normal social functions.

The **Character** menu lets you choose a recorded character or All. It filters which adventures and companions appear; companion profiles, counts, notes, nicknames, favourites and tags remain shared across the journal.

The **Role** menu filters Tank, Healer, Damage or Unknown. Adventure filters use the role recorded in each adventure; companion filters and profiles use the latest recorded role across your journal. Roles are historical reminders, not a current specialisation check. If the client does not supply a role, it stays Unknown; Familiar Faces never guesses from class.

## Remember them in your own words

Use the preset **Helpful guide**, **Quest buddy** and **Run again** tags, or create up to **20 custom tags** such as Evening regular, Exploring buddy or Patient tank.

Open **Private tags** on a companion to apply tags. Create and manage custom tags there or through Settings. Renaming a tag updates it across your companions. Removing a custom tag asks for confirmation before removing that label from everyone; it leaves their notes and history intact.

All tags are private, searchable and available through the Tag filter. Preset tags remain available and cannot be renamed or deleted.

## Recognise a familiar face

**Reunion notices** can show a quiet chat message when you group with someone from your history, recalling your previous adventure and saved note. Repeated roster changes and dungeon transitions do not repeat the notice. Recovering the same party after a reload also preserves its notice state.

**Player hover reminders** add a short Familiar Faces section to a remembered player's tooltip, showing recorded adventures together, the last adventure and favourite status. Private notes appear only if you enable that separate preference. Hover reminders skip unavailable or restricted information and operate outside combat.

## Another adventure remembered

Enable **End-of-adventure recaps** in Settings for a small, dismissible card after leaving or disbanding a recorded party.

Favourite a companion directly, open their note, or write a note about the whole adventure while the memory is fresh. The recap has pages for parties whose membership changed over time. It waits until combat and loading screens end; pausing recording or switching to an excluded group does not produce a recap.

Recaps start **off**, so you can choose whether they suit your play style.

## Keep the adventure together

After a UI reload or brief reconnect, Familiar Faces can resume the active adventure when the same character and exact party roster return within **five minutes of the last saved checkpoint**. It preserves the adventure, encounter counts and reunion-notice state, and excludes the unobserved gap from the displayed duration.

A changed roster, another character, an expired checkpoint or an observed party ending starts a new adventure. Recovery uses the last state WoW saved: it cannot reconstruct unsaved history after a crash or reliably detect a disband and identical re-formed party while you were offline. Older duplicate entries are left intact.

## Your journal, your preferences

Enjoy the stylised gold title, teal panels and native game icons in a movable, resizable journal. Size and position are saved between sessions, and the journal scales to fit smaller screens. Long names remain available in hover details.

Open **Settings** or type `/ff settings` to control:

- Recording, reunion notices and favourites-first sorting.
- Player hover reminders and whether they include private notes.
- End-of-adventure recaps.
- The optional minimap button, which you can drag around the minimap.
- Remember my view: save your tab, search, filters and sorting between logins. This starts on.

Settings also provides custom-tag management, backup export and import, a window reset and **Reset view**. Reset view opens Adventures and clears search and filters without changing your journal. Hover reminders start on; private notes in hover reminders and recaps start off. Existing preferences are preserved when updating.

Notes and nickname drafts offer **Save, Discard or Cancel** when you switch entries or close the journal. Incoming party updates keep your draft intact. Tab moves between search and detail fields. Enter opens the first search result, adds a new line in notes, or saves nickname edits. Use **Save note** to save a multiline note.

Scroll the mouse wheel over the journal list to change pages, over shared-history buttons to browse more companions or adventures, or inside a note to scroll its text. Longer filter menus also support the wheel.

## Keep the memories you want

- **Forget adventure** removes one entry and updates recorded encounter counts while retaining companion notes and favourites.
- **Forget companion** removes that player's profile and appearances from your history while keeping other companions. Empty adventures are removed.
- Both actions require confirmation. A forgotten companion can be recorded again in a later party. Forgetting an active adventure suppresses recording for that party, including a matching reload recovery.
- Pause recording at any time, or clear the whole journal with an explicit confirmation command.

## Keep a backup

Choose **Export backup** or type `/ff export` to copy a text archive of your complete saved journal and settings, including adventures, members, locations, notes, nicknames, tags, pins and preferences.

Large exports are split into numbered parts. Copy every part into one text file in order, without inserting separators or extra characters. Exports contain private player names and notes, so keep them private.

Open **Import backup** from Settings or type `/ff import`. Paste your archive, or paste each part in order and click **Add pasted part**. Choose **Preview import** to see adventure, duplicate, new-profile and text-conflict counts before applying anything.

- **Merge** keeps your existing journal, adds imported adventures and skips exact duplicate records even if their IDs differ. Existing non-empty notes and nicknames win conflicts; blank fields can be filled, and favourites, pins and tags are combined. Different snapshots of a continuing adventure may remain separate.
- **Replace journal** replaces your current history, profiles, notes, favourites, pins and custom tags. It requires a separate confirmation. Export first if you want to keep a copy.
- Both modes keep your current settings. Pasted text is parsed as data and is never executed as Lua code.
- Import while solo and outside combat. If your journal changes after previewing, preview it again. Missing parts or invalid backups are rejected without changing your journal.
- Imports accept Familiar Faces text exports up to 2 MB, 10,000 adventures and 25,000 profiles; the merged custom-tag total cannot exceed 20. Oversized or unsupported archives need to be managed through SavedVariables instead. There is no automatic account synchronisation.

## Commands

| Command | Action |
| --- | --- |
| `/ff` or `/familiarfaces` | Open or close the journal. |
| `/ff settings` | Open your journal preferences. |
| `/ff pause` | Pause recording. |
| `/ff resume` | Resume recording. |
| `/ff notices` | Toggle reunion chat notices. |
| `/ff minimap` | Show or hide the minimap button. |
| `/ff reset window` | Reset the journal's position and size. |
| `/ff reset view` | Open Adventures and clear search and filters. |
| `/ff export` | Open the copyable journal backup. |
| `/ff import` | Preview and import a journal text backup. |
| `/ff clear` | Show instructions for clearing saved data. |
| `/ff clear confirm` | Erase all journal history, profiles and custom tags, retaining display and recording preferences. |

## Installation and compatibility

Download the **WoW Forever** package and place its **FamiliarFaces** folder inside `_forever_/Interface/AddOns`. Enable it on the character-selection AddOns screen, then type `/ff` in game. When updating, replace the addon files and keep your SavedVariables to retain your journal.

This package targets **WoW Forever 1.60.1**, interface **16001**. No other addons are required. History begins when installed; earlier parties cannot be recovered. Raid, battleground and arena groups are excluded. Outdoor parties are labelled Questing, and recorded parties and durations do not verify quest or dungeon completion. First and latest meeting summaries reflect the history you have kept.

## Your memories stay yours

Your journal is stored locally in your WoW account's SavedVariables. Familiar Faces does not collect chat messages, send telemetry or automatically share notes, nicknames or tags with other players. Notes and tags are personal reminders, visible to you.

**Created by SqueezyLemons**

[More addons](https://www.curseforge.com/members/squeezylemons/projects) · [Source code](https://github.com/fullstackprocrastinator/party-memory) · [Report an issue](https://github.com/fullstackprocrastinator/party-memory/issues)
