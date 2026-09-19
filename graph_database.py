import kuzu


# -----------------------------------
# CONNECT TO DATABASE
# -----------------------------------

db = kuzu.Database("smart_organizer_db")

conn = kuzu.Connection(db)


# -----------------------------------
# HELPER FUNCTION
# -----------------------------------

def result_to_rows(result):

    rows = []

    while result.has_next():
        rows.append(
            result.get_next()
        )

    return rows


# -----------------------------------
# CREATE GRAPH STRUCTURE
# -----------------------------------

def init_graph():

    conn.execute("""
    CREATE NODE TABLE IF NOT EXISTS Person (
        name STRING,
        email STRING,
        PRIMARY KEY(name)
    )
    """)

    conn.execute("""
    CREATE NODE TABLE IF NOT EXISTS Task (
        title STRING,
        duration_minutes INT64,
        priority STRING,
        deadline STRING,
        preferred_time STRING,
        status STRING,
        scheduled_date STRING,
        scheduled_start STRING,
        scheduled_end STRING,
        
        PRIMARY KEY(title)
    )
    """)

    conn.execute("""
    CREATE NODE TABLE IF NOT EXISTS Event (
        title STRING,
        event_date STRING,
        start_time STRING,
        end_time STRING,
        location STRING,
        status STRING,
        calendar_event_id STRING,
        PRIMARY KEY(title)
    )
    """)

    conn.execute("""
    CREATE NODE TABLE IF NOT EXISTS Project (
        name STRING,
        PRIMARY KEY(name)
    )
    """)

    # Person -> Event
    conn.execute("""
    CREATE REL TABLE IF NOT EXISTS ATTENDS (
        FROM Person TO Event
    )
    """)

    # Task -> Event
    conn.execute("""
    CREATE REL TABLE IF NOT EXISTS MUST_BEFORE (
        FROM Task TO Event
    )
    """)

    # Task -> Task
    conn.execute("""
    CREATE REL TABLE IF NOT EXISTS DEPENDS_ON (
        FROM Task TO Task
    )
    """)

    # Task -> Project
    conn.execute("""
    CREATE REL TABLE IF NOT EXISTS BELONGS_TO (
        FROM Task TO Project
    )
    """)

    print("Graph structure created.")


def clear_graph():

    conn.execute("""
    MATCH (n)
    DETACH DELETE n
    """)

    print("Old graph data deleted.")


def create_person(name, email=""):

    query = """
    CREATE (p:Person {
        name: $name,
        email: $email
    })

    RETURN
        p.name,
        p.email
    """

    result = conn.execute(
        query,
        {
            "name": name,
            "email": email
        }
    )

    rows = result_to_rows(result)

    return {
        "name": rows[0][0],
        "email": rows[0][1]
    }
def create_project(name):

    query = """
    CREATE (p:Project {
        name: $name
    })

    RETURN p.name
    """

    result = conn.execute(
        query,
        {
            "name": name
        }
    )

    rows = result_to_rows(result)

    return {
        "name": rows[0][0]
    }


def create_task(
    title,
    duration_minutes,
    priority="Medium",
    deadline="",
    preferred_time="",
    status="pending",
    scheduled_date="",
    scheduled_start="",
    scheduled_end=""
):

    query = """
    CREATE (t:Task {
        title: $title,
        duration_minutes: $duration_minutes,
        priority: $priority,
        deadline: $deadline,
        preferred_time: $preferred_time,
        status:$status,
        scheduled_date:$scheduled_date,
        scheduled_start:$scheduled_start,
        scheduled_end:$scheduled_end
    })

    RETURN
        t.title,
        t.duration_minutes,
        t.priority,
        t.deadline,
        t.preferred_time,
        t.status,
        t.scheduled_date,
        t.scheduled_start,
        t.scheduled_end
    """

    result = conn.execute(
        query,
        {
            "title": title,
            "duration_minutes": duration_minutes,
            "priority": priority,
            "deadline": deadline,
            "preferred_time": preferred_time,
            "status":status,
            "scheduled_date":scheduled_date,
            "scheduled_start":scheduled_start,
             "scheduled_end":scheduled_end
            

        }
    )

    rows = result_to_rows(result)

    row = rows[0]

    return {
        "title": row[0],
        "duration_minutes": row[1],
        "priority": row[2],
        "deadline": row[3],
        "preferred_time": row[4],
        "status":row[5],
        "scheduled_date":row[6],
        "scheduled_start":row[7],
        "scheduled_end":row[8]
    }

