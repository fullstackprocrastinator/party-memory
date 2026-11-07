local PM = FamiliarFaces
local frame = CreateFrame("Frame")
function PM.NotifyReunion(name, previous, person)
    local note = person and person.note
    DEFAULT_CHAT_FRAME:AddMessage("|cffe8bd72Familiar Faces:|r You've met "..name.." before - "..previous.zone..", "..date("%d %b",previous.lastSeen).."."
        ..(note and note:match("%S") and (" Note: "..note) or ""))
end
local function safe(value)
    return (not issecretvalue or not issecretvalue(value)) and value ~= nil
end
local function nameFor(unit)
    local name, realm = UnitName(unit)
    -- UnitName may omit the realm for same-realm players.
    if not safe(name) or (issecretvalue and issecretvalue(realm)) then return end
    if name == "" or name == UNKNOWNOBJECT or name == "Unknown" then return end
    realm = realm and realm ~= "" and realm or GetRealmName()
    if not safe(realm) or realm=="" then return end
    return name .. "-" .. realm:gsub("%s", "")
end
PM.NameFor=nameFor
function PM.Capture()
    if not PM.db then return end
    -- World-instance transfers briefly expose an empty or incomplete roster.
    if PM.loadingWorld then return end
    local raid = IsInRaid and IsInRaid() or (GetNumRaidMembers and GetNumRaidMembers() > 0)
    local count = GetNumSubgroupMembers and GetNumSubgroupMembers() or (GetNumPartyMembers and GetNumPartyMembers() or 0)
    if not raid and count==0 and (PM.active or PM.pendingResume) and PM.rosterGraceUntil and time()<PM.rosterGraceUntil then return end
    if raid or count == 0 then
        PM.currentParty={}; PM.EndSession(time(),false,not raid)
        if PM.Refresh then PM.Refresh() end; return
    end
    -- Check for leaving a party even in combat; defer restricted unit reads.
    if InCombatLockdown and InCombatLockdown() then return end
    local members = {}
    local current = {}
    for i = 1, count do
        local unit = "party" .. i
        local name = nameFor(unit)
        if not name then return end -- Wait for the complete roster rather than store Unknown players.
        local _, class = UnitClass(unit)
        local role = UnitGroupRolesAssigned and UnitGroupRolesAssigned(unit) or "NONE"
        members[#members + 1] = {name = name, class = safe(class) and class or nil, role = safe(role) and role or "NONE"}
        current[name]=true
    end
    local zone, instanceType, _, difficulty = GetInstanceInfo()
    if not safe(zone) or not safe(instanceType) or not safe(difficulty) then return end
    if instanceType == "pvp" or instanceType == "arena" or instanceType == "raid" then PM.currentParty={}; PM.EndSession(time()); if PM.Refresh then PM.Refresh() end; return end
    local owner = nameFor("player")
    if not owner then return end
    PM.currentOwner=owner
    PM.currentParty=current
    PM.Record(owner, members, { kind = instanceType == "party" and "Dungeon" or "Questing",
        zone = zone ~= "" and zone or GetZoneText() or "Unknown", difficulty = difficulty }, time())
    PM.Checkpoint(owner,members,time())
    if PM.Refresh then PM.Refresh() end
end
frame:RegisterEvent("ADDON_LOADED")
for _, event in ipairs({"PLAYER_ENTERING_WORLD", "PLAYER_LEAVING_WORLD", "GROUP_ROSTER_UPDATE", "PARTY_MEMBERS_CHANGED",
    "ZONE_CHANGED_NEW_AREA", "ZONE_CHANGED", "PLAYER_REGEN_ENABLED", "PLAYER_REGEN_DISABLED", "PLAYER_LOGOUT"}) do
    pcall(frame.RegisterEvent, frame, event)
end
frame:SetScript("OnEvent", function(_, event, name)
    if event == "ADDON_LOADED" then
        if name == "FamiliarFaces" then
            FamiliarFacesDB = PM.Init(FamiliarFacesDB)
            if PM.InitMinimap then PM.InitMinimap() end
            if PM.InitTooltips then PM.InitTooltips() end
        end
    elseif event == "PLAYER_LEAVING_WORLD" then
        PM.loadingWorld=true
    elseif event == "PLAYER_ENTERING_WORLD" then
        PM.loadingWorld=false; PM.rosterGraceUntil=time()+5; PM.currentOwner=nameFor("player"); PM.Capture()
    elseif event == "PLAYER_LOGOUT" then
        PM.loadingWorld=false; PM.rosterGraceUntil=nil; PM.Capture()
    else PM.Capture() end
    if PM.MaybeShowRecap then PM.MaybeShowRecap() end
end)
local elapsed = 0
frame:SetScript("OnUpdate", function(_, delta)
    elapsed = elapsed + delta
    if elapsed >= 15 then elapsed = 0; PM.Capture(); if PM.MaybeShowRecap then PM.MaybeShowRecap() end end
end)
SLASH_FAMILIARFACES1 = "/pm"
SLASH_FAMILIARFACES2 = "/partymemory"
SLASH_FAMILIARFACES3 = "/ff"
SLASH_FAMILIARFACES4 = "/familiarfaces"
SlashCmdList.FAMILIARFACES = function(input)
    if not PM.db then return end
    input = string.lower(input or "")
    if input == "pause" or input == "resume" then
        PM.db.enabled = input == "resume"
        PM.EndSession(time(),true)
        DEFAULT_CHAT_FRAME:AddMessage("Familiar Faces: recording " .. (PM.db.enabled and "enabled." or "paused."))
        PM.Capture()
    elseif input == "clear confirm" then
        local enabled,notices,first,minimap,placement=PM.db.enabled,PM.db.reunionNotices,PM.db.favouritesFirst,PM.db.minimap,PM.db.window
        local tooltips,tooltipNotes,recaps=PM.db.tooltips,PM.db.tooltipNotes,PM.db.recaps
        PM.EndSession(time())
        PM.pendingRecap=nil; if PM.HideRecap then PM.HideRecap() end
        FamiliarFacesDB = PM.Init({enabled = enabled,reunionNotices=notices,favouritesFirst=first,minimap=minimap,window=placement,
            tooltips=tooltips,tooltipNotes=tooltipNotes,recaps=recaps})
        if PM.Refresh then PM.Refresh() end
        DEFAULT_CHAT_FRAME:AddMessage("Familiar Faces: history, notes and favourites cleared.")
    elseif input == "clear" then
        DEFAULT_CHAT_FRAME:AddMessage("Familiar Faces: type /ff clear confirm to erase all saved history, notes and favourites.")
    elseif input == "minimap" then
        PM.db.minimap.hidden=not PM.db.minimap.hidden
        if PM.InitMinimap then PM.InitMinimap() end
        if PM.Refresh then PM.Refresh() end
    elseif input == "export" then
        if PM.ShowExport then PM.ShowExport() end
    elseif input == "settings" then
        if PM.ShowSettings then PM.ShowSettings() end
    elseif input == "reset window" then
        PM.db.window=nil; if PM.ResetWindow then PM.ResetWindow() end
    elseif input == "notices" then
        PM.db.reunionNotices=not PM.db.reunionNotices
        DEFAULT_CHAT_FRAME:AddMessage("Familiar Faces: reunion notices "..(PM.db.reunionNotices and "on." or "off."))
        if PM.Refresh then PM.Refresh() end
    else PM.Toggle() end
end
