local PM = PartyMemory
local frame = CreateFrame("Frame")
local function safe(value)
    return value ~= nil and (not issecretvalue or not issecretvalue(value))
end
local function nameFor(unit)
    local name, realm = UnitName(unit)
    if not safe(name) or not safe(realm) then return end
    if not name or name == UNKNOWNOBJECT or name == "Unknown" then return end
    realm = realm and realm ~= "" and realm or GetRealmName()
    return name .. "-" .. (realm or "UnknownRealm"):gsub("%s", "")
end
function PM.Capture()
    if not PM.db then return end
    -- Retail can restrict unit information during combat. Retry after combat.
    if InCombatLockdown and InCombatLockdown() then return end
    local raid = IsInRaid and IsInRaid() or (GetNumRaidMembers and GetNumRaidMembers() > 0)
    local count = GetNumSubgroupMembers and GetNumSubgroupMembers() or (GetNumPartyMembers and GetNumPartyMembers() or 0)
    if raid or count == 0 then PM.active = nil; return end
    local members = {}
    for i = 1, count do
        local unit = "party" .. i
        local name = nameFor(unit)
        if not name then return end -- Wait for the complete roster rather than store Unknown players.
        local _, class = UnitClass(unit)
        local role = UnitGroupRolesAssigned and UnitGroupRolesAssigned(unit) or "NONE"
        members[#members + 1] = {name = name, class = safe(class) and class or nil, role = safe(role) and role or "NONE"}
    end
    local zone, instanceType, _, difficulty = GetInstanceInfo()
    if not safe(zone) or not safe(instanceType) or not safe(difficulty) then return end
    if instanceType == "pvp" or instanceType == "arena" or instanceType == "raid" then PM.active = nil; return end
    local owner = nameFor("player")
    if not owner then return end
    PM.Record(owner, members, { kind = instanceType == "party" and "Dungeon" or "Questing",
        zone = zone ~= "" and zone or GetZoneText() or "Unknown", difficulty = difficulty }, time())
    if PM.Refresh then PM.Refresh() end
end
frame:RegisterEvent("ADDON_LOADED")
for _, event in ipairs({"PLAYER_ENTERING_WORLD", "GROUP_ROSTER_UPDATE", "PARTY_MEMBERS_CHANGED",
    "ZONE_CHANGED_NEW_AREA", "ZONE_CHANGED", "PLAYER_REGEN_ENABLED", "PLAYER_LOGOUT"}) do
    pcall(frame.RegisterEvent, frame, event)
end
frame:SetScript("OnEvent", function(_, event, name)
    if event == "ADDON_LOADED" then
        if name == "PartyMemory" then PartyMemoryDB = PM.Init(PartyMemoryDB) end
    else PM.Capture() end
end)
local elapsed = 0
frame:SetScript("OnUpdate", function(_, delta)
    elapsed = elapsed + delta
    if elapsed >= 15 then elapsed = 0; PM.Capture() end
end)
SLASH_PARTYMEMORY1 = "/pm"
SLASH_PARTYMEMORY2 = "/partymemory"
SlashCmdList.PARTYMEMORY = function(input)
    if not PM.db then return end
    input = string.lower(input or "")
    if input == "pause" or input == "resume" then
        PM.db.enabled = input == "resume"
        PM.active = nil
        DEFAULT_CHAT_FRAME:AddMessage("Party Memory: recording " .. (PM.db.enabled and "enabled." or "paused."))
        PM.Capture()
    elseif input == "clear confirm" then
        PartyMemoryDB = PM.Init({enabled = PM.db.enabled})
        PM.active = nil
        if PM.Refresh then PM.Refresh() end
        DEFAULT_CHAT_FRAME:AddMessage("Party Memory: history, notes and favourites cleared.")
    elseif input == "clear" then
        DEFAULT_CHAT_FRAME:AddMessage("Party Memory: type /pm clear confirm to erase all saved history, notes and favourites.")
    else PM.Toggle() end
end