def create_event(
    title,
    event_date,
    start_time,
    end_time,
    location="",
    status="",
    calendar_event_id=""
):

    query = """
    CREATE (e:Event {
        title: $title,
        event_date: $event_date,
        start_time: $start_time,
        end_time: $end_time,
        location: $location,
        status:$status,
        calendar_event_id:$calendar_event_id
    })

    RETURN
        e.title,
        e.event_date,
        e.start_time,
        e.end_time,
        e.location,
        e.status,
        e.calendar_event_id
    """

    result = conn.execute(
        query,
        {
            "title": title,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "status":status,
            "calendar_event_id":calendar_event_id
        }
    )

    rows = result_to_rows(result)

    row = rows[0]

    return {
        "title": row[0],
        "event_date": row[1],
        "start_time": row[2],
        "end_time": row[3],
        "location": row[4],
        "status":row[5],
        "calendar_event_id":row[6]
    }



def person_attends_event(
    person_name,
    event_title
):

    query = """
    MATCH
        (p:Person {name: $person_name}),
        (e:Event {title: $event_title})

    CREATE
        (p)-[:ATTENDS]->(e)

    RETURN
        p.name,
        e.title
    """

    result = conn.execute(
        query,
        {
            "person_name": person_name,
            "event_title": event_title
        }
    )

    rows = result_to_rows(result)

    return {
        "person": rows[0][0],
        "event": rows[0][1]
    }

def task_must_be_before(
    task_title,
    event_title
):

    query = """
    MATCH
        (t:Task {title: $task_title}),
        (e:Event {title: $event_title})

    CREATE
        (t)-[:MUST_BEFORE]->(e)

    RETURN
        t.title,
        e.title
    """

    result = conn.execute(
        query,
        {
            "task_title": task_title,
            "event_title": event_title
        }
    )

    rows = result_to_rows(result)

    return {
        "task": rows[0][0],
        "event": rows[0][1]
    }


def task_depends_on(
    task_title,
    dependency_title
):

    query = """
    MATCH
        (t:Task {title: $task_title}),
        (d:Task {title: $dependency_title})

    CREATE
        (t)-[:DEPENDS_ON]->(d)

    RETURN
        t.title,
        d.title
    """

    result = conn.execute(
        query,
        {
            "task_title": task_title,
            "dependency_title": dependency_title
        }
    )

    rows = result_to_rows(result)

    return {
        "task": rows[0][0],
        "dependency": rows[0][1]
    }

def task_belongs_to_project(
    task_title,
    project_name
):

    query = """
    MATCH
        (t:Task {title: $task_title}),
        (p:Project {name: $project_name})

    CREATE
        (t)-[:BELONGS_TO]->(p)

    RETURN
        t.title,
        p.name
    """

    result = conn.execute(
        query,
        {
            "task_title": task_title,
            "project_name": project_name
        }
    )

    rows = result_to_rows(result)

    return {
        "task": rows[0][0],
        "project": rows[0][1]
    }



