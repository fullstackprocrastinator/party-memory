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
  RegisterEvent=noop, SetSize=function(self,w,h) self.width=w; self.height=h end,
  SetPoint=function(self,p,a,b,c,d) self.point=p; self.pointX=type(a)=='number' and a or c; self.pointY=type(b)=='number' and b or d end,
  SetWidth=function(self,w) self.width=w end, GetWidth=function(self) return self.width end,
  GetHeight=function(self) return self.height end, ClearAllPoints=noop,
  SetResizable=noop, SetResizeBounds=noop, StartSizing=noop,
  SetMultiLine=function(self,value) self.multiline=value end, SetScrollChild=noop, SetScale=function(self,s) self.scale=s end, GetScale=function(self) return self.scale or 1 end,
  SetHeight=function(self,h) self.height=h end, SetJustifyH=noop, SetJustifyV=noop, SetFontObject=noop, SetWordWrap=noop,
  EnableMouseWheel=noop, SetVerticalScroll=function(self,v) self.scroll=v end, GetVerticalScroll=function(self) return self.scroll or 0 end,
  SetFrameStrata=noop, SetMovable=noop, EnableMouse=noop, RegisterForDrag=noop,
  StartMoving=noop, StopMovingOrSizing=noop, SetClampedToScreen=noop,
  SetHighlightTexture=noop, SetAutoFocus=noop, SetMaxLetters=noop,
  ClearFocus=noop, SetAllPoints=noop, SetTexture=noop, SetVertexColor=noop,
  SetAlpha=noop, SetTexCoord=noop, SetTextColor=noop,
  SetFocus=noop, HighlightText=noop,
  SetText=function(self,t) self.text=t; if self.scripts.OnTextChanged then self.scripts.OnTextChanged(self) end end,
  GetText=function(self) return self.text end,
  IsShown=function(self) return self.visible end,
  Show=function(self) self.visible=true; if self.scripts.OnShow then self.scripts.OnShow(self) end end,
  Hide=function(self) self.visible=false; if self.scripts.OnHide then self.scripts.OnHide(self) end end,
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
        for name in ('Store.lua', 'Backup.lua', 'Core.lua', 'Tooltips.lua', 'UI.lua'):
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
          clickText('|cffffffffAlice-OtherRealm|r | Healer')
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
          clickText('More players'); clickText('More players'); clickText('|cffc79c6ePlayer6-HomeRealm|r | Unknown (left)')
          clickText('Whisper'); assert(whispered=='Player6-HomeRealm')
        ''')

    def test_existing_saved_rosters_remain_browsable(self):
        self.lua.execute('''
          FamiliarFacesDB=FamiliarFaces.Init({version=1,sessions={{id=1,owner='Old',kind='Questing',zone='OldZone',
            started=100,lastSeen=110,members={{name='OldPlayer'}}}},nextID=2})
          assert(#FamiliarFaces.Search('OldPlayer')==1)
          SlashCmdList.FAMILIARFACES('')
          for _,b in ipairs(buttons) do if type(b.text)=='table' then b.scripts.OnClick(b); break end end
          clickText('OldPlayer | Unknown')
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==2)
        ''')
        # Rows carry a FontString in .text rather than a button label.
        self.lua.execute('''
          for _,b in ipairs(buttons) do if type(b.text)=='table' then b.scripts.OnClick(b); break end end
          clickText('|cffffffffAlice-OtherRealm|r | Healer'); clickText('Favourite')
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

    def test_nicknames_recent_and_current_party_filters(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
          FamiliarFaces.db.people['Alice-OtherRealm'].nickname='Westfall quest buddy'
          clock=clock+10*86400; roster={{name='Bob',realm='Home Realm',class='WARRIOR'}}; FamiliarFaces.Capture()
          assert(#FamiliarFaces.Query('Companions',{query='westfall quest buddy'})==1)
          assert(#FamiliarFaces.Query('Adventures',{query='westfall quest buddy'})==1)
          assert(#FamiliarFaces.Query('Adventures',{days=7})==1)
          assert(#FamiliarFaces.Query('Companions',{days=30})==2)
          assert(#FamiliarFaces.Query('Companions',{currentParty=true})==1)
          roster={}; FamiliarFaces.Capture()
          assert(#FamiliarFaces.Query('Companions',{currentParty=true})==0)
        ''')

    def test_draft_save_discard_and_roster_updates(self):
        self.lua.execute('''
          roster[2]={name='Bob',realm='Home Realm',class='WARRIOR'}; FamiliarFaces.Capture()
          SlashCmdList.FAMILIARFACES(''); clickText('Companions')
          local alice,bob
          for _,b in ipairs(buttons) do if b.entry then if b.entry.name=='Alice-OtherRealm' then alice=b elseif b.entry.name=='Bob-HomeRealm' then bob=b end end end
          alice.scripts.OnClick(alice)
          local fields={}; for _,f in ipairs(frames) do if f.kind=='EditBox' then fields[#fields+1]=f end end
          fields[2]:SetText('Draft note'); fields[3]:SetText('Quest buddy')
          clock=clock+15; FamiliarFaces.Capture(); assert(fields[2]:GetText()=='Draft note' and fields[3]:GetText()=='Quest buddy')
          bob.scripts.OnClick(bob); assert(FamiliarFaces.db.people['Alice-OtherRealm'].note==nil)
          clickText('Save'); assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='Draft note')
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].nickname=='Quest buddy')
          fields[2]:SetText('Unsaved Bob'); clickText('Close'); clickText('Discard')
          assert(not FamiliarFacesWindow:IsShown() and FamiliarFaces.db.people['Bob-HomeRealm'].note==nil)
        ''')

    def test_escape_close_cancel_and_saved_geometry(self):
        self.lua.execute('''
          UIParent.GetCenter=function() return 560,440 end
          FamiliarFaces.db.window={width=1300,height=950,x=40,y=-25}
          FamiliarFaces.Capture(); SlashCmdList.FAMILIARFACES(''); clickText('Companions')
          assert(FamiliarFacesWindow:GetWidth()==1300 and FamiliarFacesWindow.pointX==40)
          FamiliarFacesWindow.GetCenter=function() return 610,410 end
          for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end
          clickText('Helpful'); FamiliarFacesWindow:Hide(); assert(FamiliarFacesWindow:IsShown())
          clickText('Cancel'); assert(FamiliarFacesWindow:IsShown())
          clickText('Close'); clickText('Save'); assert(not FamiliarFacesWindow:IsShown())
          assert(FamiliarFaces.db.window.width==1300 and FamiliarFaces.db.window.x==50 and FamiliarFaces.db.window.y==-30)
          SlashCmdList.FAMILIARFACES('reset window'); assert(FamiliarFacesWindow:GetWidth()==1120)
        ''')

    def test_minimap_button_toggle_and_position(self):
        self.lua.execute('''
          Minimap=CreateFrame('Frame'); Minimap.GetCenter=function() return 100,100 end
          Minimap.GetEffectiveScale=function() return 1 end
          GetCursorPosition=function() return 180,100 end
          FamiliarFaces.InitMinimap(); local b=FamiliarFacesMinimapButton
          assert(b and b:IsShown()); b.scripts.OnClick(b); assert(FamiliarFacesWindow:IsShown())
          b.scripts.OnDragStart(b); b.scripts.OnUpdate(b); b.scripts.OnDragStop(b)
          assert(math.abs(FamiliarFaces.db.minimap.angle)<0.001 and b.scripts.OnUpdate==nil)
          SlashCmdList.FAMILIARFACES('minimap'); assert(not b:IsShown())
          SlashCmdList.FAMILIARFACES('minimap'); assert(b:IsShown())
        ''')

    def test_adventure_notes_pins_and_draft_guard(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); SlashCmdList.FAMILIARFACES('')
          for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end
          local field; local seen=0
          for _,f in ipairs(frames) do if f.kind=='EditBox' then seen=seen+1; if seen==2 then field=f end end end
          field:SetText('First dungeon clear'); clickText('Pin adventure'); FamiliarFaces.Capture()
          assert(field:GetText()=='First dungeon clear')
          clickText('Close'); clickText('Save')
          assert(FamiliarFaces.db.sessions[1].note=='First dungeon clear' and FamiliarFaces.db.sessions[1].pinned)
          assert(#FamiliarFaces.Query('Adventures',{query='first dungeon clear',pinned=true})==1)
          assert(#FamiliarFaces.Search('first dungeon clear')==1)
        ''')

    def test_tags_recent_shortcut_and_first_meeting(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local first=FamiliarFaces.active; first.pinned=true; FamiliarFaces.EndSession(clock)
          clock=2000; roster[2]={name='Bob',realm='Home Realm',class='WARRIOR'}; zone='Deadmines'; FamiliarFaces.Capture()
          local alice=FamiliarFaces.db.people['Alice-OtherRealm']; FamiliarFaces.ToggleTag(alice,'Helpful guide')
          assert(FamiliarFaces.FirstAdventure(alice.name)==first and FamiliarFaces.LastAdventure(alice.name).zone=='Deadmines')
          assert(#FamiliarFaces.Query('Companions',{tag='Helpful guide'})==1)
          assert(#FamiliarFaces.Query('Companions',{query='helpful guide'})==1)
          assert(FamiliarFaces.Query('Adventures',{})[1]==first)
          SlashCmdList.FAMILIARFACES(''); clickText('Recent companions')
          assert(#FamiliarFaces.Query('Companions',{recentParty=true})==2)
          for _,b in ipairs(buttons) do if b.entry and b.entry.name==alice.name then b.scripts.OnClick(b); break end end
          clickText('Private tags'); clickText('Helpful guide [on]'); assert(not FamiliarFaces.HasTag(alice,'Helpful guide'))
        ''')

    def test_backup_round_trip_and_multipart_copy(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local original=FamiliarFaces.db
          local p=original.people['Alice-OtherRealm']; p.note='quotes " and newline\\n and backslash \\\\'; p.nickname='Quest buddy'; p.tags={['Run again']=true}
          original.sessions[1].note='A memorable run'; original.sessions[1].pinned=true
          local backup=FamiliarFaces.Export(); assert(loadstring(backup))(); local copy=FamiliarFacesDB
          assert(copy.people[p.name].note==p.note and copy.people[p.name].tags['Run again'] and copy.sessions[1].pinned)
          p.note=string.rep('x',15000); SlashCmdList.FAMILIARFACES('export')
          local field; for _,f in ipairs(frames) do if f.kind=='EditBox' and f.text:find('-- Familiar Faces journal backup',1,true) then field=f end end
          assert(field and #field.text==12000); local first=field.text; clickText('Next part')
          assert(first..field.text==FamiliarFaces.Export())
          local unicode=string.rep('é',8000); local parts=FamiliarFaces.ExportParts(unicode)
          assert(table.concat(parts)==unicode and #parts==2)
        ''')

    def test_small_screen_scale_and_keyboard_editing(self):
        self.lua.execute('''
          UIParent.GetWidth=function() return 900 end; UIParent.GetHeight=function() return 700 end
          FamiliarFaces.Capture(); SlashCmdList.FAMILIARFACES('')
          assert(FamiliarFacesWindow:GetWidth()*FamiliarFacesWindow:GetScale()<=860)
          assert(FamiliarFacesWindow:GetHeight()*FamiliarFacesWindow:GetScale()<=660)
          local fields={}; for _,f in ipairs(frames) do if f.kind=='EditBox' then fields[#fields+1]=f end end
          fields[1].scripts.OnEnterPressed(fields[1]); fields[2]:SetText('Adventure keyboard note')
          assert(fields[2].multiline and not fields[2].scripts.OnEnterPressed)
          clickText('Save note'); assert(FamiliarFaces.db.sessions[1].note=='Adventure keyboard note')
          fields[2].scripts.OnTabPressed(fields[2]); fields[1].scripts.OnTabPressed(fields[1])
        ''')

    def test_same_realm_nil_realm_names(self):
        self.lua.execute('''
          roster={{name='Alice',class='PRIEST'}}
          local original=UnitName
          UnitName=function(unit) if unit=='player' then return 'Me',nil end; return original(unit) end
          FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==1)
          assert(FamiliarFaces.db.sessions[1].owner=='Me-HomeRealm')
          assert(FamiliarFaces.db.people['Alice-HomeRealm'])
        ''')

    def test_restricted_realm_waits_for_safe_roster(self):
        self.lua.execute('''
          local restricted={}; issecretvalue=function(value) return rawequal(value,restricted) end
          local original=UnitName
          UnitName=function(unit) if unit=='party1' then return 'Alice',restricted end; return original(unit) end
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          UnitName=function(unit) if unit=='party1' then return '',nil end; return original(unit) end
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          UnitName=function(unit) if unit=='party1' then return 'Alice',nil end; return original(unit) end
          local realmName=GetRealmName; GetRealmName=function() return nil end
          FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)
          GetRealmName=realmName
          FamiliarFaces.Capture(); assert(FamiliarFaces.db.people['Alice-HomeRealm'])
        ''')

    def test_world_transfer_empty_roster_preserves_session(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local session=FamiliarFaces.active
          frames[1].scripts.OnEvent(frames[1],'PLAYER_LEAVING_WORLD')
          roster={}; FamiliarFaces.Capture(); assert(FamiliarFaces.active==session)
          frames[1].scripts.OnEvent(frames[1],'PLAYER_ENTERING_WORLD')
          assert(FamiliarFaces.active==session)
          clock=clock+2; roster={{name='Alice',realm='Other Realm',class='PRIEST'}}
          zone='Deadmines'; instanceType='party'; FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==1 and FamiliarFaces.active==session and session.zone=='Deadmines')
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].encounters==1)
          roster={}; clock=clock+6; FamiliarFaces.Capture(); assert(FamiliarFaces.active==nil)
        ''')

    def reload_addon(self):
        """Reload a serialized SavedVariables snapshot into a fresh Lua VM."""
        backup = self.lua.eval('FamiliarFaces.Export()')
        now = self.lua.eval('clock')
        self.setUp()
        self.lua.execute(backup)
        self.lua.execute('FamiliarFaces.Init(FamiliarFacesDB)')
        self.lua.globals().clock = now

    def test_reload_resumes_without_duplicate_or_reunion_and_excludes_gap(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); clock=1060; FamiliarFaces.Capture()
          FamiliarFaces.db.people['Alice-OtherRealm'].note='Keep me'
        ''')
        self.reload_addon()
        self.lua.execute('''
          local messages=0; FamiliarFaces.NotifyReunion=function() messages=messages+1 end
          clock=1120; FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==1 and FamiliarFaces.active.id==1)
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].encounters==1)
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='Keep me' and messages==0)
          assert(FamiliarFaces.Duration(FamiliarFaces.active)==60)
          clock=1180; FamiliarFaces.Capture(); assert(FamiliarFaces.Duration(FamiliarFaces.active)==120)
        ''')
        self.reload_addon()
        self.lua.execute('clock=1200; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==1 and FamiliarFaces.Duration(FamiliarFaces.active)==120)')

    def test_resume_rejects_changed_roster_character_expired_or_closed_party(self):
        for change in (
            "roster[1].name='Bob'", "clock=1401",
            "local old=UnitName; UnitName=function(u) if u=='player' then return 'Alt','Home Realm' end; return old(u) end",
            "FamiliarFaces.db.sessions[1].ended=1000",
            "roster[2]={name='Bob',realm='Home Realm',class='WARRIOR'}",
        ):
            with self.subTest(change=change):
                self.setUp(); self.lua.execute('FamiliarFaces.Capture()'); self.reload_addon()
                self.lua.execute(change + '; FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==2)')
                self.lua.execute('assert(FamiliarFaces.db.sessions[2].ended==1000)')

    def test_resume_waits_for_loading_roster_but_solo_login_invalidates(self):
        self.lua.execute('FamiliarFaces.Capture()'); self.reload_addon()
        self.lua.execute('''
          roster={}; frames[1].scripts.OnEvent(frames[1],'PLAYER_ENTERING_WORLD')
          assert(FamiliarFaces.pendingResume)
          clock=1002; roster={{name='Alice',realm='Other Realm',class='PRIEST'}}; FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==1)
        ''')
        self.reload_addon()
        self.lua.execute('''
          roster={}; frames[1].scripts.OnEvent(frames[1],'PLAYER_ENTERING_WORLD')
          clock=1010; FamiliarFaces.Capture(); assert(not FamiliarFaces.pendingResume and not FamiliarFaces.db.continuity)
          roster={{name='Alice',realm='Other Realm',class='PRIEST'}}; FamiliarFaces.Capture()
          assert(#FamiliarFaces.db.sessions==2)
        ''')

    def test_forgotten_party_and_companion_stay_forgotten_through_reload(self):
        self.lua.execute('FamiliarFaces.Capture(); FamiliarFaces.ForgetAdventure(FamiliarFaces.active)')
        self.reload_addon()
        self.lua.execute('FamiliarFaces.Capture(); assert(#FamiliarFaces.db.sessions==0)')
        self.setUp()
        self.lua.execute('''
          roster[2]={name='Bob',realm='Home Realm',class='WARRIOR'}; FamiliarFaces.Capture()
          FamiliarFaces.ForgetPerson('Alice-OtherRealm')
        ''')
        self.reload_addon()
        self.lua.execute('''
          roster[2]={name='Bob',realm='Home Realm',class='WARRIOR'}; FamiliarFaces.Capture()
          assert(not FamiliarFaces.db.people['Alice-OtherRealm'] and #FamiliarFaces.active.members==1)
        ''')
        self.setUp()
        self.lua.execute("FamiliarFaces.Capture(); FamiliarFaces.ForgetPerson('Alice-OtherRealm')")
        self.reload_addon()
        self.lua.execute("FamiliarFaces.Capture(); assert(not FamiliarFaces.db.people['Alice-OtherRealm'] and #FamiliarFaces.db.sessions==0)")

    def test_custom_tags_validation_rename_delete_and_persistence(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local p=FamiliarFaces.db.people['Alice-OtherRealm']
          assert(FamiliarFaces.CreateTag('  Evening regular  ')=='Evening regular')
          assert(not FamiliarFaces.CreateTag('EVENING REGULAR'))
          assert(not FamiliarFaces.CreateTag('Helpful guide'))
          assert(not FamiliarFaces.CreateTag('bad|tag'))
          assert(not FamiliarFaces.CreateTag(string.rep('x',49)))
          FamiliarFaces.ToggleTag(p,'Evening regular')
          assert(FamiliarFaces.RenameTag('Evening regular','Evening friend')=='Evening friend')
          assert(not p.tags['Evening regular'] and p.tags['Evening friend'])
          assert(#FamiliarFaces.Query('Companions',{tag='Evening friend'})==1)
          assert(#FamiliarFaces.Query('Adventures',{query='evening friend'})==1)
          assert(not FamiliarFaces.DeleteTag('Helpful guide'))
        ''')
        self.reload_addon()
        self.lua.execute('''
          assert(FamiliarFaces.db.customTags[1]=='Evening friend')
          assert(FamiliarFaces.DeleteTag('Evening friend'))
          assert(not FamiliarFaces.db.people['Alice-OtherRealm'].tags['Evening friend'])
          for i=1,20 do assert(FamiliarFaces.CreateTag('Tag '..i)) end
          assert(not FamiliarFaces.CreateTag('One too many'))
        ''')

    def test_tag_editor_create_rename_confirm_remove_and_filter(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); FamiliarFaces.Toggle(); clickText('Companions')
          for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end
          clickText('Private tags'); FamiliarFacesTagName:SetText('Evening regular'); clickText('Create tag')
          clickText('Evening regular [off]'); assert(FamiliarFaces.db.people['Alice-OtherRealm'].tags['Evening regular'])
          local function editTag() for _,b in ipairs(buttons) do if b.caption=='Edit' and b:IsShown() then b.scripts.OnClick(b); return end end end
          editTag(); FamiliarFacesTagName:SetText('Evening friend'); clickText('Rename tag')
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].tags['Evening friend'])
          editTag(); clickText('Remove tag'); assert(#FamiliarFaces.db.customTags==1)
          clickText('Confirm removal'); assert(#FamiliarFaces.db.customTags==0)
          for i=1,9 do FamiliarFaces.CreateTag('Custom '..i) end
          clickText('More tags'); clickText('Custom 9 [off]')
          assert(FamiliarFaces.db.people['Alice-OtherRealm'].tags['Custom 9'])
        ''')

    def test_character_filter_both_views_without_orphan_leak(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
          FamiliarFaces.Record('Alt-HomeRealm',{{name='Bob-HomeRealm',class='WARRIOR'}},{kind='Questing',zone='Westfall'},1100)
          FamiliarFaces.db.people['Orphan-HomeRealm']={name='Orphan-HomeRealm',favourite=true}
          assert(#FamiliarFaces.Query('Adventures',{owner='Me-HomeRealm'})==1)
          local people=FamiliarFaces.Query('Companions',{owner='Alt-HomeRealm'})
          assert(#people==1 and people[1].name=='Bob-HomeRealm')
          assert(#FamiliarFaces.Query('Companions',{owner='Alt-HomeRealm',query='Alice'})==0)
          assert(#FamiliarFaces.Characters()==2)
          FamiliarFaces.Toggle(); clickText('Character: All')
          clickText('Alt-HomeRealm')
          local shown=0; for _,b in ipairs(buttons) do if b.entry then shown=shown+1; assert(b.entry.owner=='Alt-HomeRealm') end end
          assert(shown==1); clickText('Clear filters')
          shown=0; for _,b in ipairs(buttons) do if b.entry then shown=shown+1 end end; assert(shown==2)
        ''')

    def test_tooltip_reminders_are_private_optional_and_skip_restricted_units(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); local p=FamiliarFaces.db.people['Alice-OtherRealm']; p.note='Private test'; p.favourite=true
          local lines=FamiliarFaces.TooltipLines(p.name)
          assert(table.concat(lines,' '):find('favourite') and not table.concat(lines,' '):find('Private test'))
          FamiliarFaces.db.tooltipNotes=true
          assert(table.concat(FamiliarFaces.TooltipLines(p.name),' '):find('Private test'))
          GameTooltip=CreateFrame('GameTooltip'); GameTooltip.lines={}
          GameTooltip.GetUnit=function() return 'Alice','party1' end
          GameTooltip.AddLine=function(self,s) table.insert(self.lines,s) end
          UnitIsPlayer=function() return true end
          FamiliarFaces.AddUnitTooltip(GameTooltip); local count=#GameTooltip.lines; assert(count>1)
          FamiliarFaces.AddUnitTooltip(GameTooltip); assert(#GameTooltip.lines==count)
          GameTooltip.familiarFacesName=nil; combat=true; FamiliarFaces.AddUnitTooltip(GameTooltip); assert(#GameTooltip.lines==count)
          combat=false; UnitIsPlayer=function() return false end; FamiliarFaces.AddUnitTooltip(GameTooltip); assert(#GameTooltip.lines==count)
          local restricted={}; issecretvalue=function(v) return rawequal(v,restricted) end
          GameTooltip.GetUnit=function() return 'Alice',restricted end
          FamiliarFaces.AddUnitTooltip(GameTooltip); assert(#GameTooltip.lines==count)
          FamiliarFaces.db.tooltips=false; assert(not FamiliarFaces.TooltipLines(p.name))
        ''')

    def test_tooltip_modern_and_legacy_hook_registration(self):
        for modern in (False, True):
            with self.subTest(modern=modern):
                self.setUp()
                self.lua.execute('''
                  GameTooltip=CreateFrame('GameTooltip')
                  GameTooltip.HookScript=function(self,event,fn) self.scripts[event]=fn end
                  GameTooltip.lines={}; GameTooltip.AddLine=function(self,s) table.insert(self.lines,s) end
                  GameTooltip.GetUnit=function() return 'Alice','party1' end
                ''')
                if modern:
                    self.lua.execute('Enum={TooltipDataType={Unit=2}}; TooltipDataProcessor={AddTooltipPostCall=function(kind,fn) assert(kind==2); callback=fn end}')
                self.lua.execute('''
                  FamiliarFaces.InitTooltips(); FamiliarFaces.Capture()
                  local fn=callback or GameTooltip.scripts.OnTooltipSetUnit
                  assert(fn); fn(GameTooltip); assert(#GameTooltip.lines>1)
                  GameTooltip.scripts.OnTooltipCleared(GameTooltip); assert(not GameTooltip.familiarFacesName)
                ''')

    def test_recap_opt_in_defers_combat_and_opens_note(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); roster={}; FamiliarFaces.Capture()
          FamiliarFaces.MaybeShowRecap(); assert(not FamiliarFacesRecap)
          FamiliarFaces.db.recaps=true
          roster={{name='Alice',realm='Other Realm',class='PRIEST'}}; FamiliarFaces.Capture()
          clock=1060; combat=true; roster={}; FamiliarFaces.Capture(); FamiliarFaces.MaybeShowRecap()
          assert(FamiliarFaces.pendingRecap and not FamiliarFacesRecap)
          combat=false; FamiliarFaces.MaybeShowRecap(); assert(FamiliarFacesRecap:IsShown())
          clickText('Favourite'); assert(FamiliarFaces.db.people['Alice-OtherRealm'].favourite)
          clickText('Add note'); assert(FamiliarFacesWindow:IsShown() and not FamiliarFacesRecap:IsShown())
          clickText('Helpful'); clickText('Save note'); assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='Helpful')
        ''')

    def test_recap_pagination_suppression_and_stale_entries(self):
        self.lua.execute('''
          FamiliarFaces.db.recaps=true; FamiliarFaces.Capture()
          for i=1,6 do roster={{name='Person'..i,realm='Home Realm',class='WARRIOR'}}; FamiliarFaces.Capture() end
          roster={}; FamiliarFaces.Capture(); FamiliarFaces.MaybeShowRecap()
          assert(FamiliarFacesRecap:IsShown()); clickText('Next'); clickText('Keep adventuring')
          FamiliarFaces.MaybeShowRecap(); assert(not FamiliarFacesRecap:IsShown())
          roster={{name='Alice',realm='Other Realm',class='PRIEST'}}; FamiliarFaces.Capture()
          SlashCmdList.FAMILIARFACES('pause'); assert(not FamiliarFaces.pendingRecap)
          SlashCmdList.FAMILIARFACES('resume'); raid=true; FamiliarFaces.Capture(); assert(not FamiliarFaces.pendingRecap)
          raid=false; FamiliarFaces.Capture(); roster={}; FamiliarFaces.Capture()
          FamiliarFaces.ForgetAdventure(FamiliarFaces.pendingRecap); FamiliarFaces.MaybeShowRecap()
          assert(not FamiliarFacesRecap:IsShown())
        ''')

    def test_settings_defaults_persistence_and_clear(self):
        self.lua.execute('''
          assert(FamiliarFaces.db.tooltips and not FamiliarFaces.db.tooltipNotes and not FamiliarFaces.db.recaps)
          SlashCmdList.FAMILIARFACES('settings'); assert(FamiliarFacesSettings:IsShown())
          clickText('End-of-adventure recaps: off'); clickText('Private notes in hover reminders: off')
          clickText('Favourites first: on'); clickText('Reunion notices: on'); clickText('Minimap button: on')
          assert(FamiliarFaces.db.recaps and FamiliarFaces.db.tooltipNotes and FamiliarFaces.db.minimap.hidden)
          SlashCmdList.FAMILIARFACES('clear confirm')
          assert(FamiliarFaces.db.recaps and FamiliarFaces.db.tooltipNotes and not FamiliarFaces.db.favouritesFirst)
        ''')
        self.reload_addon()
        self.lua.execute('assert(FamiliarFaces.db.recaps and FamiliarFaces.db.tooltipNotes and FamiliarFaces.db.minimap.hidden)')

    def test_recap_waits_for_dialogs_expires_and_hides_in_combat(self):
        self.lua.execute('''
          FamiliarFaces.db.recaps=true; FamiliarFaces.Capture(); roster={}; FamiliarFaces.Capture()
          SlashCmdList.FAMILIARFACES('settings'); FamiliarFaces.MaybeShowRecap(); assert(not FamiliarFacesRecap)
          FamiliarFacesSettings:Hide(); FamiliarFaces.MaybeShowRecap(); assert(FamiliarFacesRecap:IsShown())
          combat=true; FamiliarFaces.MaybeShowRecap(); assert(not FamiliarFacesRecap:IsShown() and FamiliarFaces.pendingRecap)
          combat=false; FamiliarFaces.MaybeShowRecap(); assert(FamiliarFacesRecap:IsShown())
          clickText('Keep adventuring')
          FamiliarFaces.QueueRecap(FamiliarFaces.db.sessions[1]); clock=clock+601
          FamiliarFaces.MaybeShowRecap(); assert(not FamiliarFacesRecap:IsShown() and not FamiliarFaces.pendingRecap)
        ''')

    def test_recap_note_navigation_preserves_unsaved_draft(self):
        self.lua.execute('''
          FamiliarFaces.db.recaps=true; FamiliarFaces.Capture(); FamiliarFaces.Toggle()
          for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end
          local fields={}; for _,f in ipairs(frames) do if f.kind=='EditBox' then fields[#fields+1]=f end end
          fields[2]:SetText('Keep this adventure draft'); roster={}; FamiliarFaces.Capture(); FamiliarFaces.MaybeShowRecap()
          clickText('Add note'); assert(FamiliarFacesDraftDialog:IsShown())
          clickText('Cancel'); assert(fields[2]:GetText()=='Keep this adventure draft')
          clickText('Add note'); clickText('Save')
          assert(FamiliarFaces.db.sessions[1].note=='Keep this adventure draft' and not FamiliarFacesRecap:IsShown())
          clickText('Helpful'); clickText('Save note'); assert(FamiliarFaces.db.people['Alice-OtherRealm'].note=='Helpful')
        ''')

    def test_import_roundtrip_legacy_and_multiline_unicode(self):
        self.lua.execute(r'''
          local PM=FamiliarFaces; PM.Capture(); roster={}; PM.Capture()
          local p=PM.db.people['Alice-OtherRealm']; p.note='A "quote", a \\ slash\nCafé healer\twith patience'; p.nickname='Étoile'
          PM.CreateTag('Evening runs'); p.tags={['Evening runs']=true}; p.favourite=true
          PM.db.sessions[1].note='Line one\nLine two'; PM.db.sessions[1].pinned=true
          for _,version in ipairs({5,6,7}) do
            PM.db.version=version; local plan,err=PM.PreviewImport(PM.Export(),'replace'); assert(plan,err)
            assert(plan.summary.added==1 and plan.summary.profiles==1)
            assert(PM.ApplyImport(plan)); assert(PM.db.people[p.name].note==p.note)
            assert(PM.db.people[p.name].nickname==p.nickname and PM.db.people[p.name].tags['Evening runs'])
            assert(PM.db.sessions[1].pinned and PM.db.sessions[1].note=='Line one\nLine two')
            assert(PM.LastRole(p.name)=='HEALER' and PM.db.people[p.name].encounters==1)
          end
        ''')

    def test_import_rejects_code_partial_oversized_and_bad_shapes(self):
        self.lua.execute(r'''
          local PM=FamiliarFaces; PM.Capture(); local before=PM.Export()
          local bad={before..' error("executed")',before:sub(1,-15),'FamiliarFacesDB=os.execute("anything")',
            'FamiliarFacesDB={ ["people"]={}, ["people"]={}, ["sessions"]={}, ["version"]=7}',
            'FamiliarFacesDB={ ["people"]={}, ["sessions"]={[2]={}}, ["version"]=7}',
            string.rep('x',2*1024*1024+1)}
          for _,text in ipairs(bad) do local plan,err=PM.PreviewImport(text,'merge'); assert(not plan and type(err)=='string'); assert(PM.Export()==before) end
          local original=PM.db.sessions[1].lastSeen; PM.db.sessions[1].lastSeen=-1
          assert(not PM.PreviewImport(PM.Export(),'merge')); PM.db.sessions[1].lastSeen=original
          PM.db.version=99; assert(not PM.PreviewImport(PM.Export(),'merge'))
        ''')

    def test_import_merge_conflicts_dedup_and_repeated_import(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); roster={}; PM.Capture()
          local p=PM.db.people['Alice-OtherRealm']; p.note='Imported note'; p.nickname='Imported name'; p.favourite=true
          PM.db.sessions[1].note='Imported adventure'; PM.db.sessions[1].pinned=true
          PM.CreateTag('Evenings'); p.tags={Evenings=true}; local backup=PM.Export()
          p.note='My note'; p.nickname='My name'; p.favourite=false; p.tags={}
          PM.db.sessions[1].id=42; PM.db.sessions[1].note='My adventure'; PM.db.sessions[1].pinned=false
          local plan,err=PM.PreviewImport(backup,'merge'); assert(plan,err)
          assert(plan.summary.added==0 and plan.summary.duplicates==1 and plan.summary.conflicts==3)
          assert(not p.favourite and PM.db.sessions[1].id==42)
          assert(PM.ApplyImport(plan)); p=PM.db.people[p.name]
          assert(p.note=='My note' and p.nickname=='My name' and p.favourite and p.tags.Evenings)
          assert(#PM.db.sessions==1 and PM.db.sessions[1].id==42 and PM.db.sessions[1].pinned)
          plan=assert(PM.PreviewImport(backup,'merge')); assert(PM.ApplyImport(plan)); assert(#PM.db.sessions==1)
        ''')

    def test_import_remaps_ids_preserves_settings_and_replace(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); roster={}; PM.Capture(); local backup=PM.Export()
          FamiliarFacesDB=PM.Init({enabled=false,recaps=true,rememberView=false,minimap={hidden=true,angle=90}})
          PM.db.enabled=true
          PM.Record('Alt',{{name='Bram',role='TANK'}},{kind='Dungeon',zone='Other'},2000); PM.EndSession(2010)
          PM.db.enabled=false
          local plan,err=PM.PreviewImport(backup,'merge'); assert(plan,err); assert(PM.ApplyImport(plan))
          assert(#PM.db.sessions==2 and PM.db.sessions[1].id~=PM.db.sessions[2].id)
          assert(not PM.db.enabled and PM.db.recaps and not PM.db.rememberView and PM.db.minimap.hidden)
          plan=assert(PM.PreviewImport(backup,'replace')); assert(PM.ApplyImport(plan))
          assert(#PM.db.sessions==1 and not PM.db.people.Bram and PM.db.people['Alice-OtherRealm'])
          assert(not PM.db.enabled and PM.db.recaps and not PM.db.rememberView)
        ''')

    def test_import_blocked_in_party_raid_combat_or_after_changes(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); local backup=PM.Export()
          local plan=assert(PM.PreviewImport(backup,'merge')); assert(not PM.ApplyImport(plan))
          roster={}; PM.Capture(); plan=assert(PM.PreviewImport(backup,'merge'))
          combat=true; assert(not PM.ApplyImport(plan)); combat=false
          raid=true; assert(not PM.ApplyImport(plan)); raid=false
          PM.db.people['Alice-OtherRealm'].note='Changed since preview'; assert(not PM.ApplyImport(plan))
          plan=assert(PM.PreviewImport(backup,'merge')); assert(PM.ApplyImport(plan))
        ''')

    def test_import_custom_tag_limit_case_mapping_and_unknown_tag(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); roster={}; PM.Capture()
          PM.CreateTag('Friends'); PM.db.people['Alice-OtherRealm'].tags={Friends=true}; local backup=PM.Export()
          PM.RenameTag('Friends','FRIENDS')
          local plan=assert(PM.PreviewImport(backup,'merge')); assert(#plan.data.customTags==1 and plan.data.people['Alice-OtherRealm'].tags.FRIENDS)
          for i=1,19 do PM.CreateTag('Tag '..i) end
          PM.RenameTag('FRIENDS','Different'); assert(not PM.PreviewImport(backup,'merge'))
          PM.db.people['Alice-OtherRealm'].tags={Unknown=true}; assert(not PM.PreviewImport(PM.Export(),'replace'))
        ''')

    def test_import_ui_parts_preview_confirmation_and_cancel(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); roster={}; PM.Capture(); local backup=PM.Export()
          SlashCmdList.FAMILIARFACES('import'); assert(FamiliarFacesImport:IsShown())
          FamiliarFacesImportText:SetText(backup:sub(1,120)); clickText('Add pasted part')
          FamiliarFacesImportText:SetText(backup:sub(121)); clickText('Preview import')
          assert(FamiliarFacesImport.plan and FamiliarFacesImport.plan.summary.duplicates==1)
          local old=PM.db; clickText('Apply import'); assert(PM.db==old)
          clickText('Confirm merge'); assert(PM.db~=old and #PM.db.sessions==1 and not FamiliarFacesImport:IsShown())
          SlashCmdList.FAMILIARFACES('import'); FamiliarFacesImportText:SetText(backup)
          clickText('Mode: Merge'); clickText('Preview import'); clickText('Apply import')
          assert(FamiliarFacesImport.confirm and FamiliarFacesImport.mode=='replace')
          FamiliarFacesImportText:SetText('bad'); assert(not FamiliarFacesImport.plan and not FamiliarFacesImport.confirm)
          FamiliarFacesImport:Hide(); assert(FamiliarFacesImportText:GetText()=='')
        ''')

    def test_dropdown_selection_and_menu_pagination(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); PM.Toggle()
          clickText('Activity: All'); clickText('Dungeon'); assert(PM.db.viewState.options.kind=='Dungeon')
          clickText('Clear filters'); clickText('Role: All'); clickText('Healer'); assert(PM.db.viewState.options.role=='HEALER')
          clickText('When: Any time'); clickText('Last 30 days'); assert(PM.db.viewState.options.days==30)
          clickText('Class: All'); clickText('PRIEST'); assert(PM.db.viewState.options.class=='PRIEST')
          for i=1,12 do PM.CreateTag('Tag '..i) end
          clickText('Tag: All'); local menu=FamiliarFacesFilterMenu; menu.scripts.OnMouseWheel(menu,-1)
          assert(menu.page==2); clickText('Tag 12'); assert(PM.db.viewState.options.tag=='Tag 12' and not menu:IsShown())
          clickText('Clear filters'); assert(not PM.db.viewState.options.role and not PM.db.viewState.options.tag)
        ''')

    def test_remember_view_reload_reset_opt_out_and_stale_filters(self):
        self.lua.execute('''
          FamiliarFaces.Capture(); FamiliarFaces.Toggle(); clickText('Companions'); clickText('Role: All'); clickText('Healer')
          clickText('Favourites: off')
          for _,f in ipairs(frames) do if f.kind=='EditBox' then f:SetText('Alice'); break end end
          clickText('Companion'); assert(FamiliarFaces.db.viewState.options.sort=='name')
        ''')
        self.reload_addon()
        self.lua.execute('''
          FamiliarFaces.Toggle(); local saved=FamiliarFaces.db.viewState
          assert(saved.view=='Companions' and saved.options.role=='HEALER' and saved.options.favourites and saved.options.query=='Alice' and saved.options.sort=='name')
          SlashCmdList.FAMILIARFACES('reset view'); assert(FamiliarFaces.db.viewState.view=='Adventures' and FamiliarFaces.db.viewState.options.query=='')
          SlashCmdList.FAMILIARFACES('settings'); clickText('Remember my view: on'); assert(not FamiliarFaces.db.viewState)
          local view,opts=FamiliarFaces.CleanView({view='garbage',options={class='NOPE',role='DPS',tag='Deleted',owner='Deleted',sort='bad'}})
          assert(view=='Adventures' and not opts.class and not opts.role and not opts.tag and not opts.owner and opts.sort=='started')
          local _,utf=FamiliarFaces.CleanView({options={query=string.rep('é',101)}})
          assert(utf.query==string.rep('é',100))
        ''')
        self.reload_addon()
        self.lua.execute("FamiliarFaces.Toggle(); assert(not FamiliarFaces.db.rememberView and not FamiliarFaces.db.viewState)")

    def test_multiline_note_save_counter_guard_and_wheel(self):
        self.lua.execute(r'''
          FamiliarFaces.Capture(); FamiliarFaces.Toggle()
          for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end
          local note=FamiliarFacesNote; assert(note.multiline and not note.scripts.OnEnterPressed)
          note:SetText('Café\nPatient healer'); assert(FamiliarFaces.TextLength(note:GetText())==19)
          clickText('Close'); assert(FamiliarFacesDraftDialog:IsShown()); clickText('Save')
          assert(FamiliarFaces.db.sessions[1].note=='Café\nPatient healer')
          FamiliarFaces.Toggle(); note:SetText(string.rep('line\n',30)); note.scripts.OnMouseWheel(note,-1)
          clickText('Save note'); assert(FamiliarFaces.db.sessions[1].note==string.rep('line\n',30))
        ''')

    def test_list_mousewheel_clamps_and_browses(self):
        self.lua.execute('''
          local PM=FamiliarFaces
          for i=1,35 do PM.Record('Me',{{name='Person'..i}},{kind='Questing',zone='Zone '..i},1000+i); PM.EndSession(1000+i) end
          PM.Toggle(); local row
          for _,b in ipairs(buttons) do if b.entry then row=b; break end end
          assert(row.entry.started==1035)
          row.scripts.OnMouseWheel(row,-1); assert(row.entry.started==1019)
          row.scripts.OnMouseWheel(row,-1); assert(row.entry.started==1003)
          row.scripts.OnMouseWheel(row,-1); assert(row.entry.started==1003)
          row.scripts.OnMouseWheel(row,1); row.scripts.OnMouseWheel(row,1); row.scripts.OnMouseWheel(row,1); assert(row.entry.started==1035)
        ''')

    def test_roles_latest_unknown_and_historical_adventure_filters(self):
        self.lua.execute('''
          local PM=FamiliarFaces; PM.Capture(); PM.EndSession(clock)
          clock=1100; roster[1].role='DAMAGER'; PM.Capture(); PM.EndSession(clock)
          assert(PM.LastRole('Alice-OtherRealm')=='DAMAGER')
          assert(#PM.Query('Companions',{role='HEALER'})==0 and #PM.Query('Companions',{role='DAMAGER'})==1)
          assert(#PM.Query('Adventures',{role='HEALER'})==1 and #PM.Query('Adventures',{role='DAMAGER'})==1)
          clock=1200; UnitGroupRolesAssigned=nil; PM.Capture()
          assert(PM.LastRole('Alice-OtherRealm')=='NONE' and #PM.Query('Companions',{role='NONE'})==1)
          PM.ForgetAdventure(PM.active); assert(PM.LastRole('Alice-OtherRealm')=='DAMAGER')
        ''')

    def test_large_journal_index_reuse_and_mutation(self):
        self.lua.execute('''
          local PM=FamiliarFaces
          -- Build a saved journal directly so this test measures lookups rather than live capture.
          for i=1,3000 do
            local s={id=i,owner='Me',kind='Dungeon',zone='Dungeon '..i,started=i,lastSeen=i+10,members={},locations={}}
            for j=1,4 do local name='Person'..((i+j)%500); s.members[j]={name=name,class='PRIEST',role='HEALER'}; PM.db.people[name]={name=name} end
            PM.db.sessions[i]=s
          end
          PM.RebuildPeople(); local index=PM.HistoryIndex(); assert(#PM.Query('Companions',{sort='adventure'})==500)
          assert(PM.HistoryIndex()==index and #PM.Query('Adventures',{query='Dungeon',role='HEALER'})==3000)
          for _,p in pairs(PM.db.people) do assert(p.encounters==24 and PM.LastAdventure(p.name) and PM.FirstAdventure(p.name)) end
          PM.ForgetAdventure(PM.db.sessions[1]); assert(PM.HistoryIndex()~=index and #PM.Query('Adventures',{})==2999)
        ''')

if __name__ == '__main__':
    unittest.main(verbosity=2)

