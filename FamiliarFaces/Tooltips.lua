local PM=FamiliarFaces
local hooked=false
local function safe(value)
    return not issecretvalue or not issecretvalue(value)
end

function PM.TooltipLines(name)
    local person=PM.db and PM.db.people[name]
    if not person or not PM.db.tooltips then return end
    local lines={"Familiar Faces - We've met before",(person.encounters or 0).." recorded adventures together"}
    if person.favourite then lines[#lines+1]="A favourite companion" end
    local last=PM.LastAdventure(name)
    if last then lines[#lines+1]="Last: "..last.zone.." - "..date("%d %b %Y",last.lastSeen) end
    if PM.db.tooltipNotes and person.note and person.note:match("%S") then lines[#lines+1]="Private note: "..person.note end
    return lines
end

function PM.AddUnitTooltip(tooltip)
    if not PM.db or not PM.db.tooltips or tooltip~=GameTooltip then return end
    if tooltip.IsForbidden and tooltip:IsForbidden() then return end
    if InCombatLockdown and InCombatLockdown() then return end
    if not tooltip.GetUnit then return end
    local ok,_,unit=pcall(tooltip.GetUnit,tooltip)
    if not ok or not safe(unit) or type(unit)~="string" or unit=="" then return end
    if UnitIsPlayer then
        local player=UnitIsPlayer(unit)
        if not safe(player) or not player then return end
    end
    local name=PM.NameFor(unit)
    if not name or tooltip.familiarFacesName==name then return end
    local lines=PM.TooltipLines(name); if not lines then return end
    tooltip.familiarFacesName=name
    tooltip:AddLine(" ")
    for i,line in ipairs(lines) do
        tooltip:AddLine(line,i==1 and 0.91 or 0.85,i==1 and 0.74 or 0.91,i==1 and 0.45 or 0.88,true)
    end
end

function PM.InitTooltips()
    if hooked or not GameTooltip then return end
    local ok=false
    if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum and Enum.TooltipDataType then
        ok=pcall(TooltipDataProcessor.AddTooltipPostCall,Enum.TooltipDataType.Unit,PM.AddUnitTooltip)
    elseif GameTooltip.HookScript then
        ok=pcall(GameTooltip.HookScript,GameTooltip,"OnTooltipSetUnit",PM.AddUnitTooltip)
    end
    if ok then
        hooked=true
        GameTooltip:HookScript("OnTooltipCleared",function(self) self.familiarFacesName=nil end)
    end
end
