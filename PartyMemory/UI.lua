local PM = PartyMemory
local window, search, detail, note, favourite, selected, listLabel
local page, filter, onlyFavourites = 1, nil, false
local rows, memberButtons = {}, {}
local function playerName(member)
    local person = PM.db.people[member.name]
    local class = member.class or (person and person.class)
    local colour = RAID_CLASS_COLORS and RAID_CLASS_COLORS[class]
    if not colour then return member.name end
    return string.format("|cff%02x%02x%02x%s|r",
        math.floor(colour.r * 255 + 0.5), math.floor(colour.g * 255 + 0.5),
        math.floor(colour.b * 255 + 0.5), member.name)
end
local function button(parent, text, x, y, width, action)
    local b = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
    b:SetSize(width, 24); b:SetPoint("TOPLEFT", x, y); b:SetText(text)
    b:SetScript("OnClick", action)
    return b
end
local function label(parent, text, x, y, width)
    local fs = parent:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    fs:SetPoint("TOPLEFT", x, y); fs:SetWidth(width); fs:SetJustifyH("LEFT"); fs:SetText(text)
    return fs
end
local function showPerson(member)
    selected = member
    local person = PM.db.people[member.name] or {}
    detail:SetText(playerName(member) .. "\n" .. (member.class or "Unknown class") .. " / " .. (member.role or "NONE")
        .. "\nSeen in " .. (person.encounters or 0) .. " recorded rosters")
    note:SetText(person.note or "")
    favourite:SetText(person.favourite and "Unfavourite" or "Favourite")
end
local function showSession(session)
    selected = nil
    detail:SetText(session.owner .. "\n" .. session.kind .. ": " .. session.zone .. "\n"
        .. date("%d %b %Y %H:%M", session.started) .. " - " .. date("%H:%M", session.lastSeen)
        .. "\n" .. (session.difficulty or ""))
    note:SetText("")
    for i, b in ipairs(memberButtons) do
        local member = session.members[i]
        if member then
            b:SetText(playerName(member)); b:SetScript("OnClick", function() showPerson(member) end); b:Show()
        else b:Hide() end
    end
