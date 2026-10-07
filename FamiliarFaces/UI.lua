local PM = FamiliarFaces
local window, search, panel, heading, summary, note, footer, empty, favourite, status, headerStatus
local view, page, linkPage, locationPage = "Adventures", 1, 1, 1
local options = {sort = "started"}
local selectedSession, selectedPerson
local rows, headers, links, actions = {}, {}, {}, {}
local activityButton, classButton, favouritesButton, notesButton, tabs = nil, nil, nil, nil, {}
local classes = {}
local refreshDetails, layout
local creatorDialog, creatorURL
local pendingForget, forgetDialog, forgetMessage, forgetButton, firstButton, noticesButton
local nickname, draftDialog, pendingNavigation, allowHide, daysButton, partyButton, minimapToggle
local function showCreator()
    if not creatorDialog then
        creatorDialog=CreateFrame("Frame",nil,window); creatorDialog:SetSize(620,140); creatorDialog:SetPoint("CENTER"); creatorDialog:EnableMouse(true)
        local bg=creatorDialog:CreateTexture(nil,"BACKGROUND"); bg:SetAllPoints(); bg:SetTexture("Interface\\Buttons\\WHITE8X8"); bg:SetVertexColor(0.025,0.065,0.085,1)
        local title=creatorDialog:CreateFontString(nil,"OVERLAY","GameFontNormal"); title:SetPoint("TOPLEFT",20,-20); title:SetText("More addons by SqueezyLemons")
        creatorURL=CreateFrame("EditBox",nil,creatorDialog,"InputBoxTemplate"); creatorURL:SetSize(565,28); creatorURL:SetPoint("TOPLEFT",28,-55); creatorURL:SetAutoFocus(false)
        creatorURL:SetScript("OnEscapePressed",function() creatorDialog:Hide() end)
        local hint=creatorDialog:CreateFontString(nil,"OVERLAY","GameFontHighlightSmall"); hint:SetPoint("TOPLEFT",20,-105); hint:SetText("Press Ctrl+C to copy, then paste into your browser. Escape to close.")
        local close=CreateFrame("Button",nil,creatorDialog,"UIPanelButtonTemplate"); close:SetSize(65,24); close:SetPoint("TOPRIGHT",-15,-14); close:SetText("Close"); close:SetScript("OnClick",function() creatorDialog:Hide() end)
        creatorDialog:SetScript("OnHide",function() creatorURL:ClearFocus() end)
    end
    creatorURL:SetText("https://www.curseforge.com/members/squeezylemons/projects"); creatorDialog:Show(); creatorURL:SetFocus(); creatorURL:HighlightText()
end
local function colourName(person)
    local saved = PM.db.people[person.name]
    local class = person.class or (saved and saved.class)
    local c = RAID_CLASS_COLORS and RAID_CLASS_COLORS[class]
    if not c then return person.name end
    return string.format("|cff%02x%02x%02x%s|r", math.floor(c.r*255+0.5), math.floor(c.g*255+0.5), math.floor(c.b*255+0.5), person.name)
end
local function fill(parent, r, g, b, a)
    local t = parent:CreateTexture(nil, "BACKGROUND")
    t:SetAllPoints(); t:SetTexture("Interface\\Buttons\\WHITE8X8"); t:SetVertexColor(r,g,b,a or 1)
    return t
end
local function border(parent)
    for _,edge in ipairs({"TOP","BOTTOM","LEFT","RIGHT"}) do
        local t=parent:CreateTexture(nil,"BORDER")
        t:SetTexture("Interface\\Buttons\\WHITE8X8"); t:SetVertexColor(0.64,0.46,0.22,0.7)
        if edge=="TOP" or edge=="BOTTOM" then
            t:SetHeight(1); t:SetPoint(edge.."LEFT",0,0); t:SetPoint(edge.."RIGHT",0,0)
        else
            t:SetWidth(1); t:SetPoint("TOP"..edge,0,0); t:SetPoint("BOTTOM"..edge,0,0)
        end
    end
end
local function art(parent,path,x,y,width,height)
    local t=parent:CreateTexture(nil,"ARTWORK")
    t:SetPoint("TOPLEFT",x,y); t:SetSize(width,height); t:SetTexture(path)
    return t