def get_all_tasks():

    query = """
    MATCH (t:Task)

    RETURN
        t.title,
        t.duration_minutes,
        t.priority,
        t.deadline,
        t.preferred_time,
        t.status,
        t.scheduled_date,
        t.scheduled_start,
        t.scheduled_end

    ORDER BY t.title
    """

    result = conn.execute(query)

    rows = result_to_rows(result)

    tasks = []

    for row in rows:

        tasks.append({
            "title": row[0],
            "duration_minutes": row[1],
            "priority": row[2],
            "deadline": row[3],
            "preferred_time": row[4],
            "status":row[5],
            "scheduled_date":row[6],
            "scheduled_start":row[7],
            "scheduled_end":row[8]

        })

    return tasks


def get_person_events(person_name):

    query = """
    MATCH
        (p:Person {name: $person_name})
        -[:ATTENDS]->
        (e:Event)

    RETURN
        e.title,
        e.event_date,
        e.start_time,
        e.end_time,
        e.location

    ORDER BY
        e.event_date,
        e.start_time
    """

    result = conn.execute(
        query,
        {
            "person_name": person_name
        }
    )

    rows = result_to_rows(result)

    events = []

    for row in rows:

        events.append({
            "title": row[0],
            "event_date": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "location": row[4]
        })

    return events

def get_tasks_before_event(event_title):

    query = """
    MATCH
        (t:Task)
        -[:MUST_BEFORE]->
        (e:Event {title: $event_title})

    RETURN
        t.title,
        t.priority,
        t.duration_minutes
    """

    result = conn.execute(
        query,
        {
            "event_title": event_title
        }
    )

    rows = result_to_rows(result)

    tasks = []

    for row in rows:

        tasks.append({
            "title": row[0],
            "priority": row[1],
            "duration_minutes": row[2]
        })

    return tasks



def get_task_dependencies(task_title):

    query = """
    MATCH
        (t:Task {title: $task_title})
        -[:DEPENDS_ON]->
        (d:Task)

    RETURN
        d.title,
        d.priority,
        d.duration_minutes
    """

    result = conn.execute(
        query,
        {
            "task_title": task_title
        }
    )

    rows = result_to_rows(result)

    dependencies = []

    for row in rows:

        dependencies.append({
            "title": row[0],
            "priority": row[1],
            "duration_minutes": row[2]
        })

    return dependencies

def get_project_tasks(project_name):

    query = """
    MATCH
        (t:Task)
        -[:BELONGS_TO]->
        (p:Project {name: $project_name})

    RETURN
        t.title,
        t.priority,
        t.duration_minutes
    """

    result = conn.execute(
        query,
        {
            "project_name": project_name
        }
    )

    rows = result_to_rows(result)

    tasks = []

    for row in rows:

        tasks.append({
            "title": row[0],
            "priority": row[1],
            "duration_minutes": row[2]
        })

    return tasks


def get_all_relationships():

    query = """
    MATCH (a)-[r]->(b)

    RETURN
        a,
        label(r),
        b
    """

    result = conn.execute(query)

    return result_to_rows(result)

def get_all_nodes():

    nodes = []

    # -------------------------
    # PEOPLE
    # -------------------------

    result = conn.execute("""
    MATCH (p:Person)
    RETURN p.name
    """)

    for row in result_to_rows(result):

        nodes.append({
            "id": "Person:" + row[0],
            "label": row[0],
            "type": "Person"
        })


    # -------------------------
    # TASKS
    # -------------------------

    result = conn.execute("""
    MATCH (t:Task)
    RETURN t.title
    """)

    for row in result_to_rows(result):

        nodes.append({
            "id": "Task:" + row[0],
            "label": row[0],
            "type": "Task"
        })


    # -------------------------
    # EVENTS
    # -------------------------

    result = conn.execute("""
    MATCH (e:Event)
    RETURN e.title
    """)

    for row in result_to_rows(result):

        nodes.append({
            "id": "Event:" + row[0],
            "label": row[0],
            "type": "Event"
        })


    # -------------------------
    # PROJECTS
    # -------------------------

    result = conn.execute("""
    MATCH (p:Project)
    RETURN p.name
    """)

    for row in result_to_rows(result):

        nodes.append({
            "id": "Project:" + row[0],
            "label": row[0],
            "type": "Project"
        })


    return nodes


