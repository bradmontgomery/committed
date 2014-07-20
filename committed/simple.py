from db import db


def _first(iter):
    """Return the first item from an iterable or None"""
    try:
        return list(iter)[0]
    except IndexError:
        return None


def get_user(username):
    """Get a User Node based on a username."""
    u = db.find("user", property_key="username", property_value=username)
    return _first(u)


def get_project(name):
    """Get a Project Node based on it's name"""
    p = db.find("project", property_key="name", property_value=name)
    return _first(p)


def user_details(n):
    """Print a User Node's properties and outgoing relationships."""
    # OR: print(n['name'], n['username'])
    for k, v in n.get_properties().items():
        print("{0}: {1}".format(k, v))

    for r in n.match_outgoing():
        print("* {0} {1}".format(r.type.lower(), r.end_node['name']))


def show_relationships(n):
    """Show both the incoming and outgoing relationships for the given node"""

    print("{0}: ".format(n['name']))
    for r in db.match(start_node=n, bidirectional=True):
        print("* {0} {1} {2}".format(
            r.start_node['name'],
            r.type.lower(),
            r.end_node['name']
        ))


def project_owners(limit=None):
    """Print and return User Nodes that own projects (with an optional limit)"""
    rels = db.match(rel_type="OWNED_BY", limit=limit)
    owners = []
    for rel in rels:
        proj = rel.start_node['name']
        user = rel.end_node['name']
        print("{0} is owned by {1}".format(proj, user))
        owners.append(rel.end_node)
    return owners


def list_user_contributors(n):
    """Given a User Node, list the projects they own, and all the people that
    contribute to each project."""

    # NOTE: (project)-[:OWNED_BY]->(user)
    # Why does match_incoming not work to find the project/user rel, below?
    project_rels = list(n.match(rel_type="OWNED_BY"))
    print("{0} owns {1} projects.".format(n['name'], len(project_rels)))

    for rel in project_rels:
        project = rel.start_node
        print("PROJECT: {0}".format(project['name']))

        for rel in project.match_incoming(rel_type="CONTRIBUTES_TO"):
            user = rel.start_node
            #print("({0})-[CONTRIBUTES_TO]->({1})".format(
                #rel.start_node['name'],
                #rel.end_node['name']
            #))
            if user['username'] != n['username']:
                print("* {0}".format(user['name']))


# Additional Questions
# --------------------
# - who contributes to the same projects that I've contributed to
# - how many "hops" am I away from someone?
