import rdflib
import queries as q


###############################################################
################# Freddy Test 23.11.19 ########################
# -- Sorting by SQL is missing:
#       We want to sort by SQL so that all triples related to the same SQL Statement will be executed sequentialy
#       This way only the result of the last sql statement hast to be cached, by our code
#       How to sort the statements can be a task. For not it would be enough by name/alpha-numeric
#       Queries that are semantic similar, or by involved table, could be a way to go in the future
###############################################################
class BaseSubjectMapTriple:
	def __init__(self, id, sql,  subject, predicate, object):
		self.sql = sql
		self.subject = subject
		self.predicate = predicate
		self.object = object
		self.id = id
	def __str__(self):
		return  ": " + self.sql + " " + self.subject + " " + self.predicate + " " + self.object
	def __repr__(self):
		return ": " + self.sql + " " + self.subject + " " + self.predicate + " " + self.object
	def getObject(self):
		return self.object
	def getPredicate(self):
		return self.predicate
	def getSubject(self):
		return str(self.subject)
	def getSql(self):
		return self.sql
	def getId(self):
		return str(self.id)


class ColumnTriple(BaseSubjectMapTriple):
	def __init__(self, id, sql,  subject, predicate, object):
		BaseSubjectMapTriple.__init__(self, id, sql, subject, predicate, object)
		self.type = "Column"
	def __str__(self):
		return BaseSubjectMapTriple.__str__(self)
	def __repr__(self):
		return BaseSubjectMapTriple.__repr__(self)

class TemplateTriple(BaseSubjectMapTriple):
	def __init__(self, id, sql,  subject, predicate, object):
		BaseSubjectMapTriple.__init__(self, id, sql, subject, predicate, object)
		self.type = "Template"
	def __str__(self):
		return BaseSubjectMapTriple.__str__(self)
	def __repr__(self):
		return BaseSubjectMapTriple.__repr__(self)

class AbstractColumnMapTriple:
	def __init__(self, id, subject, predicate, object):
		self.subject = subject
		self.object = object
		self.predicate = predicate
		self.id = id
	def getKey(self):
		return str(self.id)
	def getPredicate(self):
		return str(self.predicate)
	def getObject(self):
		return str(self.object)
	def getSubject(self):
		return self.subject

class ColumnColumnMapTriple(AbstractColumnMapTriple):
	def __init__(self, id, key, predicate, object):
		AbstractColumnMapTriple.__init__(self, id, key, predicate, object)
		self.type = "ColumnMap"
	def getType(self):
		return self.type
class TemplateColumnMapTriple(AbstractColumnMapTriple):
	def __init__(self, id, key, predicate, object):
		AbstractColumnMapTriple.__init__(self, id, key, predicate, object)
		self.type = "TemplateMap"
	def getType(self):
		return self.type

def exeucteSparqlQuery(sparqlQuery):
    #Create rdf graph and load file to graph
    global graph
    result = graph.query(sparqlQuery) #Execute sparql query
    return result
#?tableName ?subjectTemplate ?class
def handleSubjectMapTypeTableTemplate(sparqlResult):
    triple_list = []
    for (id, tableName, template, class_n) in sparqlResult:
        sqlTable = "select * from " + tableName
        t_n = TemplateTriple(id, sqlTable, template,  "rdf:type", class_n)
        triple_list.append(t_n)
    return triple_list

#?tableName ?subjectColumn ?class
def handleSubjectMapTypeTableColumn(sparqlResult):
    triple_list = []
    for (id, tableName, subjectColumn, class_n) in sparqlResult:
        sqlTable = "select * from " + tableName
        t_n = ColumnTriple(id, sqlTable, subjectColumn,  "rdf:type", class_n)
        triple_list.append(t_n)
    return triple_list

def handleSubjectMapTypeQueryTemplate(sparqlResult):
    triple_list = []
    for (id, sqlquery, template, class_n) in sparqlResult:
        t_n = TemplateTriple(id, sqlquery, template,  "rdf:type", class_n)
        triple_list.append(t_n)
    return triple_list

# ?sqlQuery ?subjectColumn ?class
def handleSubjectMapTypeQueryColumn(sparqlResult):
    triple_list = []
    for (id, sqlQuery, subjectColumn, class_n) in sparqlResult:
        t_n = ColumnTriple(id, sqlQuery, subjectColumn,  "rdf:type", class_n)
        triple_list.append(t_n)
    return triple_list

def executeFuctionForQueryResult(queryType, rows):
    if queryType == 'typeTableTemplate':
        return handleSubjectMapTypeTableTemplate(rows)
    elif queryType == 'typeTableColumn':
        return handleSubjectMapTypeTableColumn(rows)
    elif queryType == 'typeQueryTemplate':
        return handleSubjectMapTypeQueryTemplate(rows)
    elif queryType == 'typeQueryColumn':
        return handleSubjectMapTypeQueryColumn(rows)

allSubjectMapStatementsDict = {query.name: query.value for query in q.R2RMLSubjectMapQueries}
allObjectMapStatementsDict = {query.name: query.value for query in q.R2RMLObjectMapQueries }
allSubjectTriples = []
subjectToColumnMap = {}
#print(allTabelStatementsDict)
#allTabelStatementsDict = {'typeTableTemplate' : q.R2RMLqueries.typeTableTemplate.value, 'typeQueryTemplate' : q.R2RMLqueries.typeQueryTemplate.value}

def createAllSubjectTriples():
    global allSubjectTriples
    for key in allSubjectMapStatementsDict:
        sparqlQuery = allSubjectMapStatementsDict[key]
        rows = exeucteSparqlQuery(sparqlQuery)
        result = executeFuctionForQueryResult(key, rows)
        if result:
        	allSubjectTriples = allSubjectTriples + result
    allSubjectTriples.sort(key=lambda x: x.getSql())

# That has to be changed to map by tripleMapId. Otherwise a missmatch
def createAllColumnTriples():
	global subjectToColumnMap
	for key in allObjectMapStatementsDict:
		sparql = allObjectMapStatementsDict[key]
		rows = exeucteSparqlQuery(sparql)
		for (id, subjectTemplate, predicate, column) in rows:
			if key.find("ObjectTemplate") > 0:
				columnTriple = TemplateColumnMapTriple(id, subjectTemplate, predicate, column)
			elif key.find("ObjectColumn") > 0: # ObjectColumn
				columnTriple = ColumnColumnMapTriple(id, subjectTemplate, predicate, column)
			else:
				print("Not defined query is right now iterated. Please adapt query")
				break
			subjectKey = columnTriple.getKey()
			subjectToColumnMap[columnTriple.getKey()] = columnTriple

def setup():
	global graph
	graph = rdflib.Graph()
	graph.load("r2rml.n3", format="n3")
	createAllSubjectTriples()
	createAllColumnTriples()
