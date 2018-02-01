#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, csv
from py2neo import Node, Graph, Relationship

sys.path.append(os.path.abspath(os.path.expanduser('~/.apikeys')))
from apikeys import neo4j_pass, neo4j_user

# data source
current_data = '../data/31.03.2016.csv'
hyperlink = 'https://www.gov.uk/government/publications/private-finance-initiative-and-private-finance-2-projects-2016-summary-data'

def data_to_dict():
	"""
	Read in the data source, convert header names and row/column values into a list of dictionaries.
	One dictionary per project.
	"""
	pfi_data = []
	
	with open(current_data, 'rb') as data:
		reader = csv.reader(data)

		# skip empty header before the real header
		next(reader, None)
		headers = next(reader, None)

		for row in reader:

			project_data = {}

			for idx, column in enumerate(row):
				project_data[headers[idx]] = column

			# append to pfi_data
			pfi_data.append(project_data)

	return pfi_data

def prepare_plot_data(parsed_data):
	"""
	For every project, make a graph node. For all it's equity partners, make a node and link it to
	the project node.

	An attempt is made to match differently spelt equity partners, so that multiple nodes dont exist
	for what is essentially the same company / equity partner
	"""

	graph = Graph('http://%s:%s@localhost:7474' % (neo4j_user, neo4j_pass))
	graph.delete_all()

	for d in parsed_data:
		# get the department name
		pfi_department_name = d['Department']
		dept_matches = list(graph.find('Department', property_key='name', property_value=pfi_department_name))

		# if the dept node doesnt already exist, make it
		if len(dept_matches) == 0:
			dept = Node('Department', name=pfi_department_name)
			graph.create(dept)
		else:
			dept = dept_matches[0]

		# get the name of the project
		pfi_project_name = d['Project Name']

		# create project and create relationship to dept
		project = Node('Project', name=pfi_project_name)
		graph.create(project)
		rel = Relationship(project, 'PROJECT OF', dept)
		graph.create(rel)

		# potentially six equity partners
		for num in ['1', '2', '3', '4', '5', '6']:

			equity_partner = 'Equity Holder %s: Name' % num

			if equity_partner in d.keys():

				if d[equity_partner] != '':

					equity_name = d[equity_partner]
					equity_matches = list(graph.find('Company', property_key='name', property_value=equity_name))

					# if the company doesnt aleady exist, make it
					if len(equity_matches) == 0:
						company = Node('Company', name=equity_name)
						graph.create(company)
					else:
						company = equity_matches[0]

					# create relationship between company and project
					rel = Relationship(company, 'AWARDED', project)
					graph.create(rel)

data_dicts = data_to_dict()
plot_data = prepare_plot_data(data_dicts)
