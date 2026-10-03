PartyMemory = PartyMemory or {}
local PM = PartyMemory

function PM.Init(db)
    db = db or {}
    db.version = 1
    db.sessions = db.sessions or {}
    db.people = db.people or {}
    db.nextID = db.nextID or 1
    db.enabled = db.enabled ~= false
    PM.db = db
    return db
end

function PM.Record(owner, members, context, now)
    local db = PM.db
    if not db.enabled or #members == 0 then PM.active = nil; return end
    local keys = {}
    for _, member in ipairs(members) do keys[#keys + 1] = member.name end
    table.sort(keys)
    local signature = owner .. ":" .. context.kind .. ":" .. context.zone .. ":" .. table.concat(keys, ";")
    local session = PM.active
    if not session or session.signature ~= signature then
        session = { id = db.nextID, signature = signature, owner = owner,
            started = now, lastSeen = now, kind = context.kind, zone = context.zone,
            difficulty = context.difficulty, members = {} }
        db.nextID = db.nextID + 1
        table.insert(db.sessions, 1, session)
        PM.active = session
        for _, member in ipairs(members) do
            session.members[#session.members + 1] = { name = member.name, class = member.class, role = member.role }
            local person = db.people[member.name] or { name = member.name, firstSeen = now, encounters = 0 }
            person.encounters = person.encounters + 1
            person.class = member.class or person.class
            db.people[member.name] = person
        end
    end
    session.lastSeen = now
    for _, member in ipairs(members) do db.people[member.name].lastSeen = now end
    return session
end

function PM.Search(query, kind, favourites)
    local results = {}
    query = string.lower(query or "")
    for _, session in ipairs(PM.db.sessions) do
        local text = session.owner .. " " .. session.zone .. " " .. session.kind
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
