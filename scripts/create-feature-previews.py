"""Create honest CurseForge feature previews from the actual Lua UI layout."""
from pathlib import Path
import html

ROOT = Path(__file__).resolve().parents[1]
generator = ROOT / 'scripts/preview-familiarfaces-ui.py'
code = generator.read_text(encoding='utf-8')
code = code.replace("local original=CreateFrame", "previewMessages={}; DEFAULT_CHAT_FRAME.AddMessage=function(_,message) previewMessages[#previewMessages+1]=message end\nlocal original=CreateFrame")
code = code.replace("if state=='companions':", "if state in ('companions','forgetting','drafts','party','tags'):")
code = code.replace(" frames={", " if state=='forgetting': lua.execute(\"clickText('Forget companion')\")\n if state=='drafts': lua.execute(\"clickText('Helpful'); clickText('Close')\")\n if state=='reunion': lua.execute(\"previewMessages={}; clock=clock+3600; FamiliarFaces.Capture(); for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end\")\n frames={")
code = code.replace(" (DEST/(state+'.html')).write_text", " if state=='reunion': page+='<aside style=\"padding:18px 30px;background:#071820;color:#f5deb0\"><b>Example reunion chat messages</b><br>'+ '<br>'.join(text(m) for m in lua.globals().previewMessages.values())+'</aside>'\n (DEST/(state+'.html')).write_text")
code = code.replace(" frames={", " if state=='party': lua.execute(\"clickText('In your party: off'); clickText('When: Any time')\")\n frames={")
code = code.replace(" frames={", " if state=='tags': lua.execute(\"clickText('Private tags')\")\n if state=='backup': lua.execute(\"clickText('Export backup')\")\n frames={")
code = code.replace("('empty','adventures','companions')", "('empty','adventures','companions','forgetting','reunion','drafts','party','tags','backup')")
extra = '''
   RAID_CLASS_COLORS.MAGE={r=0.25,g=0.78,b=0.92}
   RAID_CLASS_COLORS.ROGUE={r=1,g=0.96,b=0.41}
   RAID_CLASS_COLORS.DRUID={r=1,g=0.49,b=0.04}
   clock=1790953200; zone='Westfall'; instanceType='none'
   roster={{name='Alice',realm='HomeRealm',class='PRIEST',role='HEALER'},
     {name='Rowan',realm='HomeRealm',class='DRUID'}, {name='Finn',realm='HomeRealm',class='ROGUE'}}
   FamiliarFaces.Capture(); clock=clock+2100; FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
   clock=1791039600; zone='Shadowfang Keep'; instanceType='party'
   roster={{name='Bram',realm='HomeRealm',class='WARRIOR',role='TANK'},
     {name='Mira',realm='HomeRealm',class='MAGE'}}
   FamiliarFaces.Capture(); clock=clock+2700; FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
   clock=1791111600; zone='Redridge Mountains'; instanceType='none'
   roster={{name='Alice',realm='HomeRealm',class='PRIEST'}, {name='Mira',realm='HomeRealm',class='MAGE'}}
   FamiliarFaces.Capture(); clock=clock+1200; FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
   zone='Elwynn Forest'; instanceType='none'
'''
code = code.replace("   roster={{name='Alice',realm='HomeRealm',class='PRIEST',role='HEALER'},", extra + "   roster={{name='Alice',realm='HomeRealm',class='PRIEST',role='HEALER'},", 1)
code = code.replace("   FamiliarFaces.db.people['Alice-HomeRealm'].favourite=true", """   FamiliarFaces.db.people['Alice-HomeRealm'].favourite=true
   FamiliarFaces.db.people['Bram-HomeRealm'].note='Explained every boss. Would group again.'
   FamiliarFaces.db.people['Alice-HomeRealm'].nickname='Westfall quest buddy'
   FamiliarFaces.db.people['Alice-HomeRealm'].tags={['Helpful guide']=true,['Run again']=true}
   FamiliarFaces.db.sessions[1].note='Our first Deadmines clear. Patient group, lots of laughs.'
   FamiliarFaces.db.sessions[1].pinned=true
   FamiliarFaces.db.people['Bram-HomeRealm'].favourite=true
   FamiliarFaces.db.people['Mira-HomeRealm'].note='Always brings snacks.'""")
exec(compile(code, str(generator), 'exec'), {'__file__': str(generator), '__name__': '__main__'})

dest = ROOT / 'assets/curseforge'
dest.mkdir(parents=True, exist_ok=True)
cards = {
 'adventures': ('Every party has a story.', 'Browse past adventures, remember your party and follow the places you explored together.'),
 'companions': ('Familiar names. New adventures.', 'Find familiar companions, save a personal note, mark favourites and whisper or invite them again.'),
 'forgetting': ('Keep the memories you want.', 'Forget an individual companion or adventure with a clear confirmation before anything is removed.'),
 'reunion': ('A familiar face joins the party.', 'Optional reunion messages recall your previous adventure and note, once per companion per party.'),
 'drafts': ('A good memory should not get lost.', 'Save, discard or cancel when leaving an unsaved note or nickname. Roster updates keep your draft intact.'),
 'party': ('Your current company, at a glance.', 'Focus on the people in your party, filter recent adventures and keep a searchable private nickname.'),
 'tags': ('Remember what made them memorable.', 'Keep private companion tags, filter by them and revisit how you first met.'),
 'backup': ('Keep a copy of your adventures.', 'Copy your complete saved journal and settings into a private text backup.'),
}
for state, (title, caption) in cards.items():
 page = (ROOT / f'docs/previews/familiar-faces/{state}.html').read_text(encoding='utf-8')
 start = page.index('<p style="margin:20px">')
 end = page.index('</p>', start) + 4
 heading = '<header style="padding:26px 30px 8px"><div style="color:#e6b967;font-size:12px;letter-spacing:2px">FAMILIAR FACES · FEATURE PREVIEW</div><h1 style="margin:10px 0;color:#f5deb0;font:30px Georgia">' + html.escape(title) + '</h1><div style="font-size:15px;color:#d4e2df">' + html.escape(caption) + '</div></header>'
 page = page[:start] + heading + page[end:]
 page += '<footer style="padding:0 30px 24px;color:#bed0d0;font-size:12px">Sample data rendered from the addon Lua layout. Native game icons and input skins are placeholders. Created by SqueezyLemons.</footer>'
 page = page.replace('src="Wordmark.png"', 'src="../../docs/previews/familiar-faces/Wordmark.png"')
 (dest / f'familiar-faces-{state}.html').write_text(page, encoding='utf-8')
print(dest)
