-- Read the addon's exported data grammar. Never evaluate pasted Lua.
local PM=FamiliarFaces
local MAX_BYTES=2*1024*1024
PM.ImportMaxBytes=MAX_BYTES
local function fail(message) error(message,0) end
local function decode(text)
    if type(text)~="string" or #text>MAX_BYTES then fail("Backup is too large (maximum 2 MB).") end
    text=text:gsub("^\239\187\191","")
    local pos,nodes=1,0
    local function skip()
        while true do
            local _,finish=text:find("^%s+",pos); if finish then pos=finish+1 end
            if text:sub(pos,pos+1)~="--" then return end
            pos=(text:find("\n",pos+2,true) or #text)+1
        end
    end
    local function token(value)
        skip(); if text:sub(pos,pos+#value-1)~=value then fail("Invalid backup near character "..pos..".") end
        pos=pos+#value
    end
    local function str()
        token('"'); local parts={}
        while pos<=#text do
            local char=text:sub(pos,pos); pos=pos+1
            if char=='"' then return table.concat(parts) end
            if char=="\\" then
                local escape=text:sub(pos,pos); pos=pos+1
                local escapes={a="\a",b="\b",f="\f",n="\n",r="\r",t="\t",v="\v",['"']='"',["'"]="'",["\\"]="\\",["\n"]="\n"}
                if escape:match("%d") then
                    local digits=escape
                    for _=1,2 do local c=text:sub(pos,pos); if not c:match("%d") then break end; digits=digits..c; pos=pos+1 end
                    if tonumber(digits)>255 then fail("Invalid character escape.") end
                    parts[#parts+1]=string.char(tonumber(digits))
                elseif escape=="\r" then
                    if text:sub(pos,pos)=="\n" then pos=pos+1 end
                    parts[#parts+1]="\n"
                elseif escapes[escape] then parts[#parts+1]=escapes[escape]
                else fail("Unsupported character escape.") end
            elseif char=="\n" or char=="\r" then fail("An unescaped line break was found inside a quoted value.")
            else parts[#parts+1]=char end
        end
        fail("The backup ends inside a quoted value. Copy every export part.")
    end
    local value
    value=function(depth)
        nodes=nodes+1
        if nodes>200000 or depth>12 then fail("Backup has too many entries or nesting levels.") end
        skip(); local char=text:sub(pos,pos)
        if char=='"' then return str() end
        if char=="{" then
            pos=pos+1; local result,seen={},{}
            skip()
            while text:sub(pos,pos)~="}" do
                token("["); local key=value(depth+1)
                if type(key)~="string" and (type(key)~="number" or key<1 or key%1~=0) then fail("Invalid table key.") end
                if seen[key] then fail("Duplicate table key.") end; seen[key]=true
                token("]"); token("="); result[key]=value(depth+1); skip()
                if text:sub(pos,pos)=="," then pos=pos+1; skip()
                elseif text:sub(pos,pos)~="}" then fail("Missing comma or closing brace.") end
            end
            pos=pos+1; return result
        end
        for word,v in pairs({["true"]=true,["false"]=false}) do
            if text:sub(pos,pos+#word-1)==word then pos=pos+#word; return v end
        end
        if text:sub(pos,pos+2)=="nil" then pos=pos+3; return nil end
        local number=text:match("^[-+]?%d+%.?%d*[eE]?[-+]?%d*",pos)
        local numeric=number and tonumber(number)
        if numeric and numeric==numeric and math.abs(numeric)<1e15 then pos=pos+#number; return numeric end
        fail("Only Familiar Faces backup data is accepted; code and expressions are not allowed.")
    end
    token("FamiliarFacesDB"); token("="); local db=value(0); skip()
    if pos<=#text then fail("Unexpected text after the backup. Paste only the exported archive.") end
    return db
end
local function stringValue(value,max,optional,multiline)
    if value==nil and optional then return nil end
    if type(value)~="string" or PM.TextLength(value)>max or (not optional and value=="") then fail("A name, label or note is missing or too long.") end
    if value:find(multiline and "[%z\1-\8\11\12\14-\31]" or "[%c]") then fail("A field contains unsupported control characters.") end
    return value
end
local function num(value,optional)
    if value==nil and optional then return nil end
    if type(value)~="number" or value<0 or value>4102444800 or value%1~=0 then fail("Invalid timestamp or number.") end
    return value
end
local function array(value,limit)
    if type(value)~="table" then fail("A required list is missing.") end
    local count=0
    for k in pairs(value) do if type(k)~="number" or k<1 or k%1~=0 then fail("Invalid list key.") end; count=count+1 end
    if count~=#value or count>limit then fail("A list is incomplete or exceeds the import limit.") end
    for i=1,count do if value[i]==nil then fail("A list is incomplete.") end end
    return value
end
local function class(value)
    if value==nil then return nil end
    if type(value)~="string" or #value>32 or not value:match("^[A-Z_]+$") then fail("Invalid class value.") end
    return value
end
local function clean(raw)
    if type(raw)~="table" or type(raw.version)~="number" or raw.version%1~=0 or raw.version<1 or raw.version>7 then fail("Unsupported backup version.") end
    local db={sessions={},people={},customTags={}}
    local tags={}; for _,t in ipairs(PM.TagChoices) do tags[t:lower()]=t end
    for _,t in ipairs(array(raw.customTags or {},20)) do
        stringValue(t,48); if #t>48 or t:find("|") or tags[t:lower()] then fail("Invalid or duplicate custom tag.") end
        tags[t:lower()]=t; db.customTags[#db.customTags+1]=t
    end
    if type(raw.people)~="table" then fail("Companion profiles are missing.") end
    local count=0
    for name,p in pairs(raw.people) do
        count=count+1; if count>25000 or type(p)~="table" then fail("Too many or invalid companion profiles.") end
        stringValue(name,160); if p.name and p.name~=name then fail("A companion name does not match its profile.") end
        local person={name=name,class=class(p.class),note=stringValue(p.note,1000,true,true),nickname=stringValue(p.nickname,60,true),favourite=p.favourite==true,tags={}}
        if p.tags~=nil and type(p.tags)~="table" then fail("Invalid companion tags.") end
        for tag,on in pairs(p.tags or {}) do
            if on then
                if type(tag)~="string" or not tags[tag:lower()] then fail("A companion uses an unknown tag.") end
                person.tags[tags[tag:lower()]]=true
            end
        end
        db.people[name]=person
    end
    for _,s in ipairs(array(raw.sessions,10000)) do
        if type(s)~="table" then fail("Invalid adventure.") end
        local session={owner=stringValue(s.owner,160),zone=stringValue(s.zone,250),kind=s.kind,started=num(s.started),lastSeen=num(s.lastSeen),ended=num(s.ended or s.lastSeen),
            note=stringValue(s.note,1000,true,true),pinned=s.pinned==true,awaySeconds=num(s.awaySeconds or 0),difficulty=stringValue(s.difficulty,100,true),members={},locations={}}
        if session.kind~="Dungeon" and session.kind~="Questing" then fail("Invalid adventure activity.") end
        if session.lastSeen<session.started or session.ended<session.lastSeen or session.awaySeconds>session.ended-session.started then fail("Invalid adventure time range.") end
        local names={}
        for _,m in ipairs(array(s.members,1000)) do
            if type(m)~="table" then fail("Invalid companion entry.") end
            local name=stringValue(m.name,160)
            if names[name] then fail("Duplicate companion in an adventure.") end; names[name]=true
            local member={name=name,class=class(m.class),role=PM.Role(m.role),joined=num(m.joined or s.started),lastSeen=num(m.lastSeen or s.lastSeen),left=num(m.left,true)}
            if member.joined<s.started or member.lastSeen<member.joined or member.lastSeen>session.ended then fail("Invalid companion time range.") end
            session.members[#session.members+1]=member
            db.people[name]=db.people[name] or {name=name,class=member.class,tags={}}
        end
        if #session.members==0 then fail("An adventure has no companions.") end
        for _,l in ipairs(array(s.locations or {},1000)) do
            if type(l)~="table" then fail("Invalid location entry.") end
            local location={zone=stringValue(l.zone,250),kind=l.kind,started=num(l.started),lastSeen=num(l.lastSeen or l.started),difficulty=stringValue(l.difficulty,100,true)}
            if (l.kind~="Dungeon" and l.kind~="Questing") or location.started<s.started or location.lastSeen<location.started or location.lastSeen>session.ended then fail("Invalid location or time range.") end
            session.locations[#session.locations+1]=location
        end
        db.sessions[#db.sessions+1]=session
    end
    return db
end
local function copy(value)
    if type(value)~="table" then return value end
    local result={}; for k,v in pairs(value) do result[k]=copy(v) end; return result
end
local function identity(s)
    local out={}
    local function add(v) v=tostring(v or ""); out[#out+1]=#v..":"..v end
    add(s.owner); add(s.started); add(s.lastSeen); add(s.ended or s.lastSeen); add(s.kind); add(s.zone); add(s.difficulty)
    add(s.awaySeconds or 0)
    local members={}; for _,m in ipairs(s.members) do members[#members+1]=m end
    table.sort(members,function(a,b) return a.name<b.name end)
    for _,m in ipairs(members) do add(m.name); add(m.class); add(PM.Role(m.role)); add(m.joined or s.started); add(m.lastSeen or s.lastSeen); add(m.left) end
    for _,l in ipairs(s.locations or {}) do add(l.zone); add(l.kind); add(l.difficulty); add(l.started); add(l.lastSeen or l.started) end
    return table.concat(out,"|")
end
function PM.PreviewImport(text,mode)
    local ok,incoming=pcall(function() return clean(decode(text)) end)
    if not ok then return nil,incoming end
    if mode~="merge" and mode~="replace" then return nil,"Choose Merge or Replace journal." end
    local target=copy(PM.db); target.continuity=nil
    if mode=="replace" then target.sessions={}; target.people={}; target.customTags={} end
    local summary={added=0,duplicates=0,profiles=0,conflicts=0,mode=mode}
    local tagMap={}; for _,t in ipairs(PM.TagChoices) do tagMap[t:lower()]=t end
    for _,t in ipairs(target.customTags) do tagMap[t:lower()]=t end
    for _,t in ipairs(incoming.customTags) do
        if not tagMap[t:lower()] then
            if #target.customTags>=20 then return nil,"Merging would exceed 20 custom tags. Remove unused tags first." end
            target.customTags[#target.customTags+1]=t; tagMap[t:lower()]=t
        end
    end
    local function mergeText(dst,src,key)
        if not dst[key] or not dst[key]:match("%S") then dst[key]=src[key]
        elseif src[key] and src[key]:match("%S") and src[key]~=dst[key] then summary.conflicts=summary.conflicts+1 end
    end
    for name,p in pairs(incoming.people) do
        local old=target.people[name]
        if not old then old={name=name,class=p.class,tags={}}; target.people[name]=old; summary.profiles=summary.profiles+1 end
        mergeText(old,p,"note"); mergeText(old,p,"nickname")
        old.favourite=old.favourite or p.favourite; old.class=old.class or p.class; old.tags=old.tags or {}
        for t,on in pairs(p.tags) do if on then old.tags[tagMap[t:lower()]]=true end end
    end
    local known={}; local nextID=target.nextID or 1
    for _,s in ipairs(target.sessions) do known[identity(s)]=s; nextID=math.max(nextID,(s.id or 0)+1) end
    for _,s in ipairs(incoming.sessions) do
        local key=identity(s); local old=known[key]
        if old then summary.duplicates=summary.duplicates+1; mergeText(old,s,"note"); old.pinned=old.pinned or s.pinned
        else s.id=nextID; nextID=nextID+1; target.sessions[#target.sessions+1]=s; known[key]=s; summary.added=summary.added+1 end
    end
    table.sort(target.sessions,function(a,b) if a.started==b.started then return a.id>b.id end; return a.started>b.started end)
    target.nextID=nextID; target.version=7
    summary.total=#target.sessions
    return {data=target,summary=summary,before=PM.Export()}
end
function PM.ApplyImport(plan)
    if type(plan)~="table" or not plan.data or not plan.before then return nil,"Preview a backup first." end
    if InCombatLockdown and InCombatLockdown() then return nil,"Finish combat before importing." end
    local partyCount=GetNumSubgroupMembers and GetNumSubgroupMembers() or (GetNumPartyMembers and GetNumPartyMembers() or 0)
    if partyCount>0 or (IsInRaid and IsInRaid()) or PM.active or PM.pendingResume or (PM.currentParty and next(PM.currentParty)) then return nil,"Leave your party before importing a journal." end
    if PM.Export()~=plan.before then return nil,"Your journal changed after the preview. Preview the backup again." end
    FamiliarFacesDB=PM.Init(plan.data); PM.RebuildPeople(); PM.pendingRecap=nil
    if PM.HideRecap then PM.HideRecap() end
    return true
end