end
function PM.Refresh()
    if not window or not window:IsShown() then return end
    local results = PM.Search(search:GetText(), filter, onlyFavourites)
    local pages = math.max(1, math.ceil(#results / 9))
    page = math.min(page, pages)
    listLabel:SetText(#results .. " groups | Page " .. page .. "/" .. pages .. (PM.db.enabled and " | Recording" or " | Paused"))
    for i, row in ipairs(rows) do
        local session = results[(page - 1) * 9 + i]
        if session then
            local names = {}
            for _, member in ipairs(session.members) do names[#names + 1] = playerName(member) end
            row.text:SetText(date("%d %b %Y %H:%M", session.started) .. " | " .. session.kind .. "\n"
                .. session.zone .. "\n" .. table.concat(names, ", "))
            row:SetScript("OnClick", function() showSession(session) end); row:Show()
        else row:Hide() end
    end
end
local function build()
    window = CreateFrame("Frame", "PartyMemoryWindow", UIParent)
    window:SetSize(860, 650); window:SetPoint("CENTER"); window:SetFrameStrata("DIALOG")
    local bg = window:CreateTexture(nil, "BACKGROUND"); bg:SetAllPoints(); bg:SetTexture("Interface\\Buttons\\WHITE8X8"); bg:SetVertexColor(0.035, 0.045, 0.065, 0.97)
    window:SetMovable(true); window:EnableMouse(true); window:RegisterForDrag("LeftButton")
    window:SetScript("OnDragStart", window.StartMoving); window:SetScript("OnDragStop", window.StopMovingOrSizing)
    window:SetClampedToScreen(true)
    table.insert(UISpecialFrames, "PartyMemoryWindow")
    label(window, "PARTY MEMORY", 20, -18, 700)
    label(window, "Remember the people you adventure with", 20, -42, 700)
    button(window, "Close", 775, -14, 65, function() window:Hide() end)
    search = CreateFrame("EditBox", nil, window, "InputBoxTemplate")
    search:SetSize(420, 26); search:SetPoint("TOPLEFT", 26, -80); search:SetAutoFocus(false)
    search:SetMaxLetters(100); search:SetScript("OnEscapePressed", search.ClearFocus)
    search:SetScript("OnTextChanged", function() page = 1; PM.Refresh() end)
    label(window, "Search names, notes, locations or characters", 20, -63, 460)
    button(window, "All", 20, -117, 65, function() filter = nil; page = 1; PM.Refresh() end)
    button(window, "Dungeons", 90, -117, 100, function() filter = "Dungeon"; page = 1; PM.Refresh() end)
    button(window, "Questing", 195, -117, 100, function() filter = "Questing"; page = 1; PM.Refresh() end)
    local favFilter
    favFilter = button(window, "Favourites: off", 300, -117, 145, function()
        onlyFavourites = not onlyFavourites; favFilter:SetText(onlyFavourites and "Favourites: on" or "Favourites: off"); page = 1; PM.Refresh()
    end)
    listLabel = label(window, "", 20, -150, 450)
    for i = 1, 9 do
        local row = CreateFrame("Button", nil, window)
        row:SetSize(450, 45); row:SetPoint("TOPLEFT", 20, -173 - (i - 1) * 47)
        row:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight")
        row.text = label(row, "", 3, -2, 440); row.text:SetFontObject("GameFontHighlightSmall")
        rows[i] = row
    end
    button(window, "Previous", 20, -605, 95, function() page = math.max(1, page - 1); PM.Refresh() end)
    button(window, "Next", 120, -605, 95, function()
        local total = #PM.Search(search:GetText(), filter, onlyFavourites)
        page = math.min(math.max(1, math.ceil(total / 9)), page + 1); PM.Refresh()
    end)
    label(window, "Select a group, then a player", 500, -80, 335)
    detail = label(window, "Your recorded groups appear on the left.\nHistory starts when this addon is installed.", 500, -110, 335)
    detail:SetFontObject("GameFontHighlight"); detail:SetHeight(90); detail:SetJustifyV("TOP")
    for i = 1, 4 do memberButtons[i] = button(window, "", 500, -210 - (i - 1) * 28, 330, function() end); memberButtons[i]:Hide() end
    label(window, "Player note (click Save note)", 500, -333, 335)
    note = CreateFrame("EditBox", nil, window, "InputBoxTemplate")
    note:SetSize(322, 28); note:SetPoint("TOPLEFT", 506, -359); note:SetAutoFocus(false); note:SetMaxLetters(300)
    note:SetScript("OnEscapePressed", note.ClearFocus)
    button(window, "Save note", 500, -398, 110, function()
        if selected then PM.db.people[selected.name].note = note:GetText(); note:ClearFocus(); PM.Refresh() end
    end)
    favourite = button(window, "Favourite", 615, -398, 125, function()
        if selected then local p = PM.db.people[selected.name]; p.favourite = not p.favourite; showPerson(selected); PM.Refresh() end
    end)
    button(window, "Whisper", 500, -431, 110, function()
        if selected then ChatFrame_SendTell(selected.name) end
    end)
    button(window, "Invite", 615, -431, 125, function()
        if selected and not (InCombatLockdown and InCombatLockdown()) then
            if C_PartyInfo and C_PartyInfo.InviteUnit then C_PartyInfo.InviteUnit(selected.name)
            elseif InviteUnit then InviteUnit(selected.name) end
        end
    end)
    label(window, "Outdoor groups are labelled Questing.\nEach roster or location change makes a new entry.\n\n/pm pause or /pm resume\n/pm clear then /pm clear confirm\n\nSaved locally. No chat messages collected.", 500, -485, 335)
    window:SetScript("OnShow", PM.Refresh)
    window:Hide()
end
function PM.Toggle()
    if not window then build() end
    if window:IsShown() then window:Hide() else window:Show(); PM.Refresh() end
end