def get_all_edges():

    edges = []


    # ==================================
    # PERSON ATTENDS EVENT
    # ==================================

    result = conn.execute("""
    MATCH
        (p:Person)
        -[:ATTENDS]->
        (e:Event)

    RETURN
        p.name,
        e.title
    """)

    for row in result_to_rows(result):

        edges.append({
            "source": "Person:" + row[0],
            "target": "Event:" + row[1],
            "relationship": "ATTENDS"
        })


    # ==================================
    # TASK MUST_BEFORE EVENT
    # ==================================

    result = conn.execute("""
    MATCH
        (t:Task)
        -[:MUST_BEFORE]->
        (e:Event)

    RETURN
        t.title,
        e.title
    """)

    for row in result_to_rows(result):

        edges.append({
            "source": "Task:" + row[0],
            "target": "Event:" + row[1],
            "relationship": "MUST_BEFORE"
        })


    # ==================================
    # TASK DEPENDS_ON TASK
    # ==================================

    result = conn.execute("""
    MATCH
        (t:Task)
        -[:DEPENDS_ON]->
        (d:Task)

    RETURN
        t.title,
        d.title
    """)

    for row in result_to_rows(result):

        edges.append({
            "source": "Task:" + row[0],
            "target": "Task:" + row[1],
            "relationship": "DEPENDS_ON"
        })


    # ==================================
    # TASK BELONGS_TO PROJECT
    # ==================================

    result = conn.execute("""
    MATCH
        (t:Task)
        -[:BELONGS_TO]->
        (p:Project)

    RETURN
        t.title,
        p.name
    """)

    for row in result_to_rows(result):

        edges.append({
            "source": "Task:" + row[0],
            "target": "Project:" + row[1],
            "relationship": "BELONGS_TO"
        })


    return edges
def get_task(title):
    query = """
    MATCH (t:Task {title: $title})
    RETURN
        t.title,
        t.duration_minutes,
        t.priority,
        t.deadline,
        t.preferred_time,
        t.status,
        t.scheduled_date,
        t.scheduled_start,
        t.scheduled_end
    """

    result = conn.execute(
        query,
        {
            "title": title
        }
    )

    rows = result_to_rows(result)
    if not rows:
        return None
    row = rows[0]

    return {
        "title": row[0],
        "duration_minutes": row[1],
        "priority": row[2],
        "deadline": row[3],
        "preferred_time": row[4],
        "status": row[5],
        "scheduled_date": row[6],
        "scheduled_start": row[7],
        "scheduled_end": row[8]
    }


def update_task(title, duration_minutes, priority, deadline, preferred_time, status):
    query = """
    MATCH (t:Task {title: $title})
    SET t.duration_minutes = $duration_minutes,
        t.priority = $priority,
        t.deadline = $deadline,
        t.preferred_time = $preferred_time,
        t.status = $status
    """
    conn.execute(
        query,
        {
            "title": title,
            "duration_minutes": duration_minutes,
            "priority": priority,
            "deadline": deadline,
            "preferred_time": preferred_time,
            "status": status
        }
    )

def delete_task(title):
    query = """
    MATCH (t:Task {title: $title})
    DETACH DELETE t
    """
    conn.execute(query, {"title": title})

def get_event(title):
    query = """
    MATCH (e:Event {title: $title})
    RETURN
        e.title,
        e.event_date,
        e.start_time,
        e.end_time,
        e.location,
        e.status,
        e.calendar_event_id
    """
    result = conn.execute(query, {"title": title})
    rows = result_to_rows(result)
    
    if not rows:
        return None
        
    row = rows[0]
    return {
        "title": row[0],
        "event_date": row[1],
        "start_time": row[2],
        "end_time": row[3],
        "location": row[4],
        "status": row[5],
        "calendar_event_id": row[6]
    }

