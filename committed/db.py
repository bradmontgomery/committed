import random
from py2neo import neo4j, node, rel


HOST = 'http://localhost:7474'
PATH = '/db/data/'

# Connect to a DB.
db = neo4j.GraphDatabaseService(HOST + PATH)


# -----------------------------------------------------------------------------
# I'm gonna generate some sample data while learning this stuff. The following
# are tools to do that.
# -----------------------------------------------------------------------------

# Invent some people.
people = [
    'Brad',
    'Bridget',
    'Billy',
    'Betty',
    'Bob',
    'Brenda',
    'Charles',
    'Cindy',
    'Chuck',
    'Catherine',
    'Donald',
    'Delia',
    'Evan',
    'Evelynne',
    'Frank',
    'Felicity',
    'Zeb',
    'Zoe',
]

# And some interesting project names, e.g. adj+noun
adjectives = [
    'flaming', 'sparkling', 'ambiguous', 'random', 'open', 'free', 'massive',
    'tiny', 'enterprise', 'flailing', 'secret',
]
nouns = [
    'aardvark', 'workhorse', 'sealion', 'butterfly', 'grasshopper',
    'jackrabbit', 'turtledove', 'armyant'
]


def random_users(n=100):
    """Generate `n` random users. Returns (full name, username)."""
    results = []
    while len(results) < n:
        first, last = random.choice(people), random.choice(people)
        name = " ".join([first, last])
        username = "".join([first, last]).lower()
        t = (name, username)
        if t not in results:
            results.append(t)
    return results


def random_projects(n=20):
    results = []
    while len(results) < n:
        p = "-".join([random.choice(adjectives), random.choice(nouns)])
        if p not in results:
            results.append(p)
    return results


def create_project_graph():
    """Creates a project Graph and stashes it in Neo4j.

    Returns a tuple of (users, projects, relationships), where each item is
    a list of the created data.

    """
    # Create some Users
    user_nodes = [node(name=t[0], username=t[1]) for t in random_users()]
    users = db.create(*user_nodes)
    for u in users:
        # ...and label them as such.
        u.add_labels("user")

    # Create some Projects.
    project_nodes = [node(name=s) for s in random_projects()]
    projects = db.create(*project_nodes)

    rels = []
    for p in projects:
        # ...and label them as such.
        p.add_labels("project")

        # Set up some relationships.
        # 1. Give the project a single Owner
        rels.append(rel((p, "OWNED_BY", random.choice(users))))

        # 2. Give the project a random number of contributors.
        for u in random.sample(users, random.randrange(3, 50)):
            rels.append(rel((u, "CONTRIBUTES_TO", p)))

    # Save the relationships
    rels = db.create(*rels)
    return (users, projects, rels)
