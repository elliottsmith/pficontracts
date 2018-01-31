#!/usr/bin/env python
import sys, os
from py2neo import Node, Graph, Relationship

sys.path.append(os.path.abspath(os.path.expanduser('~/.apikeys')))
from apikeys import neo4j_pass, neo4j_user

graph = Graph('http://%s:%s@localhost:7474' % (neo4j_user, neo4j_pass))
graph.delete_all()

company = Node('Company', name='MILK')
graph.create(company)

people = ['Alice', 'Bob', 'Terry', 'Sam', 'Eve']
people_nodes = []
for p in people:
	n = Node('Person', name=p)
	r = Relationship(n, 'WORKS FOR', company)
	graph.create(r)