end
local function label(parent, text, x, y, width, font)
    local f = parent:CreateFontString(nil,"OVERLAY",font or "GameFontHighlightSmall")
    f:SetPoint("TOPLEFT",x,y); f:SetWidth(width); f:SetJustifyH("LEFT"); f:SetText(text)
    return f
end
local function button(parent,text,x,y,width,fn)
    local b = CreateFrame("Button",nil,parent)
    b:SetSize(width,26); b:SetPoint("TOPLEFT",x,y)
    b.bg = fill(b,0.075,0.16,0.19); border(b)
    b.textLabel = label(b,text,8,-7,width-16,"GameFontHighlightSmall")
    b:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight")
    b.SetText = function(self,t) self.textLabel:SetText(t); self.caption=t end
    b:SetText(text); b:SetScript("OnClick",fn)
    return b
end
local function dirty()
    return selectedPerson and (note:GetText()~=(selectedPerson.note or "") or nickname:GetText()~=(selectedPerson.nickname or ""))
end
local function saveDraft()
    if selectedPerson then selectedPerson.note=note:GetText(); selectedPerson.nickname=nickname:GetText(); note:ClearFocus(); nickname:ClearFocus() end
end
local function guard(fn)
    if not dirty() then fn(); return end
    if pendingNavigation then return end
    pendingNavigation=fn
    if not draftDialog then
        draftDialog=CreateFrame("Frame",nil,window); draftDialog:SetSize(540,150); draftDialog:SetPoint("CENTER"); draftDialog:EnableMouse(true); draftDialog:SetFrameStrata("FULLSCREEN_DIALOG")
        fill(draftDialog,0.025,0.065,0.085); border(draftDialog)
        label(draftDialog,"You have unsaved notes or a nickname.\nSave your changes before moving on?",20,-25,500,"GameFontHighlight")
        local function finish(save,discard)
            if save then saveDraft() elseif discard and selectedPerson then note:SetText(selectedPerson.note or ""); nickname:SetText(selectedPerson.nickname or "") end
            local nextAction=pendingNavigation; pendingNavigation=nil; draftDialog:Hide()
            if nextAction then nextAction() end
        end
        button(draftDialog,"Save",20,-105,150,function() finish(true) end)
        button(draftDialog,"Discard",190,-105,150,function() finish(false,true) end)
        button(draftDialog,"Cancel",360,-105,150,function() pendingNavigation=nil; draftDialog:Hide() end)
    end
    draftDialog:Show()
end
function PM.SaveWindow()
    if not window then return end
    local placement={width=window:GetWidth(),height=window:GetHeight()}
    if window.GetCenter and UIParent.GetCenter then
        local x,y=window:GetCenter(); local cx,cy=UIParent:GetCenter()
        if x and y and cx and cy then placement.x=x-cx; placement.y=y-cy end
    end
    PM.db.window=placement
end
function PM.ResetWindow()
    if window then window:ClearAllPoints(); window:SetPoint("CENTER"); window:SetSize(1120,880); PM.SaveWindow() end
end
function PM.Close()
    guard(function() allowHide=true; PM.SaveWindow(); window:Hide(); allowHide=false end)
end
local function askForget()
    pendingForget=selectedPerson and {person=selectedPerson.name} or (selectedSession and {session=selectedSession})
    if not pendingForget then return end
    if not forgetDialog then
        forgetDialog=CreateFrame("Frame",nil,window); forgetDialog:SetSize(600,180); forgetDialog:SetPoint("CENTER"); forgetDialog:EnableMouse(true)
        forgetDialog:SetFrameStrata("FULLSCREEN_DIALOG")
        fill(forgetDialog,0.025,0.065,0.085); border(forgetDialog)
        forgetMessage=label(forgetDialog,"",20,-20,560,"GameFontHighlight"); forgetMessage:SetHeight(100)
        button(forgetDialog,"Cancel",20,-135,160,function() forgetDialog:Hide(); pendingForget=nil end)
        button(forgetDialog,"Confirm forget",390,-135,190,function()
            if pendingForget then
                if pendingForget.person then PM.ForgetPerson(pendingForget.person) else PM.ForgetAdventure(pendingForget.session) end
            end
            pendingForget=nil; selectedPerson=nil; selectedSession=nil; note:SetText(""); forgetDialog:Hide(); PM.Refresh()
        end)
    end
    forgetMessage:SetText(pendingForget.person and ("Forget "..pendingForget.person.."?\nRemoves their notes, favourite and appearances in your history.\nOther companions are kept. They can be recorded in a future party.")
        or "Forget this adventure?\nRemoves this entry and updates encounter counts.\nCompanion notes and favourites are kept.\nAn active party will not be recorded again until it ends.")
    forgetDialog:Show()
