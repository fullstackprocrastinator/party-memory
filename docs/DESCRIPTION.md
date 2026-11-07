# Familiar Faces

**Remember the people you adventure with.**

The healer who saved the run. The tank who explained the boss. The questing companion who stayed for one more adventure.

Good company deserves more than a name you almost remember. **Familiar Faces** keeps a personal journal of your dungeon and questing parties, helping you recognise familiar players and find them again.

## New in 0.7.0: Good Company

- **We've met before:** optional player hover reminders show how many recorded adventures you have shared, your last meeting and favourite status. Include your private note if you choose.
- **Another adventure remembered:** an optional recap after your party ends lets you favourite companions or jump straight into writing a companion or adventure note.
- **Pick up where you left off:** recover a recent adventure after a UI reload or brief reconnect when your character and full party roster still match.
- **Your words, your memories:** create your own companion tags, alongside Helpful guide, Quest buddy and Run again.
- **A journal for every character:** filter adventures and companions by the character you played.
- **Make yourself at home:** a dedicated Settings panel puts your preferences in one place.

## Every party has a story

Familiar Faces automatically records the companions you group with, including their names, realms and classes, your character, dates and locations.

One continuous party stays together in one adventure. Forming a group, entering a dungeon and leaving together updates that entry, with member changes and locations recorded inside it. Outdoor-only groups remain labelled Questing.

In the **Adventures** tab you can:

- Browse parties by date, activity, location, party size and recorded duration.
- Select an adventure to see everyone who joined and the places you visited together.
- Write a private adventure note and find it again through search.
- Pin memorable adventures above other entries, or show only pinned adventures.
- Filter by your character, activity, class, favourites, notes, tags, current party or the last 7 or 30 days.
- Sort using column headings and clear filters whenever you want the full picture.

## Good company is worth remembering

The **Companions** tab brings your remembered players together in one searchable list, with class-coloured names, shared-adventure counts, last adventures and last-seen dates.

- Save a personal note or a private nickname, such as Westfall quest buddy.
- Use Helpful, Patient and Great company prompts to start a note, then save it.
- Mark favourite companions and optionally keep them at the top of your list.
- View the first and latest adventures you have kept with a player and browse your shared history.
- Use **Recent companions** to reopen everyone from your latest recorded party, even after it ends. This shortcut clears other filters.
- Spot current party members with a green marker or the In your party filter.
- Search names, realms, locations, your characters, notes, nicknames and tags.
- Open a whisper or invite a selected companion through the game's normal social functions.

The **Character** button cycles through your recorded characters and All. It filters which adventures and companions appear; companion profiles, counts, notes, nicknames, favourites and tags remain shared across the journal.

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

Settings also provides custom-tag management, a backup shortcut and a window reset. Hover reminders start on; private notes in hover reminders and recaps start off. Existing preferences are preserved when updating.

Notes and nickname drafts offer **Save, Discard or Cancel** when you switch entries or close the journal. Incoming party updates keep your draft intact. Tab moves between search and detail fields; Enter opens the first search result or saves your detail edits.

## Keep the memories you want

- **Forget adventure** removes one entry and updates recorded encounter counts while retaining companion notes and favourites.
- **Forget companion** removes that player's profile and appearances from your history while keeping other companions. Empty adventures are removed.
- Both actions require confirmation. A forgotten companion can be recorded again in a later party. Forgetting an active adventure suppresses recording for that party, including a matching reload recovery.
- Pause recording at any time, or clear the whole journal with an explicit confirmation command.

## Keep a backup

Choose **Export backup** or type `/ff export` to copy a text archive of your complete saved journal and settings, including adventures, members, locations, notes, nicknames, tags, pins and preferences.

Large exports are split into numbered parts. Copy every part into one text file in order, without inserting separators or extra characters. Exports contain private player names and notes, so keep them private. This is a saved-data archive for safekeeping; automatic import is not included.

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
| `/ff export` | Open the copyable journal backup. |
| `/ff clear` | Show instructions for clearing saved data. |
| `/ff clear confirm` | Erase all journal history, profiles and custom tags, retaining display and recording preferences. |

## Installation and compatibility

Download the **WoW Forever** package and place its **FamiliarFaces** folder inside `_forever_/Interface/AddOns`. Enable it on the character-selection AddOns screen, then type `/ff` in game. When updating, replace the addon files and keep your SavedVariables to retain your journal.

This package targets **WoW Forever 1.60.1**, interface **16001**. No other addons are required. History begins when installed; earlier parties cannot be recovered. Raid, battleground and arena groups are excluded. Outdoor parties are labelled Questing, and recorded parties and durations do not verify quest or dungeon completion. First and latest meeting summaries reflect the history you have kept.

## Your memories stay yours

Your journal is stored locally in your WoW account's SavedVariables. Familiar Faces does not collect chat messages, send telemetry or automatically share notes, nicknames or tags with other players. Notes and tags are personal reminders, visible to you.

**Created by SqueezyLemons**

[More addons](https://www.curseforge.com/members/squeezylemons/projects) · [Source code](https://github.com/fullstackprocrastinator/party-memory) · [Report an issue](https://github.com/fullstackprocrastinator/party-memory/issues)
