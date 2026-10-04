FamiliarFaces = FamiliarFaces or {}
local PM = FamiliarFaces

function PM.Init(db)
    db = db or {}
    db.version = 2
    db.sessions = db.sessions or {}
    db.people = db.people or {}
    db.nextID = db.nextID or 1
    db.enabled = db.enabled ~= false
    PM.db = db
    return db
end

function PM.EndSession(now)
    if PM.active then PM.active.ended = now end
    PM.active = nil
end

function PM.Record(owner, members, context, now)
    local db = PM.db
    if not db.enabled or #members == 0 then PM.EndSession(now); return end
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
    if not location or location.zone ~= context.zone or location.kind ~= context.kind
        or location.difficulty ~= context.difficulty then
        location = {zone = context.zone, kind = context.kind, difficulty = context.difficulty, started = now}
        session.locations[#session.locations + 1] = location
    end
    location.lastSeen = now
    -- Retain the latest dungeon as the title even after returning outdoors.
    if context.kind == "Dungeon" or session.kind ~= "Dungeon" then
        session.kind = context.kind; session.zone = context.zone; session.difficulty = context.difficulty
    end
    local current = {}
    for _, member in ipairs(members) do
        current[member.name] = true
        local saved
        for _, previous in ipairs(session.members) do
            if previous.name == member.name then saved = previous; break end
        end
        if not saved then
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
    for _, member in ipairs(session.members) do
        if not current[member.name] and not member.left then member.left = now end
    end
    session.lastSeen = now
    return session
end

function PM.Search(query, kind, favourites)
    local results = {}
    query = string.lower(query or "")
    for _, session in ipairs(PM.db.sessions) do
        local text = session.owner .. " " .. session.zone .. " " .. session.kind
        for _, location in ipairs(session.locations or {}) do text = text .. " " .. location.zone end
        local favourite = false
        for _, member in ipairs(session.members) do
            local person = PM.db.people[member.name] or {}
            text = text .. " " .. member.name .. " " .. (person.note or "")
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
    local query = string.lower(options.query or "")
    for _, session in ipairs(PM.db.sessions) do
        local locationText = session.zone .. " " .. session.owner .. " " .. session.kind
        for _, location in ipairs(session.locations or {}) do locationText = locationText .. " " .. location.zone end
        local matchingMember, matchesQuery = false, string.find(string.lower(locationText), query, 1, true) ~= nil
        for _, member in ipairs(session.members) do
            local person = PM.db.people[member.name] or {name = member.name, class = member.class}
            local eligible = (not options.class or (person.class or member.class) == options.class)
                and (not options.favourites or person.favourite)
                and (not options.notes or (person.note and person.note:match("%S")))
            local personMatch = string.find(string.lower(member.name .. " " .. (person.note or "")), query, 1, true) ~= nil
            if eligible then
                matchingMember = true
                if personMatch then matchesQuery = true end
            end
            if view == "Companions" and eligible and (personMatch or string.find(string.lower(locationText), query, 1, true))
                and (not options.kind or session.kind == options.kind) and not seen[member.name] then
                seen[member.name] = true
                results[#results + 1] = person
            end
        end
        if view == "Adventures" and matchingMember and matchesQuery and (not options.kind or session.kind == options.kind) then
            results[#results + 1] = session
        end
    end
    local function value(item)
        local key = options.sort
        if view == "Companions" then
            if key == "name" then return string.lower(item.name) end
            if key == "class" then return item.class or "" end
            if key == "encounters" then return item.encounters or 0 end
            if key == "note" then return string.lower(item.note or "") end
            if key == "favourite" then return item.favourite and 1 or 0 end
            return item.lastSeen or 0
        end
        if key == "kind" then return item.kind end
        if key == "zone" then return string.lower(item.zone) end
        if key == "members" then return #item.members end
        if key == "duration" then return math.max(0, (item.ended or item.lastSeen) - item.started) end
        return item.started
    end
    table.sort(results, function(a, b)
        local av, bv = value(a), value(b)
        if av == bv then return tostring(a.id or a.name) < tostring(b.id or b.name) end
        if options.ascending then return av < bv else return av > bv end
    end)
    return results
end