end
local adventureColumns = {{"Date","started",0},{"Activity","kind",0.22},{"Adventure","zone",0.39},{"People","members",0.76},{"Time","duration",0.88}}
local companionColumns = {{"Companion","name",0},{"Class","class",0.32},{"Together","encounters",0.46},{"Last adventure","adventure",0.59},{"Last seen","lastSeen",0.83}}
local function columns() return view=="Adventures" and adventureColumns or companionColumns end
local function duration(session)
    local minutes = math.floor(math.max(0,(session.ended or session.lastSeen)-session.started)/60)
    return minutes < 60 and (minutes.."m") or (math.floor(minutes/60).."h "..(minutes%60).."m")
end
local function selectSession(session)
    guard(function()
        selectedSession=session; selectedPerson=nil; linkPage=1; locationPage=1
        note:SetText(""); nickname:SetText(""); PM.Refresh()
    end)
end
local function selectPerson(person)
    if selectedPerson==person then return end
    guard(function()
        selectedPerson=person; selectedSession=nil; linkPage=1
        note:SetText(person.note or ""); nickname:SetText(person.nickname or ""); PM.Refresh()
    end)
end
local function related()
    if selectedPerson then
        local list={}
        for _,s in ipairs(PM.db.sessions) do
            for _,m in ipairs(s.members) do if m.name==selectedPerson.name then list[#list+1]=s; break end end
        end
        return list,"Shared adventures"
    end
    return selectedSession and selectedSession.members or {},"Companions"
end
refreshDetails = function()
    if selectedPerson and not PM.db.people[selectedPerson.name] then selectedPerson=nil; selectedSession=nil; note:SetText("") end
    if selectedSession then
        local valid=false
        for _,s in ipairs(PM.db.sessions) do if s==selectedSession then valid=true; break end end
        if not valid then selectedSession=nil; selectedPerson=nil; note:SetText("") end
    end
    if selectedPerson then
        heading:SetText(colourName(selectedPerson))
        local last=PM.LastAdventure(selectedPerson.name)
        summary:SetText((selectedPerson.class or "Unknown class").."\n"..(selectedPerson.encounters or 0).." shared entries\nLast adventure: "..(last and last.zone or "No saved adventures").."\nLast together: "..(selectedPerson.lastSeen and date("%d %b %Y %H:%M",selectedPerson.lastSeen) or "Unknown"))
    elseif selectedSession then
        heading:SetText(selectedSession.zone)
        summary:SetText(selectedSession.kind.." | "..(selectedSession.difficulty or "").."\n"..date("%d %b %Y %H:%M",selectedSession.started).." | "..duration(selectedSession).."\n"..selectedSession.owner)
    else
        heading:SetText("Your adventure journal")
        summary:SetText("Select an adventure or companion.\n\nNew parties appear automatically.\nYour notes and favourites stay local.")
    end
    for _,b in ipairs(actions) do if selectedPerson then b:Show() else b:Hide() end end
    if selectedPerson or selectedSession then forgetButton:Show() else forgetButton:Hide() end
    forgetButton:SetText(selectedPerson and "Forget companion" or "Forget adventure")
    if selectedPerson then note:Show(); nickname:Show(); panel.nicknameLabel:Show(); panel.noteLabel:Show() else note:Hide(); nickname:Hide(); panel.nicknameLabel:Hide(); panel.noteLabel:Hide() end
    panel.noteLabel:SetText(dirty() and "Personal note - unsaved changes" or "A little note for next time")
    for _,b in ipairs({panel.previousLinks,panel.nextLinks}) do
        if selectedPerson or selectedSession then b:Show() else b:Hide() end
    end
    for _,item in ipairs({panel.timeline,panel.previousLocations,panel.nextLocations}) do
        if selectedSession then item:Show() else item:Hide() end
    end
    if selectedPerson or selectedSession then panel.welcomeArt:Hide(); panel.welcomeText:Hide()
    else panel.welcomeArt:Show(); panel.welcomeText:Show() end
    favourite:SetText(selectedPerson and selectedPerson.favourite and "Unfavourite" or "Favourite")
    local list,title=related()
    local pages=math.max(1,math.ceil(#list/5)); linkPage=math.min(linkPage,pages)
    panel.linkTitle:SetText((selectedSession or selectedPerson) and (title.." | "..linkPage.."/"..pages) or "")
    panel.previousLinks:SetText(selectedPerson and "Previous adventures" or "Previous players")
    panel.nextLinks:SetText(selectedPerson and "More adventures" or "More players")
    for i,b in ipairs(links) do
        local entry=list[(linkPage-1)*5+i]
        if entry then
            if selectedPerson then
                b:SetText(date("%d %b",entry.started).."  "..entry.zone)
                b:SetScript("OnClick",function() guard(function() view="Adventures"; options.sort="started"; page=1; selectSession(entry) end) end)
            else
                b:SetText(colourName(entry)..(entry.left and " (left)" or ""))
                b:SetScript("OnClick",function() selectPerson(PM.db.people[entry.name] or entry) end)
            end
            b:Show()
        else b:Hide() end
    end
    local locations=selectedSession and selectedSession.locations or {}
    local pagesLocation=math.max(1,math.ceil(#locations/3)); locationPage=math.min(locationPage,pagesLocation)
    local lines={"Location timeline | "..locationPage.."/"..pagesLocation}
    for i=(locationPage-1)*3+1,math.min(locationPage*3,#locations) do
        local loc=locations[i]; lines[#lines+1]=date("%H:%M",loc.started).."  "..loc.zone
    end
    if #locations==0 then lines[#lines+1]=selectedSession and selectedSession.zone or "Choose an adventure to see its route." end
    panel.timeline:SetText(table.concat(lines,"\n"))
end
local function visibleRows() return math.max(1,math.min(16,math.floor((window:GetHeight()-339)/30))) end
function PM.Refresh()
    if not window or not window:IsShown() then return end
    options.query=search:GetText()
    options.favouritesFirst=PM.db.favouritesFirst
    daysButton:SetText("When: "..(options.days and ("Last "..options.days.." days") or "Any time"))
    partyButton:SetText(options.currentParty and "In your party: on" or "In your party: off")
    minimapToggle:SetText("Minimap: "..(PM.db.minimap.hidden and "off" or "on"))
    firstButton:SetText("Favourites first: "..(PM.db.favouritesFirst and "on" or "off"))
    noticesButton:SetText("Reunion notices: "..(PM.db.reunionNotices and "on" or "off"))
    local results=PM.Query(view,options)
    local count=visibleRows(); local pages=math.max(1,math.ceil(#results/count)); page=math.min(page,pages)
    for name,b in pairs(tabs) do
        b.bg:SetVertexColor(name==view and 0.68 or 0.075,name==view and 0.46 or 0.16,name==view and 0.19 or 0.19,1)
        b.textLabel:SetTextColor(name==view and 0.06 or 1,name==view and 0.10 or 0.94,name==view and 0.12 or 0.81)
    end
    local cols=columns(); local tableWidth=window:GetWidth()-400
    for i,h in ipairs(headers) do
        local c=cols[i]; h:SetText(c[1]..(options.sort==c[2] and (options.ascending and " +" or " -") or ""))
        h:ClearAllPoints(); h:SetPoint("TOPLEFT",20+tableWidth*c[3],-274)
        h:SetWidth(tableWidth*((cols[i+1] and cols[i+1][3] or 1)-c[3]))
    end
    for i,row in ipairs(rows) do
        local item=i<=count and results[(page-1)*count+i]
        if item then
            row.entry=item
            local selected=view=="Adventures" and item==selectedSession or view=="Companions" and item==selectedPerson
            row.bg:SetVertexColor(selected and 0.16 or (i%2==0 and 0.065 or 0.045),selected and 0.27 or 0.11,selected and 0.19 or 0.14,1)
            row.marker:SetVertexColor(selected and 0.90 or 0.45,selected and 0.69 or 0.36,selected and 0.31 or 0.23,1)
            row.icon:SetTexture(view=="Companions" and "Interface\\Icons\\INV_Misc_GroupLooking"
                or (item.kind=="Dungeon" and "Interface\\Icons\\INV_Misc_Key_03" or "Interface\\Icons\\INV_Misc_Map_01"))
            local cells
            if view=="Adventures" then cells={date("%d %b %H:%M",item.started),item.kind,item.zone,tostring(#item.members),duration(item)}
            else local last=PM.LastAdventure(item.name)
                cells={colourName(item)..(item.favourite and " |cffe8bd72*|r" or "")..(PM.currentParty and PM.currentParty[item.name] and " |cff70cc97[party]|r" or ""),item.class or "Unknown",tostring(item.encounters or 0),last and last.zone or "-",item.lastSeen and date("%d %b %H:%M",item.lastSeen) or "-"} end
            for j,f in ipairs(row.cells) do
                f:ClearAllPoints(); f:SetPoint("TOPLEFT",(j==1 and 29 or 8)+tableWidth*cols[j][3],-9)
                f:SetWidth(math.max(20,tableWidth*((cols[j+1] and cols[j+1][3] or 1)-cols[j][3])-(j==1 and 33 or 12))); f:SetText(cells[j])
            end
            row:SetScript("OnClick",function() if view=="Adventures" then selectSession(item) else selectPerson(item) end end)
            row:SetScript("OnEnter",function()
                if not GameTooltip then return end
                GameTooltip:SetOwner(row,"ANCHOR_RIGHT")
                if view=="Companions" then
                    GameTooltip:SetText(item.name); GameTooltip:AddLine(item.note or "No personal note",1,1,1,true)
                    if item.nickname and item.nickname~="" then GameTooltip:AddLine("Nickname: "..item.nickname,1,1,1,true) end
                    if PM.currentParty and PM.currentParty[item.name] then GameTooltip:AddLine("In your party",0.44,0.80,0.59) end
                    local last=PM.LastAdventure(item.name)
                    if last then GameTooltip:AddLine("Last adventure: "..last.zone.." | "..date("%d %b %Y %H:%M",last.lastSeen),1,1,1,true) end
                else
                    GameTooltip:SetText(item.zone)
                    for _,member in ipairs(item.members) do GameTooltip:AddLine(colourName(member)) end
                end
                GameTooltip:Show()
            end)
            row:SetScript("OnLeave",function() if GameTooltip then GameTooltip:Hide() end end)
            row:Show()
        else row.entry=nil; row:Hide() end
    end
    empty:SetText(#results==0 and (#PM.db.sessions==0 and "Your next party starts the story.\nJoin a group to remember your first companions." or "No matches. Try clearing your filters.") or "")
    local totalPeople,totalFavourites=0,0
    for _,p in pairs(PM.db.people) do totalPeople=totalPeople+1; if p.favourite then totalFavourites=totalFavourites+1 end end
    footer:SetText(#PM.db.sessions.." adventures  |  "..totalPeople.." companions  |  "..totalFavourites.." favourites")
    headerStatus:SetText(PM.db.enabled and "|cff70cc97Your journal is open|r" or "|cffe8bd72Taking a little break|r")
    status:SetText(#results.." shown | Page "..page.."/"..pages..(PM.db.enabled and " | Recording" or " | Paused"))
    refreshDetails()
end
local function build()
    window=CreateFrame("Frame","FamiliarFacesWindow",UIParent)
    local placement=PM.db.window or {}
    window:SetSize(math.max(1100,math.min(1500,placement.width or 1120)),math.max(880,math.min(1100,placement.height or 880)))
    if placement.x and placement.y then window:SetPoint("CENTER",UIParent,"CENTER",placement.x,placement.y) else window:SetPoint("CENTER") end
    window:SetFrameStrata("DIALOG")
    fill(window,0.025,0.065,0.085,0.99); border(window)
    window:SetMovable(true); window:EnableMouse(true); window:RegisterForDrag("LeftButton")
    window:SetScript("OnDragStart",window.StartMoving); window:SetScript("OnDragStop",function() window:StopMovingOrSizing(); PM.SaveWindow() end)
    window:SetClampedToScreen(true); window:SetResizable(true)
    if window.SetResizeBounds then window:SetResizeBounds(1100,880,1500,1100)
    elseif window.SetMinResize then window:SetMinResize(1100,880); window:SetMaxResize(1500,1100) end
    table.insert(UISpecialFrames,"FamiliarFacesWindow")
    local emblem=CreateFrame("Frame",nil,window); emblem:SetSize(74,74); emblem:SetPoint("TOPLEFT",24,-24)
    fill(emblem,0.13,0.20,0.21); border(emblem)
    art(emblem,"Interface\\Icons\\INV_Misc_Book_09",8,-8,58,58)
    art(window,"Interface\\AddOns\\FamiliarFaces\\Textures\\Wordmark.tga",114,-17,430,86)
    label(window,"Remember the people you adventure with.",117,-103,500)
    headerStatus=label(window,"",770,-65,300,"GameFontNormal")
    button(window,"Created by SqueezyLemons",770,-89,300,showCreator)
    firstButton=button(window,"",310,-122,195,function() PM.db.favouritesFirst=not PM.db.favouritesFirst; page=1; PM.Refresh() end)
    noticesButton=button(window,"",515,-122,195,function() PM.db.reunionNotices=not PM.db.reunionNotices; PM.Refresh() end)
    local close=button(window,"Close",0,0,70,PM.Close)
    close:ClearAllPoints(); close:SetPoint("TOPRIGHT",-20,-20)
    for i,name in ipairs({"Adventures","Companions"}) do
        tabs[name]=button(window,name,20+(i-1)*145,-122,135,function()
            view=name; page=1; options.sort=name=="Adventures" and "started" or "lastSeen"; options.ascending=false; PM.Refresh()
        end)
    end
    search=CreateFrame("EditBox",nil,window,"InputBoxTemplate")
    search:SetSize(330,26); search:SetPoint("TOPLEFT",26,-166); search:SetAutoFocus(false); search:SetMaxLetters(100)
    search:SetScript("OnEscapePressed",search.ClearFocus)
    search:SetScript("OnTextChanged",function() page=1; PM.Refresh() end)
    label(window,"Find a familiar face or favourite place",375,-174,350)
    activityButton=button(window,"Activity: All",20,-202,145,function()
        options.kind=options.kind==nil and "Dungeon" or (options.kind=="Dungeon" and "Questing" or nil)
        activityButton:SetText("Activity: "..(options.kind or "All")); page=1; PM.Refresh()
    end)
    classButton=button(window,"Class: All",172,-202,150,function()
        classes={}; local unique={}
        for _,p in pairs(PM.db.people) do if p.class then unique[p.class]=true end end
        for c in pairs(unique) do classes[#classes+1]=c end; table.sort(classes)
        local index=0; for i,c in ipairs(classes) do if c==options.class then index=i end end
        options.class=classes[index+1]; classButton:SetText("Class: "..(options.class or "All")); page=1; PM.Refresh()
    end)
    favouritesButton=button(window,"Favourites: off",329,-202,140,function()
        options.favourites=not options.favourites; favouritesButton:SetText(options.favourites and "Favourites: on" or "Favourites: off"); page=1; PM.Refresh()
    end)
    notesButton=button(window,"Notes: off",476,-202,105,function()
        options.notes=not options.notes; notesButton:SetText(options.notes and "Notes: on" or "Notes: off"); page=1; PM.Refresh()
    end)
    button(window,"Clear filters",588,-202,125,function()
        options.kind=nil; options.class=nil; options.favourites=false; options.notes=false; options.days=nil; options.currentParty=false; page=1
        activityButton:SetText("Activity: All"); classButton:SetText("Class: All"); favouritesButton:SetText("Favourites: off"); notesButton:SetText("Notes: off"); search:SetText(""); PM.Refresh()
    end)
    daysButton=button(window,"",20,-238,190,function() options.days=options.days==nil and 7 or (options.days==7 and 30 or nil); page=1; PM.Refresh() end)
    partyButton=button(window,"",220,-238,190,function() options.currentParty=not options.currentParty; page=1; PM.Refresh() end)
    minimapToggle=button(window,"",420,-238,145,function() PM.db.minimap.hidden=not PM.db.minimap.hidden; PM.InitMinimap(); PM.Refresh() end)
    for i=1,5 do headers[i]=button(window,"",0,-194,100,function()
        local key=columns()[i][2]
        if options.sort==key then options.ascending=not options.ascending else options.sort=key; options.ascending=key=="name" or key=="zone" or key=="class" end
        page=1; PM.Refresh()
    end) end
    for i=1,16 do
        local row=CreateFrame("Button",nil,window); row:SetSize(720,30); row:SetPoint("TOPLEFT",20,-306-(i-1)*30)
        row.bg=fill(row,0.10,0.11,0.13); row:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight")
        row.marker=art(row,"Interface\\Buttons\\WHITE8X8",0,0,2,30)
        row.icon=art(row,"Interface\\Icons\\INV_Misc_Map_01",7,-7,16,16)
        row.cells={}; for j=1,5 do row.cells[j]=label(row,"",0,-9,100) end
        row.text=row.cells[1]; rows[i]=row
    end
    empty=label(window,"",40,-350,640,"GameFontHighlight")
    local prev=button(window,"Previous",0,0,95,function() page=math.max(1,page-1); PM.Refresh() end)
    prev:ClearAllPoints(); prev:SetPoint("BOTTOMLEFT",20,49)
    local nextButton=button(window,"Next",0,0,95,function()
        local maxPage=math.max(1,math.ceil(#PM.Query(view,options)/visibleRows())); page=math.min(maxPage,page+1); PM.Refresh()
    end)
    nextButton:ClearAllPoints(); nextButton:SetPoint("BOTTOMLEFT",122,49)
    status=label(window,"",230,0,470); status:ClearAllPoints(); status:SetPoint("BOTTOMLEFT",230,57)
    footer=label(window,"",20,0,850); footer:ClearAllPoints(); footer:SetPoint("BOTTOMLEFT",20,23)
    panel=CreateFrame("Frame",nil,window); panel:SetSize(340,704); panel:SetPoint("TOPRIGHT",-20,-154); fill(panel,0.035,0.09,0.11); border(panel)
    heading=label(panel,"",14,-15,310,"GameFontNormalLarge")
    summary=label(panel,"",14,-48,310); summary:SetHeight(75); summary:SetJustifyV("TOP")
    panel.linkTitle=label(panel,"",14,-132,310,"GameFontNormal")
    for i=1,5 do links[i]=button(panel,"",14,-156-(i-1)*29,312,function() end) end
    panel.previousLinks=button(panel,"Previous players",14,-305,150,function() linkPage=math.max(1,linkPage-1); refreshDetails() end)
    panel.nextLinks=button(panel,"More players",170,-305,156,function() local list=related(); linkPage=math.min(math.max(1,math.ceil(#list/5)),linkPage+1); refreshDetails() end)
    panel.noteLabel=label(panel,"A little note for next time",14,-349,300,"GameFontNormal")
    panel.welcomeArt=art(panel,"Interface\\Icons\\INV_Misc_Book_09",122,-185,96,96)
    panel.welcomeText=label(panel,"The healer who saved the run.\nThe tank who showed the way.\nThe friend who made it fun.\n\nKeep their story here.",30,-325,280,"GameFontHighlight")
    note=CreateFrame("EditBox",nil,panel,"InputBoxTemplate"); note:SetSize(302,26); note:SetPoint("TOPLEFT",20,-373); note:SetAutoFocus(false); note:SetMaxLetters(300); note:SetScript("OnEscapePressed",note.ClearFocus)
    panel.nicknameLabel=label(panel,"Private nickname",14,-515,300,"GameFontNormal")
    nickname=CreateFrame("EditBox",nil,panel,"InputBoxTemplate"); nickname:SetSize(302,26); nickname:SetPoint("TOPLEFT",20,-539); nickname:SetAutoFocus(false); nickname:SetMaxLetters(60); nickname:SetScript("OnEscapePressed",nickname.ClearFocus)
    local function draftChanged() if selectedPerson then panel.noteLabel:SetText(dirty() and "Personal note - unsaved changes" or "A little note for next time") end end
    note:SetScript("OnTextChanged",draftChanged); nickname:SetScript("OnTextChanged",draftChanged)
    actions[1]=button(panel,"Save note",14,-410,150,function()
        saveDraft(); PM.Refresh()
    end)
    actions[1].bg:SetVertexColor(0.72,0.49,0.20,1); actions[1].textLabel:SetTextColor(0.06,0.10,0.12)
    favourite=button(panel,"Favourite",170,-410,156,function()
        if selectedPerson then selectedPerson.favourite=not selectedPerson.favourite; PM.Refresh() end
    end); actions[2]=favourite
    actions[3]=button(panel,"Whisper",14,-442,150,function() if selectedPerson then ChatFrame_SendTell(selectedPerson.name) end end)
    actions[4]=button(panel,"Invite",170,-442,156,function()
        if selectedPerson and not (InCombatLockdown and InCombatLockdown()) then
            if C_PartyInfo and C_PartyInfo.InviteUnit then C_PartyInfo.InviteUnit(selectedPerson.name) elseif InviteUnit then InviteUnit(selectedPerson.name) end
        end
    end)
    for i,text in ipairs({"Helpful","Patient","Great company"}) do
        actions[#actions+1]=button(panel,text,14+(i-1)*105,-478,100,function()
            if selectedPerson then
                local current=note:GetText()
                if not string.find(current,text,1,true) then note:SetText((current:match("%S") and current.."; " or "")..text) end
            end
        end)
    end
    forgetButton=button(panel,"Forget adventure",14,-663,312,function() guard(askForget) end)
    panel.timeline=label(panel,"",14,-577,310); panel.timeline:SetHeight(60); panel.timeline:SetJustifyV("TOP")
    panel.previousLocations=button(panel,"Previous locations",14,-640,150,function() locationPage=math.max(1,locationPage-1); refreshDetails() end)
    panel.nextLocations=button(panel,"More locations",170,-640,156,function() locationPage=locationPage+1; refreshDetails() end)
    local resize=button(window,"Resize",0,0,65,function() end); resize:ClearAllPoints(); resize:SetPoint("BOTTOMRIGHT",-10,10)
    resize:SetScript("OnMouseDown",function() window:StartSizing("BOTTOMRIGHT") end)
    resize:SetScript("OnMouseUp",function() window:StopMovingOrSizing(); PM.SaveWindow() end)
    layout=function()
        local width=window:GetWidth()-400
        for _,row in ipairs(rows) do row:SetWidth(width) end
        PM.Refresh()
    end
    window:SetScript("OnSizeChanged",layout); window:SetScript("OnShow",layout); window:Hide()
    window:SetScript("OnHide",function()
        if dirty() and not allowHide then window:Show(); PM.Close(); return end
        if forgetDialog then forgetDialog:Hide() end; pendingForget=nil
    end)
end
function PM.Toggle()
    if not window then build() end
    if window:IsShown() then PM.Close() else window:Show() end
end

local minimapButton
function PM.InitMinimap()
    if not Minimap or not PM.db then return end
    local settings=PM.db.minimap
    if not minimapButton then
        minimapButton=CreateFrame("Button","FamiliarFacesMinimapButton",Minimap)
        minimapButton:SetSize(30,30); minimapButton:SetFrameStrata("MEDIUM"); minimapButton:EnableMouse(true)
        fill(minimapButton,0.035,0.09,0.11); border(minimapButton)
        art(minimapButton,"Interface\\Icons\\INV_Misc_Book_09",3,-3,24,24)
        minimapButton:RegisterForDrag("LeftButton")
        minimapButton:SetScript("OnClick",PM.Toggle)
        local function position()
            local radians=math.rad(PM.db.minimap.angle or 220)
            minimapButton:ClearAllPoints()
            minimapButton:SetPoint("CENTER",Minimap,"CENTER",math.cos(radians)*80,math.sin(radians)*80)
        end
        minimapButton.position=position
        minimapButton:SetScript("OnDragStart",function(self)
            self:SetScript("OnUpdate",function()
                local x,y=GetCursorPosition(); local cx,cy=Minimap:GetCenter(); local scale=Minimap:GetEffectiveScale()
                if cx and cy then PM.db.minimap.angle=math.deg(math.atan2(y/scale-cy,x/scale-cx)); position() end
            end)
        end)
        minimapButton:SetScript("OnDragStop",function(self) self:SetScript("OnUpdate",nil) end)
        minimapButton:SetScript("OnEnter",function(self)
            if GameTooltip then GameTooltip:SetOwner(self,"ANCHOR_LEFT"); GameTooltip:SetText("Familiar Faces"); GameTooltip:AddLine("Click to open your journal. Drag to move.\nHide with /ff minimap.",1,1,1,true); GameTooltip:Show() end
        end)
        minimapButton:SetScript("OnLeave",function() if GameTooltip then GameTooltip:Hide() end end)
    end
    minimapButton.position()
    if settings.hidden then minimapButton:Hide() else minimapButton:Show() end
end
