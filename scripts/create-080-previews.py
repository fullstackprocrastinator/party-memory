"""0.8.0 gallery: actual Lua UI with fictional, reproducible journal data."""
from pathlib import Path
import importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/preview-familiarfaces-ui.py')
preview=importlib.util.module_from_spec(spec); spec.loader.exec_module(preview)
preview.DEST=ROOT/'assets/curseforge/0.8.0'
preview.DEST.mkdir(parents=True,exist_ok=True)
Image.open(ROOT/'FamiliarFaces/Textures/Wordmark.tga').save(preview.DEST/'Wordmark.png')
SETUP=r'''
 local PM=FamiliarFaces
 RAID_CLASS_COLORS.MAGE={r=0.25,g=0.78,b=0.92}; RAID_CLASS_COLORS.DRUID={r=1,g=0.49,b=0.04}
 PM.CreateTag('Evening regular'); PM.ToggleTag(PM.db.people['Alice-HomeRealm'],'Evening regular')
 PM.db.people['Alice-HomeRealm'].nickname='Westfall quest buddy'
 PM.db.people['Alice-HomeRealm'].note='Patient healer. Explains each boss.\nWaited while we found the entrance.\nBring along for our next evening run!'
 PM.db.people['Bram-HomeRealm'].note='Our trusty tank. Great company.'
 PM.db.sessions[1].note='Our first Deadmines trip. Lots of laughs.'; PM.db.sessions[1].pinned=true
 local trips={
  {zone='Westfall',kind='Questing',owner='Willow-HomeRealm'},
  {zone='Shadowfang Keep',kind='Dungeon',owner='Briar-HomeRealm'},
  {zone='Redridge Mountains',kind='Questing',owner='Willow-HomeRealm'},
  {zone='Deadmines',kind='Dungeon',owner='Willow-HomeRealm'},
 }
 for i,t in ipairs(trips) do
  local at=1793955600+i*86400
  local members={{name='Alice-HomeRealm',class='PRIEST',role='HEALER'},
    {name='Mira-HomeRealm',class='MAGE',role='DAMAGER'}, {name='Rowan-HomeRealm',class='DRUID',role='TANK'}}
  PM.Record(t.owner,members,t,at); PM.Record(t.owner,members,t,at+2400); PM.EndSession(at+2400)
 end
 PM.RebuildPeople(); PM.currentOwner='Willow-HomeRealm'; PM.currentParty={}; roster={}; clock=1794303000
'''
ALICE="clickText('Companions'); for _,b in ipairs(buttons) do if b.entry and b.entry.name=='Alice-HomeRealm' then b.scripts.OnClick(b); break end end"
cards={
 '01-journal':('Every party has a story.','One adventure per continuous party, with private notes, remembered roles and a route through your time together.',
    "for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end"),
 '02-notes':('A little more room for the memories.','Multiline notes, private nicknames and a shared history. Remember the person behind the character.',ALICE),
 '03-role-filter':('Find the company you remember.','Choose a recorded role from a menu. Unknown stays unknown; classes are never used to guess a role.',ALICE+"; clickText('Role: All')"),
 '04-settings':('Right where you left it.','Remember your tab, filters and sort order between logins, or reset the view with one click.',"clickText('Settings')"),
 '05-import':('Bring your memories along.','Preview a backup before merging. Duplicate adventures are skipped and your existing notes win conflicts.',r'''
    local PM=FamiliarFaces; local backup=PM.Export()
    PM.ForgetAdventure(PM.db.sessions[1]); PM.ForgetAdventure(PM.db.sessions[1])
    PM.db.people['Alice-HomeRealm'].note='My current journal note.'
    PM.ShowImport(); FamiliarFacesImportText:SetText(backup); clickText('Preview import')
 '''),
}
for state,(title,caption,actions) in cards.items():
 preview.render(state,setup=SETUP,actions=actions,title=title,caption=caption)
print(preview.DEST)
