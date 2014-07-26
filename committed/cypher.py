"""
Some of the same things from the ``simple`` module, but using CYPHER
instead of the python api.

"""
from py2neo import cypher

from db import HOST
from simple import _first


def cypher_transaction():
    """Creates & Returns a Cyper Transaction."""
    session = cypher.Session(HOST)
    return session.create_transaction()


def get_user(username):
    """Get a User Node based on a username."""
    tx = cypher_transaction()
    query = """MATCH (n:user) WHERE n.username={username} RETURN n"""
    tx.append(query, parameters={'username': username})
    result = tx.commit()

    # Returns a result of the form [[
    #   Record(
    #       columns=('n',),
    #       values=(Node('http://localhost:7474/db/data/node/137'),)
    #   )
    # ]]
    return _first(result)[0].values[0]


def get_user_projects(username):
    """List a user's projects."""

    tx = cypher_transaction()
    query = """
        MATCH (p:project)-[:OWNED_BY]->(u:user {username:{uname}})
        RETURN p
    """
    tx.append(query, parameters={'uname': username})
    results = _first(tx.commit())
    projects = []
    for r in results:
        proj, = r.values
        print("* {0}".format(proj['name']))
        projects.append(proj)
    return projects


def get_project(name):
    """Get a Project Node based on it's name"""
    tx = cypher_transaction()
    query = """MATCH (n:project) WHERE n.name={project_name} RETURN n"""
    tx.append(query, parameters={'project_name': name})
    result = tx.commit()

    # Returns a result of the form [[
    #   Record(
    #       columns=('n',),
    #       values=(Node('http://localhost:7474/db/data/node/233'),)
    #   )
    # ]]
    return _first(result)[0].values[0]


def project_owners(limit=None):
    """Print and return User Nodes that own projects (with an optional limit)"""
    tx = cypher_transaction()
    query = """MATCH (p:project)-[:OWNED_BY]->(u:user) RETURN u, p"""
    if limit is not None:
        query += " LIMIT {limit}"
        tx.append(query, parameters={'limit': limit})
    else:
        tx.append(query)

    results = tx.commit()
    owners = []  # Just a list of user nodes
    for record in _first(results):
        user, project = record.values
        print("{0} is owned by {1}".format(project['name'], user['name']))
        owners.append(user)
    return owners


def project_contributors(project_name):
    """Given a project, list its contributors."""
    tx = cypher_transaction()
    owners_query = """
        MATCH (p:project)-[:OWNED_BY]->(u:user)
        WHERE p.name={project_name}
        RETURN u
    """
    contributors_query = """
        MATCH (u:user)-[:CONTRIBUTES_TO]->(p:project)
        WHERE p.name={project_name}
        RETURN u, p
        ORDER BY u.name
    """
    tx.append(owners_query, parameters={'project_name': project_name})
    tx.append(contributors_query, parameters={'project_name': project_name})
    owners, contributors = tx.commit()
    for record in owners:
        u = record.values[0]
        print("> Owner: {0}".format(u['name']))
    for record in contributors:
        u, p = record.values
        print("* {0} -> {1}".format(u['name'], p['name']))


def list_user_contributors(n):
    """Given a User Node, list the projects they own, and all the people that
    contribute to each project."""

    tx = cypher_transaction()
    query = """
        MATCH (p:project)-[:OWNED_BY]->(owner),
              (u:user)-[:CONTRIBUTES_TO]->(p)
        WHERE owner.username={username}
        RETURN DISTINCT u, p
    """
    tx.append(query, parameters={'username': n['username']})
    results = _first(tx.commit())
    contributors = set()
    for record in results:
        user, project = record.values
        contributors.add(user)
        print("* {0} -> {1}".format(user['name'], project['name']))
    return contributors


def user_path(a, b):
    """Given two user nodes, what's user A's connection to user B? E.G. How
    many `hops` are in between? What's the shortest path?

    """
    tx = cypher_transaction()

    # Limit the number of relationships in the path?
    # p = shortestPath((a)-[*..15]-(b))
    query = """
        MATCH
            (a:user {username:{username_a}}),
            (b:user {username:{username_b}}),
            p = shortestPath((a)-[]->(b))
        RETURN LENGTH(p), p
    """
    params = {
        'username_a': a['username'],
        'username_b': b['username']
    }
    tx.append(query, parameters=params)
    results = _first(tx.commit())
    paths = []
    for record in results:
        length, path = record.values
        m = "There are {0} hops from {1} to {2}:\n"
        print(m.format(length, a['name'], b['name']))
        for rel in path.relationships:
            print("  ({0})-[:{1}]->({2})".format(
                rel.start_node['name'],
                rel.type,
                rel.end_node['name']
            ))
        paths.append(path)
    return paths


def project_recommendations(project_name, limit=5):
    """
    People that contribute to `project_name` also contribute to...
    """
    query = """
    MATCH
      (p:project)<-[:CONTRIBUTES_TO]-(u:user)-[:CONTRIBUTES_TO]->(o:project)
    WHERE p.name={name}
    RETURN o.name, count(*)
    ORDER BY count(*) DESC, o.name
    LIMIT {limit}
    """
    # o.name            count(*)
    # --------------------------
    # open-jackrabbit       6
    # flailing-jackrabbit   5
    # secret-butterfly      5
    # tiny-armyant          5
    # flaming-butterfly     3

    tx = cypher_transaction()
    tx.append(query, parameters={"name": project_name, "limit": limit})
    results = _first(tx.commit())
    for record in results:
        name, count = record.values
        print("({0}) {1}".format(count, name))
    return results


def similar_contributors(username, limit=10):
    """Find People who contribute to "similar" projects as `username`."""
    query = """
    MATCH
      (me:user)-[:CONTRIBUTES_TO]->(p:project)-[:OWNED_BY]->
      (u)-[:CONTRIBUTES_TO]->(x:project)<-[:CONTRIBUTES_TO]-(people)
    WHERE me.username={username} AND NOT me=people
    RETURN people.name AS name, count(*) AS similar_contribs
    ORDER BY similar_contribs DESC
    """
    # people.name         count(*)
    # ---------------------------
    # 'Bridget Betty'       33
    # 'Donald Catherine'    33
    # 'Donald Bob'          30
    # 'Frank Chuck'         28
    # 'Bob Brad'            27

    tx = cypher_transaction()
    tx.append(query, parameters={"username": username, "limit": limit})
    results = _first(tx.commit())
    for record in results:
        name, count = record.values
        print("{0}".format(name))
    return results
