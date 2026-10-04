# CurseForge release checklist

1. Confirm the intended game client. Test the addon in that client using TESTING.md, and set its exact interface number in the TOC. Keep private-server-only packages separately labelled; do not claim support for official clients you have not tested.
2. Run `pwsh -File scripts/package.ps1 -Client Retail` for Retail, or `-Client 335` for legacy 3.3.5. The default command produces a WoW Forever package (interface 16001); do not label it as an official Retail release. Inspect the generated ZIP: its root must contain the FamiliarFaces folder, with the TOC and Lua files inside.
3. Create a World of Warcraft project at https://authors.curseforge.com/ with the name **Familiar Faces**. Suggested category: Chat & Communication or Miscellaneous (use the current available categories). Select MIT as the license and use the GitHub repository for source and issues.
4. Add an original project avatar and screenshots from the actual game. Use the description below and clearly identify tested client versions.
5. Upload the correct ZIP, select the matching official game version and release type. Start with Alpha while in-game testing is incomplete. A Release file is required for CurseForge App distribution after approval. Submit for moderation.

Official guidance: https://support.curseforge.com/support/solutions/articles/9000197241-creating-and-submitting-a-project

## Suggested project description

Ever finish a great dungeon run and forget the name of the person who made it fun? Familiar Faces keeps a personal journal of the people you group with.

It records dungeon and outdoor parties, including names, realms, dates and locations. Browse your previous groups, search for a player, add a personal note and favourite someone you'd like to play with again. Select a player to whisper or invite them through the game's normal social functions.

Open Familiar Faces with /ff or /familiarfaces. History starts when the addon is installed. Outdoor parties are labelled Questing. Raid and battleground groups are excluded. Everything is saved locally in your WoW account; no chat messages or telemetry are collected. Pause recording with /ff pause and resume with /ff resume.

Compatibility: [replace with client versions actually tested before submission].

## Release notes for 0.3.0 Alpha

Redesigned the journal with Adventures and Companions tabs, sortable tables, activity/class/favourites/notes filters, and a linked detail panel. Browse every shared adventure from a player's profile, read notes in row tooltips, and resize the window. The charcoal and gold interface adds alternating rows and clear selection highlights. Existing FamiliarFaces history, notes and favourites are preserved. Open with /ff or /familiarfaces.

## Release notes for 0.3.1

- A warmer journal design with a gold serif wordmark, teal panels, gold borders and native game icons.
- Clearer selected rows, highlighted tabs and a welcoming empty journal.
- Added Created by SqueezyLemons. Click the credit to copy the creator's CurseForge projects link.
- Existing history, notes and favourites are preserved. Commands remain /ff and /familiarfaces.
