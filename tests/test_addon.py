"""Execute the addon under Lua 5.1 with deterministic WoW API mocks."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime

MOCKS = r'''
clock = 1000
time = function() return clock end
date = function(fmt, value) return os.date(fmt, value) end
UIParent = {}; UISpecialFrames = {}; SlashCmdList = {}
RAID_CLASS_COLORS = { PRIEST={r=1,g=1,b=1}, WARRIOR={r=0.78,g=0.61,b=0.43} }
DEFAULT_CHAT_FRAME = {AddMessage = function() end}
frames = {}; buttons = {}; combat = false; raid = false
roster = { {name='Alice',realm='Other Realm',class='PRIEST',role='HEALER'} }
zone = 'Elwynn Forest'; instanceType = 'none'
GetRealmName = function() return 'Home Realm' end
UnitName = function(unit)
 if unit == 'player' then return 'Me', 'Home Realm' end
 local m = roster[tonumber(string.match(unit, '%d+'))]
 if m then return m.name, m.realm end
end
UnitClass = function(unit) local m=roster[tonumber(string.match(unit,'%d+'))]; return 'Class',m.class end
UnitGroupRolesAssigned = function(unit) return roster[tonumber(string.match(unit,'%d+'))].role end
GetNumSubgroupMembers = function() return #roster end
IsInRaid = function() return raid end
InCombatLockdown = function() return combat end
GetInstanceInfo = function() return zone,instanceType,1,'Normal' end
GetZoneText = function() return zone end
ChatFrame_SendTell = function(name) whispered=name end
C_PartyInfo = {InviteUnit=function(name) invited=name end}
local noop = function() end
function CreateFrame(kind,name,parent,template)
 local f = {scripts={},visible=true,text='',kind=kind,width=1120,height=760}
 local methods = {
  SetScript=function(self,event,fn) self.scripts[event]=fn end,
  RegisterEvent=noop, SetSize=function(self,w,h) self.width=w; self.height=h end, SetPoint=noop,
  SetWidth=function(self,w) self.width=w end, GetWidth=function(self) return self.width end,
  GetHeight=function(self) return self.height end, ClearAllPoints=noop,
  SetResizable=noop, SetResizeBounds=noop, StartSizing=noop,
  SetHeight=noop, SetJustifyH=noop, SetJustifyV=noop, SetFontObject=noop,
  SetFrameStrata=noop, SetMovable=noop, EnableMouse=noop, RegisterForDrag=noop,
  StartMoving=noop, StopMovingOrSizing=noop, SetClampedToScreen=noop,
  SetHighlightTexture=noop, SetAutoFocus=noop, SetMaxLetters=noop,
  ClearFocus=noop, SetAllPoints=noop, SetTexture=noop, SetVertexColor=noop,
  SetTextColor=noop,
  SetFocus=noop, HighlightText=noop,
  SetText=function(self,t) self.text=t; if self.scripts.OnTextChanged then self.scripts.OnTextChanged(self) end end,
  GetText=function(self) return self.text end,
  IsShown=function(self) return self.visible end,
  Show=function(self) self.visible=true; if self.scripts.OnShow then self.scripts.OnShow(self) end end,
  Hide=function(self) self.visible=false end,
  CreateTexture=function() return CreateFrame('Texture') end,
  CreateFontString=function() return CreateFrame('FontString') end,
 }
 setmetatable(f,{__index=methods}); table.insert(frames,f)
 if kind=='Button' then table.insert(buttons,f) end
 if name then _G[name]=f end
 return f
end
function clickText(text)
 for _,b in ipairs(buttons) do if b.caption==text or b.text==text then b.scripts.OnClick(b); return end end
 error('Missing button: '..text)
end
'''

class AddonTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(MOCKS)
        for name in ('Store.lua', 'Core.lua', 'UI.lua'):
            self.lua.execute((ROOT / 'FamiliarFaces' / name).read_text(encoding='utf-8'))
        self.lua.execute("frames[1].scripts.OnEvent(frames[1], 'ADDON_LOADED', 'FamiliarFaces')")

    def test_roster_sessions_and_history(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==1)
          clock=1015; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==1)
          assert(FamiliarFaces.db.sessions[1].lastSeen==1015)
          roster[2]={name='Bob',realm='Home Realm',class='WARRIOR',role='TANK'}
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==1)
          assert(#FamiliarFaces.db.sessions[1].members==2)
          roster={}; FamiliarFaces.Capture()
          roster={{name='Alice',realm='Other Realm',class='PRIEST',role='HEALER'}}
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==2)
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].encounters==2)
        ''')

    def test_companion_filters_sorting_and_shared_history(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
          roster={{name='Bob',realm='Home Realm',class='WARRIOR'}}
          zone='Deadmines'; instanceType='party'; clock=2000; FamiliarFaces.Capture()
          local alice=FamiliarFaces.db.people['Alice-OtherRealm']; alice.note='Helpful healer'; alice.favourite=true
          local list=FamiliarFaces.Query('Companions',{sort='name',ascending=true})
          assert(#list==2 and list[1]==alice)
          assert(#FamiliarFaces.Query('Companions',{kind='Dungeon',notes=true})==0)
          assert(#FamiliarFaces.Query('Companions',{class='PRIEST',favourites=true,notes=true})==1)
          assert(#FamiliarFaces.Query('Companions',{query='Deadmines'})==1)
          assert(#FamiliarFaces.Query('Adventures',{query='Helpful',class='WARRIOR'})==0)
          assert(FamiliarFaces.Query('Adventures',{sort='started'})[1].zone=='Deadmines')
          assert(FamiliarFaces.Query('Adventures',{sort='started',ascending=true})[1].zone=='Elwynn Forest')
          SlashCmdList.FAMILIARFACES(''); clickText('Companions')
          for _,b in ipairs(buttons) do if b.entry==alice then b.scripts.OnClick(b); break end end
          clickText('Whisper'); assert(whispered=='Alice-OtherRealm')
          clickText('01 Jan  Elwynn Forest')
          clickText('|cffffffffAlice-OtherRealm|r')
          clickText('Unfavourite'); assert(not alice.favourite)
          clickText('Clear filters')
          FamiliarFacesWindow:SetSize(1300,900); FamiliarFacesWindow.scripts.OnSizeChanged()
          for _,b in ipairs(buttons) do if b.entry then assert(b:GetWidth()==900) end end
          SlashCmdList.FAMILIARFACES('clear confirm')
          clickText('Save note'); assert(#FamiliarFaces.db.sessions==0)
        ''')

    def test_filters_notes_realms_and_reload(self):
        self.lua.execute('''
          FamiliarFaces.Capture()
          zone='Deadmines'; instanceType='party'; FamiliarFaces.Capture()
          local p=FamiliarFaces.db.people['Alice-OtherRealm']; p.note='Helpful healer'; p.favourite=true
          assert(#FamiliarFaces.Search('HELPFUL', 'Dungeon', true)==1)
          assert(#FamiliarFaces.Search('Me-HomeRealm')==1)
          assert(#FamiliarFaces.Search('%')==0)
          FamiliarFaces.Init(FamiliarFacesDB); FamiliarFaces.active=nil
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='Helpful healer')
          roster[1].realm='Third Realm'; FamiliarFaces.Capture()
          assert(FamiliarFaces.db.people['Alice-ThirdRealm'])
        ''')

    def test_pause_unknown_combat_and_exclusions(self):
        self.lua.execute('''
          combat=true; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          combat=false; roster[1].name='Unknown'; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          roster[1].name='Alice'; raid=true; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          raid=false; instanceType='pvp'; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          instanceType='none'; SlashCmdList.FAMILIARFACES('pause'); assert(#FamiliarFaces.db.sessions==0)
          SlashCmdList.FAMILIARFACES('resume'); assert(#FamiliarFaces.db.sessions==1)
          SlashCmdList.FAMILIARFACES('clear'); assert(#FamiliarFaces.db.sessions==1)
          SlashCmdList.FAMILIARFACES('clear confirm'); assert(#FamiliarFaces.db.sessions==0)
        ''')

    def test_legacy_api_and_event_fallbacks(self):
        self.lua.execute('''
          GetNumPartyMembers=GetNumSubgroupMembers; GetNumSubgroupMembers=nil
          GetNumRaidMembers=function() return 0 end; IsInRaid=nil
          UnitGroupRolesAssigned=nil; C_PartyInfo=nil; InviteUnit=function(n) invited=n end
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==1)
          assert(FamiliarFaces.db.sessions[1].members[1].role=='NONE')
          SlashCmdList.FAMILIARFACES(''); assert(FamiliarFacesWindow:IsShown())
        ''')

    def test_ui_open_select_notes_actions_and_pagination(self):
        self.lua.execute('''
          for i=1,12 do zone='Zone '..i; FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock) end
          SlashCmdList.FAMILIARFACES(''); assert(FamiliarFacesWindow:IsShown())
          clickText('Next'); clickText('Previous')
        ''')

    def test_dungeon_round_trip_and_outdoor_party(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local s=FamiliarFaces.active
          zone='Westfall'; FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==1 and s.kind=='Questing')
          zone='Deadmines'; instanceType='party'; FamiliarFaces.Capture()
          zone='Westfall'; instanceType='none'; FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==1 and s.kind=='Dungeon' and s.zone=='Deadmines')
          assert(#s.locations==4 and #FamiliarFaces.Search('Elwynn')==1)
          assert(#FamiliarFaces.Search('', 'Questing')==0)
          assert(#FamiliarFaces.Search('', 'Dungeon')==1)
          combat=true; roster={}; FamiliarFaces.Capture(); assert(FamiliarFaces.active==nil)
          combat=false; roster={{name='Alice',realm='Other Realm',class='PRIEST'}}
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==2)
          assert(FamiliarFaces.active.kind=='Questing')
        ''')

    def test_member_replacements_and_history_pagination(self):
        self.lua.execute('''
          FamiliarFaces.Capture()
          for i=1,6 do roster={{name='Player'..i,realm='Home Realm',class='WARRIOR'}}; FamiliarFaces.Capture() end
          assert(#FamiliarFaces.db.sessions==1 and #FamiliarFaces.active.members==7)
          assert(FamiliarFaces.active.members[1].left)
          roster={{name='Alice',realm='Other Realm',class='PRIEST'}}; FamiliarFaces.Capture()
          assert(FamiliarFaces.active.members[1].left==nil)
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].encounters==1)
          SlashCmdList.FAMILIARFACES('')
          for _,b in ipairs(buttons) do if type(b.text)=='table' then b.scripts.OnClick(b); break end end
          clickText('More players'); clickText('|cffc79c6ePlayer6-HomeRealm|r (left)')
          clickText('Whisper'); assert(whispered=='Player6-HomeRealm')
        ''')

    def test_existing_saved_rosters_remain_browsable(self):
        self.lua.execute('''
          FamiliarFacesDB=FamiliarFaces.Init({version=1,sessions={{id=1,owner='Old',kind='Questing',zone='OldZone',
            started=100,lastSeen=110,members={{name='OldPlayer'}}}},nextID=2})
          assert(#FamiliarFaces.Search('OldPlayer')==1)
          SlashCmdList.FAMILIARFACES('')
          for _,b in ipairs(buttons) do if type(b.text)=='table' then b.scripts.OnClick(b); break end end
          clickText('OldPlayer')
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==2)
        ''')
        # Rows carry a FontString in .text rather than a button label.
        self.lua.execute('''
          for _,b in ipairs(buttons) do if type(b.text)=='table' then b.scripts.OnClick(b); break end end
          clickText('|cffffffffAlice-OtherRealm|r'); clickText('Favourite')
          for _,f in ipairs(frames) do if f.kind=='EditBox' then f:SetText('A great healer') end end
          clickText('Save note'); assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='A great healer')
          clickText('Whisper'); assert(whispered=='Alice-OtherRealm')
          combat=true; clickText('Invite'); assert(invited==nil)
          combat=false; clickText('Invite'); assert(invited=='Alice-OtherRealm')
          clickText('Close'); assert(not FamiliarFacesWindow:IsShown())
          SlashCmdList.FAMILIARFACES(''); assert(FamiliarFacesWindow:IsShown())
        ''')

    def test_creator_credit_link(self):
        self.lua.execute('''
          SlashCmdList.FAMILIARFACES(''); clickText('Created by SqueezyLemons')
          local link
          for _,f in ipairs(frames) do
            if f.kind=='EditBox' and f.text=='https://www.curseforge.com/members/squeezylemons/projects' then link=f end
          end
          assert(link and link:IsShown())
          link.scripts.OnEscapePressed(link)
          clickText('Created by SqueezyLemons')
          assert(link:GetText()=='https://www.curseforge.com/members/squeezylemons/projects')
        ''')

    def test_reunion_notices_once_and_toggle(self):
        self.lua.execute('''
          messages={}; DEFAULT_CHAT_FRAME.AddMessage=function(_,text) if text:find("You've met",1,true) then messages[#messages+1]=text end end
          FamiliarFaces.Capture(); assert(#messages==0)
          FamiliarFaces.db.people['Alice-OtherRealm'].note='Patient healer'
          roster={}; FamiliarFaces.Capture()
          roster={{name='Alice',realm='Other Realm',class='PRIEST'}}
          clock=2000; FamiliarFaces.Capture(); FamiliarFaces.Capture()
          assert(#messages==1 and messages[1]:find('Elwynn Forest',1,true) and messages[1]:find('Patient healer',1,true))
          SlashCmdList.FAMILIARFACES('pause'); SlashCmdList.FAMILIARFACES('resume')
          assert(#messages==1)
          roster={}; FamiliarFaces.Capture(); FamiliarFaces.db.reunionNotices=false
          roster={{name='Alice',realm='Other Realm',class='PRIEST'}}; FamiliarFaces.Capture()
          assert(#messages==1)
        ''')

    def test_last_adventure_and_favourite_first(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
          FamiliarFaces.db.people['Alice-OtherRealm'].favourite=true
          clock=2000; zone='Deadmines'; instanceType='party'
          roster={{name='Bob',realm='Home Realm',class='WARRIOR'}}; FamiliarFaces.Capture()
          assert(FamiliarFaces.LastAdventure('Alice-OtherRealm').zone=='Elwynn Forest')
          local list=FamiliarFaces.Query('Companions',{sort='lastSeen',favouritesFirst=true})
          assert(list[1].name=='Alice-OtherRealm')
          list=FamiliarFaces.Query('Companions',{sort='lastSeen',favouritesFirst=false})
          assert(list[1].name=='Bob-HomeRealm')
        ''')

    def test_forget_adventure_preserves_profiles_and_active_suppression(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local session=FamiliarFaces.active
          local person=FamiliarFaces.db.people['Alice-OtherRealm']; person.note='Helpful'; person.favourite=true
          assert(FamiliarFaces.ForgetAdventure(session)); FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==0 and person.encounters==0 and person.note=='Helpful' and person.favourite)
          assert(#FamiliarFaces.Query('Companions',{})==1)
          assert(#FamiliarFaces.Query('Companions',{kind='Dungeon'})==0)
          roster={}; FamiliarFaces.Capture(); roster={{name='Alice',realm='Other Realm',class='PRIEST'}}
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==1 and person.encounters==1)
        ''')

    def test_forget_person_removes_history_and_recounts_others(self):
        self.lua.execute('''
          roster[2]={name='Bob',realm='Home Realm',class='WARRIOR'}
          FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
          clock=2000; FamiliarFaces.Capture()
          assert(FamiliarFaces.ForgetPerson('Alice-OtherRealm')); FamiliarFaces.Capture()
          assert(FamiliarFaces.db.people['Alice-OtherRealm']==nil)
          assert(#FamiliarFaces.db.sessions==2 and #FamiliarFaces.db.sessions[1].members==1)
          assert(FamiliarFaces.db.people['Bob-HomeRealm'].encounters==2)
          roster={}; FamiliarFaces.Capture(); roster={{name='Alice',realm='Other Realm',class='PRIEST'}}
          FamiliarFaces.Capture(); assert(FamiliarFaces.db.people['Alice-OtherRealm'].encounters==1)
        ''')

    def test_quick_notes_and_confirmed_forget(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); SlashCmdList.FAMILIARFACES(''); clickText('Companions')
          for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end
          clickText('Helpful'); clickText('Helpful'); clickText('Patient'); clickText('Save note')
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='Helpful; Patient')
          clickText('Forget companion'); clickText('Cancel')
          assert(FamiliarFaces.db.people['Alice-OtherRealm'])
          clickText('Forget companion'); clickText('Confirm forget')
          assert(FamiliarFaces.db.people['Alice-OtherRealm']==nil and #FamiliarFaces.db.sessions==0)
        ''')

if __name__ == '__main__':
    unittest.main(verbosity=2)

