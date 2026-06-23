from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
async def parse_pipeline(request: Request):
    data = await request.json()
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    
    num_nodes = len(nodes)
    num_edges = len(edges)
    
    # --- DAG Check (Cycle Detection) ---
    # Create adjacency list for the graph
    graph = {node["id"]: [] for node in nodes}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source in graph:
            graph[source].append(target)
            
    # DFS to detect cycles
    visited = {} # node_id -> int (0: unvisited, 1: visiting, 2: visited)
    
    def has_cycle(node_id):
        visited[node_id] = 1 # Mark as currently visiting
        for neighbor in graph.get(node_id, []):
            state = visited.get(neighbor, 0)
            if state == 1:
                return True # Cycle detected (back-edge)
            elif state == 0:
                if has_cycle(neighbor):
                    return True
        visited[node_id] = 2 # Mark as fully visited
        return False
        
    is_dag = True
    for node in nodes:
        node_id = node["id"]
        if visited.get(node_id, 0) == 0:
            if has_cycle(node_id):
                is_dag = False
                break
                
    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "is_dag": is_dag
    }
