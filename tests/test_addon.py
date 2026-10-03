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
 local f = {scripts={},visible=true,text='',kind=kind}
 local methods = {
  SetScript=function(self,event,fn) self.scripts[event]=fn end,
  RegisterEvent=noop, SetSize=noop, SetPoint=noop, SetWidth=noop,
  SetHeight=noop, SetJustifyH=noop, SetJustifyV=noop, SetFontObject=noop,
  SetFrameStrata=noop, SetMovable=noop, EnableMouse=noop, RegisterForDrag=noop,
  StartMoving=noop, StopMovingOrSizing=noop, SetClampedToScreen=noop,
  SetHighlightTexture=noop, SetAutoFocus=noop, SetMaxLetters=noop,
  ClearFocus=noop, SetAllPoints=noop, SetTexture=noop, SetVertexColor=noop,
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
 for _,b in ipairs(buttons) do if b.text==text then b.scripts.OnClick(b); return end end
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

if __name__ == '__main__':
    unittest.main(verbosity=2)