def update_event(title, event_date, start_time, end_time, location, status):
    query = """
    MATCH (e:Event {title: $title})
    SET e.event_date = $event_date,
        e.start_time = $start_time,
        e.end_time = $end_time,
        e.location = $location,
        e.status = $status
    """
    conn.execute(
        query,
        {
            "title": title,
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "status": status
        }
    )

def delete_event(title):
    query = """
    MATCH (e:Event {title: $title})
    DETACH DELETE e
    """
    conn.execute(query, {"title": title})

def get_all_events():
    query = """
    MATCH (e:Event)
    RETURN
        e.title,
        e.event_date,
        e.start_time,
        e.end_time,
        e.location,
        e.status,
        e.calendar_event_id
    ORDER BY e.event_date, e.start_time
    """
    result = conn.execute(query)
    rows = result_to_rows(result)
    events = []
    for row in rows:
        events.append({
            "title": row[0],
            "event_date": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "location": row[4],
            "status": row[5],
            "calendar_event_id": row[6]
        })
    return events

def get_all_people():
    query = """
    MATCH (p:Person)
    RETURN p.name, p.email
    ORDER BY p.name
    """
    result = conn.execute(query)
    rows = result_to_rows(result)
    people = []
    for row in rows:
        people.append({
            "name": row[0],
            "email": row[1]
        })
    return people

def get_all_projects():
    query = """
    MATCH (p:Project)
    RETURN p.name
    ORDER BY p.name
    """
    result = conn.execute(query)
    rows = result_to_rows(result)
    projects = []
    for row in rows:
        projects.append({
            "name": row[0]
        })
    return projects
def get_high_priority_tasks():
    query = """
    MATCH (t:Task {priority: 'High'})
    RETURN 
        t.title, t.duration_minutes, t.priority, t.deadline, 
        t.preferred_time, t.status, t.scheduled_date, 
        t.scheduled_start, t.scheduled_end
    """
    result = conn.execute(query)
    tasks = []
    for row in result_to_rows(result):
        tasks.append({
            "title": row[0], "duration_minutes": row[1], "priority": row[2],
            "deadline": row[3], "preferred_time": row[4], "status": row[5],
            "scheduled_date": row[6], "scheduled_start": row[7], "scheduled_end": row[8]
        })
    return tasks

def get_events_for_date(event_date):
    query = """
    MATCH (e:Event {event_date: $event_date})
    RETURN 
        e.title, e.event_date, e.start_time, e.end_time, 
        e.location, e.status, e.calendar_event_id
    """
    result = conn.execute(query, {"event_date": event_date})
    events = []
    for row in result_to_rows(result):
        events.append({
            "title": row[0], "event_date": row[1], "start_time": row[2],
            "end_time": row[3], "location": row[4], "status": row[5],
            "calendar_event_id": row[6]
        })
    return events

def get_tasks_for_date(scheduled_date):
    query = """
    MATCH (t:Task {scheduled_date: $scheduled_date})
    RETURN 
        t.title, t.duration_minutes, t.priority, t.deadline, 
        t.preferred_time, t.status, t.scheduled_date, 
        t.scheduled_start, t.scheduled_end
    """
    result = conn.execute(query, {"scheduled_date": scheduled_date})
    tasks = []
    for row in result_to_rows(result):
        tasks.append({
            "title": row[0], "duration_minutes": row[1], "priority": row[2],
            "deadline": row[3], "preferred_time": row[4], "status": row[5],
            "scheduled_date": row[6], "scheduled_start": row[7], "scheduled_end": row[8]
        })
    return tasks

def get_event_attendees(event_title):
    query = """
    MATCH (p:Person)-[:ATTENDS]->(e:Event {title: $event_title})
    RETURN p.name, p.email
    """
    result = conn.execute(query, {"event_title": event_title})
    attendees = []
    for row in result_to_rows(result):
        attendees.append({
            "name": row[0],
            "email": row[1]
        })
    return attendees