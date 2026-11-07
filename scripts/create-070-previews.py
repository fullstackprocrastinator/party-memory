"""Release images driven by the actual addon Lua and synthetic player data."""
from pathlib import Path
import importlib.util
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/preview-familiarfaces-ui.py')
preview=importlib.util.module_from_spec(spec); spec.loader.exec_module(preview)
preview.DEST=ROOT/'assets/curseforge/0.7.0'
preview.DEST.mkdir(parents=True,exist_ok=True)
Image.open(ROOT/'FamiliarFaces/Textures/Wordmark.tga').save(preview.DEST/'Wordmark.png')
SETUP=r'''
 RAID_CLASS_COLORS.MAGE={r=0.25,g=0.78,b=0.92}
 RAID_CLASS_COLORS.DRUID={r=1,g=0.49,b=0.04}
 local PM=FamiliarFaces
 PM.db.people['Alice-HomeRealm'].nickname='Westfall quest buddy'
 PM.db.people['Alice-HomeRealm'].note='Patient healer. Always happy to explain a boss.'
 PM.db.people['Bram-HomeRealm'].note='Our trusty tank. Great company.'
 PM.CreateTag('Evening regular'); PM.CreateTag('Exploring buddy')
 PM.ToggleTag(PM.db.people['Alice-HomeRealm'],'Evening regular')
 PM.ToggleTag(PM.db.people['Alice-HomeRealm'],'Helpful guide')
 PM.ToggleTag(PM.db.people['Alice-HomeRealm'],'Run again')
 PM.db.sessions[1].note='Our first Deadmines trip. Lots of laughs.'; PM.db.sessions[1].pinned=true
 -- All characters, dates and parties below are fictional demonstration data.
 PM.db.sessions[1].started=1793898000; PM.db.sessions[1].lastSeen=1793900400; PM.db.sessions[1].ended=1793900400
 PM.db.sessions[1].owner='Willow-HomeRealm'
 for _,m in ipairs(PM.db.sessions[1].members) do m.joined=1793898000; m.lastSeen=1793900400 end
 for i,l in ipairs(PM.db.sessions[1].locations) do l.started=1793898000+(i-1)*600; l.lastSeen=i==1 and 1793898600 or 1793900400 end
 local trips={
  {at=1793984400,owner='Willow-HomeRealm',zone='Westfall',kind='Questing',duration=1800},
  {at=1794070800,owner='Briar-HomeRealm',zone='Shadowfang Keep',kind='Dungeon',duration=3000},
  {at=1794157200,owner='Willow-HomeRealm',zone='Redridge Mountains',kind='Questing',duration=2100},
 }
 for _,t in ipairs(trips) do
  local members={{name='Alice-HomeRealm',class='PRIEST'},{name='Mira-HomeRealm',class='MAGE'},{name='Rowan-HomeRealm',class='DRUID'}}
  PM.Record(t.owner,members,{zone=t.zone,kind=t.kind},t.at)
  PM.Record(t.owner,members,{zone=t.zone,kind=t.kind},t.at+t.duration); PM.EndSession(t.at+t.duration)
 end
 for _,s in ipairs(PM.db.sessions) do
  s.started=s.started-86400; s.lastSeen=s.lastSeen-86400; s.ended=s.ended-86400
  for _,m in ipairs(s.members) do m.joined=m.joined-86400; m.lastSeen=m.lastSeen-86400 end
  for _,l in ipairs(s.locations or {}) do l.started=l.started-86400; l.lastSeen=l.lastSeen-86400 end
 end
 PM.RebuildPeople(); PM.currentOwner='Willow-HomeRealm'; PM.currentParty={}; clock=1794073200
'''
SELECT_ALICE="clickText('Companions'); for _,b in ipairs(buttons) do if b.entry and b.entry.name=='Alice-HomeRealm' then b.scripts.OnClick(b); break end end"
cards={
 '01-adventures':('Every party has a story.','A searchable journal of your companions, favourite adventures and the places you explored.',
   "for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end"),
 '02-companions':('Good company is worth remembering.','Private notes, nicknames, favourite companions and a history of how you met.',SELECT_ALICE),
 '03-custom-tags':('Remember them in your own words.','Create private tags, apply them to companions and find the right company next time.',SELECT_ALICE+"; clickText('Private tags')"),
 '04-settings':('Make yourself at home.','All your preferences together, including optional hover reminders and adventure recaps.',"clickText('Settings')"),
 '05-recap':('Another adventure remembered.','An optional recap makes it easy to favourite companions and write a note after your party ends.',
   "FamiliarFaces.db.recaps=true; FamiliarFaces.QueueRecap(FamiliarFaces.db.sessions[1]); FamiliarFaces.MaybeShowRecap()"),
 '06-characters':('Every character. Their own adventures.','Filter your journal by character while keeping companion notes and favourites shared.',
   "clickText('Character: All'); for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end"),
 '07-hover-reminders':("Haven't we adventured together?",'Recognise a remembered player on hover. Private notes are optional and start switched off.',SELECT_ALICE+r'''
   GameTooltip=CreateFrame('Frame',nil,UIParent); GameTooltip:SetSize(430,205); GameTooltip:SetPoint('TOPLEFT',260,-420); GameTooltip:SetFrameStrata('FULLSCREEN_DIALOG')
   local bg=GameTooltip:CreateTexture(nil,'BACKGROUND'); bg:SetAllPoints(); bg:SetTexture('Interface\\Buttons\\WHITE8X8'); bg:SetVertexColor(0.02,0.04,0.06,1)
   local line=0
   GameTooltip.AddLine=function(self,text,r,g,b)
     local f=self:CreateFontString(nil,'OVERLAY','GameFontHighlightSmall'); f:SetPoint('TOPLEFT',18,-18-line*24); f:SetWidth(394); f:SetText(text)
     f:SetTextColor(r or 1,g or 1,b or 1); line=line+1
   end
   GameTooltip.GetUnit=function() return 'Alice','party1' end
   roster={{name='Alice',realm='HomeRealm',class='PRIEST'}}
   GameTooltip:AddLine('Alice-HomeRealm',1,1,1)
   FamiliarFaces.AddUnitTooltip(GameTooltip)
 '''),
}
for state,(title,caption,actions) in cards.items():
 preview.render(state,setup=SETUP,actions=actions,title=title,caption=caption)
print(preview.DEST)
