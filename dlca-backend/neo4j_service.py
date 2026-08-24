from flask import Blueprint, request, jsonify
from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship, Path

bp = Blueprint("neo4j_service", __name__)

URI = "neo4j+s://c28e52e2.databases.neo4j.io"
AUTH = ("neo4j", "W9i-1q8QYTY7x-Y7T8KWiyF_-dv3nWfcE8epNhRK5VY")

driver = GraphDatabase.driver(URI, auth=AUTH, max_connection_lifetime=200)

@bp.route("/query", methods=["POST"])
def query_graph():
    
    data = request.json
    cypher_query = data.get("cypher", "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50")
    
    nodes_dict = {}
    links_dict = {} 
    
    try:
        with driver.session() as session:
            result = session.run(cypher_query)
            for record in result:
                
                for value in record.values():
                    
                    if isinstance(value, Node):
                        nodes_dict[value.element_id] = {
                            "id": value.element_id, 
                            "label": list(value.labels)[0] if value.labels else "Unknown",
                            **dict(value)
                        }
                    
                    elif isinstance(value, Relationship):
                        links_dict[value.element_id] = {
                            "source": value.start_node.element_id,
                            "target": value.end_node.element_id,
                            "type": value.type,
                            "id": value.element_id
                        }
                    
                    elif isinstance(value, Path):
                        for n in value.nodes:
                            nodes_dict[n.element_id] = {"id": n.element_id, "label": list(n.labels)[0] if n.labels else "Unknown", **dict(n)}
                        for r in value.relationships:
                            links_dict[r.element_id] = {"source": r.start_node.element_id, "target": r.end_node.element_id, "type": r.type, "id": r.element_id}

        return jsonify({
            "nodes": list(nodes_dict.values()), 
            "links": list(links_dict.values())
        })
        
    except Exception as e:
        print(f"[error] Neo4j query failed: {e}")
        return jsonify({"error": str(e), "nodes": [], "links": []}), 500