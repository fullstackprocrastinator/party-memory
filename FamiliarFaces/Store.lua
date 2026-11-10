FamiliarFaces = FamiliarFaces or {}
local PM = FamiliarFaces

PM.TagChoices={"Helpful guide","Quest buddy","Run again"}
PM.ResumeWindow=300
PM.RoleNames={TANK="Tank",HEALER="Healer",DAMAGER="Damage",NONE="Unknown"}
function PM.Role(role) return PM.RoleNames[role] and role or "NONE" end
function PM.InvalidateHistory() PM.historyIndex=nil end
function PM.HistoryIndex()
    if PM.historyIndex then return PM.historyIndex end
    local index={people={},sessions={},latest=nil}
    for _,s in ipairs(PM.db.sessions) do
        index.sessions[s]=true
        if not index.latest or s.started>index.latest.started then index.latest=s end
        local seen={}
        for _,m in ipairs(s.members) do
            local p=index.people[m.name]
            if not p then p={adventures={},count=0}; index.people[m.name]=p end
            if not seen[m.name] then p.count=p.count+1; p.adventures[#p.adventures+1]=s; seen[m.name]=true end
            if not p.first or s.started<p.first.started then p.first=s end
            if not p.last or s.lastSeen>p.last.lastSeen then p.last=s end
            local at=m.lastSeen or s.lastSeen
            if not p.roleAt or at>p.roleAt or (at==p.roleAt and s.started>(p.roleStarted or 0)) then
                p.roleAt=at; p.roleStarted=s.started; p.role=PM.Role(m.role); p.class=m.class or p.class
            end
            p.firstSeen=math.min(p.firstSeen or s.started,m.joined or s.started)
            p.lastSeen=math.max(p.lastSeen or 0,at)
        end
    end
    PM.historyIndex=index; return index
end
function PM.LastRole(name)
    local p=PM.HistoryIndex().people[name]; return p and p.role or "NONE"
end
function PM.SharedAdventures(name)
    local p=PM.HistoryIndex().people[name]; return p and p.adventures or {}
end
function PM.TextLength(text)
    local _,count=(text or ""):gsub("[^\128-\191]",""); return count
end
function PM.LimitText(text,limit)
    local count=0
    for i=1,#text do
        local byte=text:byte(i)
        if byte<128 or byte>=192 then count=count+1; if count>limit then return text:sub(1,i-1) end end
    end
    return text
end

function PM.AllTags()
    local tags={}
    for _,tag in ipairs(PM.TagChoices) do tags[#tags+1]=tag end
    for _,tag in ipairs(PM.db.customTags or {}) do tags[#tags+1]=tag end
    return tags
end
local function validTag(text, previous)
    text=type(text)=="string" and text:match("^%s*(.-)%s*$") or ""
    if text=="" or #text>48 or text:find("[%c|]") then return nil,"Use 1-48 bytes, without control characters or |." end
    for _,tag in ipairs(PM.AllTags()) do
        if tag~=previous and tag:lower()==text:lower() then return nil,"That tag already exists." end
    end
    return text
end
function PM.CreateTag(text)
    if #PM.db.customTags>=20 then return nil,"You can keep up to 20 custom tags." end
    local tag,err=validTag(text); if not tag then return nil,err end
    table.insert(PM.db.customTags,tag); return tag
end
function PM.RenameTag(previous,text)
    local tag,err=validTag(text,previous); if not tag then return nil,err end
    for i,old in ipairs(PM.db.customTags) do
        if old==previous then
            PM.db.customTags[i]=tag
            for _,person in pairs(PM.db.people) do
                if person.tags and person.tags[old] then person.tags[old]=nil; person.tags[tag]=true end
            end
            return tag
        end
    end
    return nil,"Preset tags cannot be renamed."
end
function PM.DeleteTag(tag)
    for i,old in ipairs(PM.db.customTags) do
        if old==tag then
            table.remove(PM.db.customTags,i)
            for _,person in pairs(PM.db.people) do if person.tags then person.tags[tag]=nil end end
            return true
        end
    end
    return false
end
function PM.Characters()
    local names,seen={},{}
    for _,s in ipairs(PM.db.sessions) do
        if not seen[s.owner] then seen[s.owner]=true; names[#names+1]=s.owner end
    end
    if PM.currentOwner and not seen[PM.currentOwner] then names[#names+1]=PM.currentOwner end
    table.sort(names); return names
end
function PM.HasAdventure(target)
    return PM.HistoryIndex().sessions[target] or false
end
function PM.Duration(session)
    return math.max(0,(session.ended or session.lastSeen)-session.started-(session.awaySeconds or 0))
end

local function rosterKey(members)
    local names={}; for _,member in ipairs(members) do names[#names+1]=member.name end
    table.sort(names); return table.concat(names,"\n")
end
function PM.Checkpoint(owner,members,now)
    if not PM.db.enabled then PM.db.continuity=nil; return end
    PM.db.continuity={id=PM.active and PM.active.id,owner=owner,roster=rosterKey(members),at=now,
        notified=PM.notified,ignored=PM.ignored,suppressed=PM.suppressParty}
end
function PM.TryResume(owner,members,now)
    local saved=PM.pendingResume
    PM.pendingResume=nil
    if not saved then return end
    PM.db.continuity=nil
    local session
    for _,s in ipairs(PM.db.sessions) do if saved.id and s.id==saved.id then session=s; break end end
    local matches=PM.db.enabled and saved.owner==owner and type(saved.at)=="number"
        and now>=saved.at and now-saved.at<=PM.ResumeWindow and saved.roster==rosterKey(members)
    if matches and ((session and not session.ended) or saved.suppressed) then
        PM.active=session; PM.notified=saved.notified or {}; PM.ignored=saved.ignored; PM.suppressParty=saved.suppressed
        if session then
            session.awaySeconds=(session.awaySeconds or 0)+math.max(0,now-session.lastSeen)
            -- Begin a new observed location span; time spent offline is not a visit.
            session.resumed=true
        end
        return true
    end
    if session and not session.ended then session.ended=session.lastSeen end
    return false
end
function PM.FirstAdventure(name)
    local p=PM.HistoryIndex().people[name]; return p and p.first
end
function PM.RecentAdventure()
    return PM.HistoryIndex().latest
end
function PM.HasTag(person,tag)
    return not tag or (person.tags and person.tags[tag])
end
function PM.ToggleTag(person,tag)
    person.tags=person.tags or {}; person.tags[tag]=not person.tags[tag] or nil
end
function PM.TagText(person)
    local tags={}; for tag,enabled in pairs(person.tags or {}) do if enabled then tags[#tags+1]=tag end end
    table.sort(tags); return table.concat(tags,", ")
end
function PM.Export()
    local function encode(value)
        if type(value)=="string" then return string.format("%q",value) end
        if type(value)=="number" or type(value)=="boolean" then return tostring(value) end
        if type(value)~="table" then return "nil" end
        local keys={}; for key in pairs(value) do keys[#keys+1]=key end
        table.sort(keys,function(a,b) if type(a)~=type(b) then return type(a)<type(b) end; return a<b end)
        local entries={}
        for _,key in ipairs(keys) do entries[#entries+1]="["..encode(key).."]="..encode(value[key]) end
        return "{\n"..table.concat(entries,",\n").."\n}"
    end
    return "-- Familiar Faces journal backup v1. Contains private player names and notes.\nFamiliarFacesDB="..encode(PM.db).."\n"
end
function PM.ExportParts(text)
    local parts,start={},1
    while start<=#text do
        local finish=math.min(#text,start+11999)
        while text:byte(finish+1) and text:byte(finish+1)>=128 and text:byte(finish+1)<192 do finish=finish-1 end
        parts[#parts+1]=text:sub(start,finish); start=finish+1
    end
    if #parts==0 then parts[1]="" end
    return parts
end

function PM.LastAdventure(name, exclude)
    local p=PM.HistoryIndex().people[name]
    if not p then return end
    if p.last~=exclude then return p.last end
    local latest
    for _,session in ipairs(p.adventures) do
        if session ~= exclude then
            if not latest or session.lastSeen > latest.lastSeen then latest=session end
        end
    end
    return latest
end

function PM.RebuildPeople()
    PM.InvalidateHistory()
    local index=PM.HistoryIndex()
    for name,person in pairs(PM.db.people) do
        local p=index.people[name]
        person.encounters=p and p.count or 0; person.firstSeen=p and p.firstSeen; person.lastSeen=p and p.lastSeen
        person.class=(p and p.class) or person.class
    end
end

function PM.ForgetAdventure(target)
    for i,session in ipairs(PM.db.sessions) do
        if session==target then
            table.remove(PM.db.sessions,i)
            if PM.active==target then PM.active=nil; PM.suppressParty=true end
            if PM.pendingRecap==target then PM.pendingRecap=nil end
            if PM.db.continuity and PM.db.continuity.id==target.id then PM.db.continuity.id=nil; PM.db.continuity.suppressed=true end
            PM.RebuildPeople(); return true
        end
    end
end

function PM.ForgetPerson(name)
    if not PM.db.people[name] then return end
    PM.ignored=PM.ignored or {}; PM.ignored[name]=true
    if PM.db.continuity then PM.db.continuity.ignored=PM.ignored end
    for i=#PM.db.sessions,1,-1 do
        local session=PM.db.sessions[i]
        for j=#session.members,1,-1 do
            if session.members[j].name==name then table.remove(session.members,j) end
        end
        if #session.members==0 then
            table.remove(PM.db.sessions,i)
            if PM.active==session then
                PM.active=nil; PM.suppressParty=true
                if PM.db.continuity then PM.db.continuity.id=nil; PM.db.continuity.suppressed=true end
            end
            if PM.pendingRecap==session then PM.pendingRecap=nil end
        end
    end
    PM.db.people[name]=nil; PM.RebuildPeople(); return true
end

function PM.Init(db)
    db = db or {}
    db.version = 7
    db.sessions = db.sessions or {}
    db.people = db.people or {}
    db.nextID = db.nextID or 1
    db.enabled = db.enabled ~= false
    db.reunionNotices = db.reunionNotices ~= false
    db.favouritesFirst = db.favouritesFirst ~= false
    db.minimap = db.minimap or {hidden=false,angle=220}
    db.customTags = db.customTags or {}
    db.tooltips = db.tooltips ~= false
    db.tooltipNotes = db.tooltipNotes == true
    db.recaps = db.recaps == true
    db.rememberView = db.rememberView ~= false
    PM.active=nil; PM.notified=nil; PM.ignored=nil; PM.suppressParty=nil; PM.currentParty={}
    PM.pendingResume=db.continuity
    PM.db = db
    PM.InvalidateHistory()
    return db
end

function PM.EndSession(now, keepParty, recap)
    local ended=PM.active
    if ended then ended.ended = now end
    PM.active = nil
    if PM.pendingResume then
        for _,s in ipairs(PM.db.sessions) do if s.id==PM.pendingResume.id and not s.ended then s.ended=s.lastSeen end end
    end
    PM.pendingResume=nil; PM.db.continuity=nil
    if not keepParty then PM.notified = nil; PM.ignored=nil; PM.suppressParty=nil end
    if recap and ended and PM.db.recaps and PM.QueueRecap then PM.QueueRecap(ended) end
end

function PM.Record(owner, members, context, now)
    local db = PM.db
    if #members == 0 then PM.EndSession(now); return end
    if not db.enabled then PM.EndSession(now,true); return end
    if PM.pendingResume then PM.TryResume(owner,members,now) end
    if PM.suppressParty then return end
    local session = PM.active
    if session and session.owner ~= owner then PM.EndSession(now); session = nil end
    if not session then
        session = { id = db.nextID, owner = owner,
            started = now, lastSeen = now, kind = context.kind, zone = context.zone,
            difficulty = context.difficulty, members = {}, locations = {} }
        db.nextID = db.nextID + 1
        table.insert(db.sessions, 1, session)
        PM.active = session
    end
    local location = session.locations[#session.locations]
    if session.resumed or not location or location.zone ~= context.zone or location.kind ~= context.kind
        or location.difficulty ~= context.difficulty then
        location = {zone = context.zone, kind = context.kind, difficulty = context.difficulty, started = now}
        session.locations[#session.locations + 1] = location
    end
    session.resumed=nil
    location.lastSeen = now
    -- Retain the latest dungeon as the title even after returning outdoors.
    if context.kind == "Dungeon" or session.kind ~= "Dungeon" then
        session.kind = context.kind; session.zone = context.zone; session.difficulty = context.difficulty
    end
    local current = {}
    for _, member in ipairs(members) do
        if not (PM.ignored and PM.ignored[member.name]) then
        current[member.name] = true
        local saved
        for _, previous in ipairs(session.members) do
            if previous.name == member.name then saved = previous; break end
        end
        if not saved then
            PM.notified=PM.notified or {}
            if not PM.notified[member.name] then
                PM.notified[member.name]=true
                local previous=PM.LastAdventure(member.name,session)
                if db.reunionNotices and previous and PM.NotifyReunion then
                    PM.NotifyReunion(member.name,previous,db.people[member.name])
                end
            end
            saved = {name = member.name, class = member.class, role = member.role, joined = now}
            session.members[#session.members + 1] = saved
            local person = db.people[member.name] or { name = member.name, firstSeen = now, encounters = 0 }
            person.encounters = person.encounters + 1
            person.class = member.class or person.class
            db.people[member.name] = person
        end
        saved.class = member.class or saved.class; saved.role = member.role or saved.role
        saved.lastSeen = now; saved.left = nil
        db.people[member.name].lastSeen = now
        end
    end
    for _, member in ipairs(session.members) do
        if not current[member.name] and not member.left then member.left = now end
    end
    session.lastSeen = now
    PM.InvalidateHistory()
    return session
end

function PM.Search(query, kind, favourites)
    local results = {}
    query = string.lower(query or "")
    for _, session in ipairs(PM.db.sessions) do
        local text = session.owner .. " " .. session.zone .. " " .. session.kind.." "..(session.note or "")
        for _, location in ipairs(session.locations or {}) do text = text .. " " .. location.zone end
        local favourite = false
        for _, member in ipairs(session.members) do
            local person = PM.db.people[member.name] or {}
            text = text .. " " .. member.name .. " " .. (person.note or "").." "..(person.nickname or "").." "..PM.TagText(person)
            favourite = favourite or person.favourite
        end
        if (not kind or session.kind == kind) and (not favourites or favourite)
            and string.find(string.lower(text), query, 1, true) then
            results[#results + 1] = session
        end
    end
    return results
end

-- The two browsers share filters, but companion filters apply to that person.
function PM.Query(view, options)
    options = options or {}
    local results, seen = {}, {}
    local latestParty=options.recentParty and PM.RecentAdventure()
    local query = string.lower(options.query or "")
    local peopleText={}
    local function personText(person)
        local text=peopleText[person.name]
        if not text then
            text=string.lower(person.name.." "..(person.note or "").." "..(person.nickname or "").." "..PM.TagText(person))
            peopleText[person.name]=text
        end
        return text
    end
    for _, session in ipairs(PM.db.sessions) do
        local locationText = session.zone .. " " .. session.owner .. " " .. session.kind.." "..(session.note or "")
        for _, location in ipairs(session.locations or {}) do locationText = locationText .. " " .. location.zone end
        local locationMatch=string.find(string.lower(locationText),query,1,true)~=nil
        local recent = (not options.days or session.lastSeen >= time()-options.days*86400)
            and (not options.recentParty or session==latestParty)
            and (not options.owner or session.owner==options.owner)
        local matchingMember, matchesQuery = false, locationMatch
        for _, member in ipairs(session.members) do
            local person = PM.db.people[member.name] or {name = member.name, class = member.class}
            local eligible = (not options.class or (person.class or member.class) == options.class)
                and (not options.favourites or person.favourite)
                and (not options.notes or (person.note and person.note:match("%S")))
                and (not options.currentParty or (PM.currentParty and PM.currentParty[member.name]))
                and PM.HasTag(person,options.tag)
                and (not options.role or (view=="Adventures" and PM.Role(member.role) or PM.LastRole(member.name))==options.role)
            local personMatch = string.find(personText(person), query, 1, true) ~= nil
            if eligible then
                matchingMember = true
                if personMatch then matchesQuery = true end
            end
            if view == "Companions" and eligible and (personMatch or locationMatch)
                and recent and (not options.kind or session.kind == options.kind) and not seen[member.name] then
                seen[member.name] = true
                results[#results + 1] = person
            end
        end
        if view == "Adventures" and recent and matchingMember and matchesQuery and (not options.kind or session.kind == options.kind)
            and (not options.pinned or session.pinned) then
            results[#results + 1] = session
        end
    end
    if view == "Companions" and not options.owner and not options.kind and not options.days and not options.recentParty then
        for name,person in pairs(PM.db.people) do
            if not seen[name] and (not options.class or person.class==options.class)
                and (not options.favourites or person.favourite)
                and (not options.notes or (person.note and person.note:match("%S")))
                and (not options.currentParty or (PM.currentParty and PM.currentParty[name]))
                and PM.HasTag(person,options.tag)
                and (not options.role or PM.LastRole(name)==options.role)
                and string.find(personText(person),query,1,true) then
                results[#results+1]=person
            end
        end
    end
    local function value(item)
        local key = options.sort
        if view == "Companions" then
            if key == "name" then return string.lower(item.name) end
            if key == "class" then return item.class or "" end
            if key == "role" then return PM.RoleNames[PM.LastRole(item.name)] end
            if key == "encounters" then return item.encounters or 0 end
            if key == "note" then return string.lower(item.note or "") end
            if key == "favourite" then return item.favourite and 1 or 0 end
            if key == "adventure" then local last=PM.LastAdventure(item.name); return last and string.lower(last.zone) or "" end
            return item.lastSeen or 0
        end
        if key == "kind" then return item.kind end
        if key == "zone" then return string.lower(item.zone) end
        if key == "members" then return #item.members end
        if key == "duration" then return PM.Duration(item) end
        return item.started
    end
    local values={}; for _,item in ipairs(results) do values[item]=value(item) end
    table.sort(results, function(a, b)
        if view=="Adventures" and not not a.pinned ~= not not b.pinned then return not not a.pinned end
        if view=="Companions" and options.favouritesFirst and not not a.favourite ~= not not b.favourite then return not not a.favourite end
        local av, bv = values[a], values[b]
        if av == bv then return tostring(a.id or a.name) < tostring(b.id or b.name) end
        if options.ascending then return av < bv else return av > bv end
    end)
    return results
end

function PM.CleanView(state)
    state=type(state)=="table" and state or {}
    local src=type(state.options)=="table" and state.options or {}; local result={}
    local keys={name=true,class=true,role=true,encounters=true,note=true,favourite=true,adventure=true,lastSeen=true,kind=true,zone=true,members=true,duration=true,started=true}
    local view=state.view=="Companions" and "Companions" or "Adventures"
    result.sort=keys[src.sort] and src.sort or (view=="Companions" and "lastSeen" or "started")
    for _,k in ipairs({"ascending","favourites","notes","currentParty","pinned","recentParty"}) do result[k]=src[k]==true end
    result.query=type(src.query)=="string" and PM.LimitText(src.query,100) or ""
    result.kind=(src.kind=="Dungeon" or src.kind=="Questing") and src.kind or nil
    result.days=(src.days==7 or src.days==30) and src.days or nil
    result.role=PM.RoleNames[src.role] and src.role or nil
    for _,tag in ipairs(PM.AllTags()) do if src.tag==tag then result.tag=tag end end
    for _,owner in ipairs(PM.Characters()) do if src.owner==owner then result.owner=owner end end
    for _,p in pairs(PM.db.people) do if p.class and src.class==p.class then result.class=src.class; break end end
    return view,result
end
