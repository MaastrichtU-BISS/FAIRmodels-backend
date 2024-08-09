from rdflib import Graph, URIRef

class JSONLDParser:
    def __init__(self, json_ld_object=None):
        """
        Initialize a JSON-LD parser.
        """
        self.__graph = Graph()
        if json_ld_object:
            self.parse_json_ld(json_ld_object)
    
    def parse_json_ld(self, json_ld_object):
        """
        Parse a JSON-LD object into an RDF graph.
        """
        self.__graph.parse(data=json_ld_object, format='json-ld')
    
    def get_value(self, predicate, subject=None):
        """
        Get the value of a predicate for a subject. If no subject is given, the first value found is returned.
        """
        if type(predicate)!=URIRef: predicate = URIRef(predicate)
        if subject:
            if type(subject)!=URIRef: subject = URIRef(subject)

        for s, p, o in self.__graph.triples((subject,  predicate, None)):
            return o.value
