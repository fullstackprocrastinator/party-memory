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
