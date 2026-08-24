from neo4j import GraphDatabase

URI = "neo4j+s://c28e52e2.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "W9i-1q8QYTY7x-Y7T8KWiyF_-dv3nWfcE8epNhRK5VY"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_graph_data(data):
    
    buildingage = data.get("buildingage", "")
    geo = data.get("geography", [])
    material = data.get("material_name", "")
    component = data.get("component_name", "")

   
    if "query" in data:
        query = data["query"]
        params = {} 
    else:
       
        query = """
            MATCH (n)-[r]->(m)
            WHERE 
                toLower(n.buildingage) CONTAINS toLower($buildingage) AND
                ANY(g IN $geo WHERE toLower(n.geography) CONTAINS toLower(g)) AND
                toLower(n.material_name) CONTAINS toLower($material) AND
                toLower(n.component_name) CONTAINS toLower($component)
            RETURN n, r, m LIMIT 20
        """
        params = {
            "buildingage": buildingage,
            "geo": geo,
            "material": material,
            "component": component
        }

    with driver.session() as session:
        result = session.run(query, params)
        records = []
        for record in result:
            records.append({
                "n": dict(record["n"]),
                "r": dict(record["r"].items()),
                "m": dict(record["m"])
            })

    return records