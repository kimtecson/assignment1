import json
import sys
import csv
import time
import statistics

# Add the project to path
sys.path.insert(0, '.')

from graph.coordinate import Coordinate
from graph.adjacency_matrix import AdjacencyMatrixGraph
from graph.adjacency_list import AdjacencyListGraph
from maze.maze import Maze
from maze.dfs_generator import generateMazeDFS
from MST.prims import primMST
from MST.kruskals import kruskalMST

# Test configurations
sizes = [10, 20, 50, 100]
densities = [0, 25, 50, 75, 100]
combinations = [
    ("matrix", "prims"),
    ("matrix", "kruskals"),
    ("list", "prims"),
    ("list", "kruskals")
]

MAZES_PER_CONFIG = 10  # Generate 10 different mazes per configuration
WARMUP_RUNS = 2  # Warmup runs (not counted)

results = []
total_configs = len(sizes) * len(densities) * MAZES_PER_CONFIG
total_tests = total_configs * len(combinations)

config_num = 0

print("="*80)
print("MST ALGORITHM PERFORMANCE EXPERIMENT")
print("1 Maze → 4 Algorithm Combinations → Repeat 10× per config")
print("="*80)
print(f"Sizes: {sizes}")
print(f"Densities: {densities}")
print(f"Algorithms: {len(combinations)} combinations")
print(f"Mazes per configuration: {MAZES_PER_CONFIG}")
print(f"Warmup runs: {WARMUP_RUNS}")
print(f"Total mazes: {total_configs}")
print(f"Total tests: {total_tests}")
print("="*80 + "\n")

def convert_matrix_to_list(graph_matrix, rows, cols):
    """Convert adjacency matrix to adjacency list with same edges."""
    graph_list = AdjacencyListGraph(rows, cols)

    # Add all vertices
    for r in range(rows):
        for c in range(cols):
            graph_list.addVertex(Coordinate(r, c))

    # Copy edges from matrix to list (avoid duplicates)
    for v in graph_matrix.getVertices():
        for u in graph_matrix.neighbours(v):
            # Only add each edge once (when v < u)
            if v.getRow() < u.getRow() or (v.getRow() == u.getRow() and v.getCol() < u.getCol()):
                weight = graph_matrix.getWeight(v, u)
                graph_list.addEdge(v, u, weight)

    return graph_list

for n in sizes:
    rows, cols = n, n
    entrance = Coordinate(0, 0)

    for density in densities:
        print(f"\n{'='*80}")
        print(f"Configuration: {n}×{n} maze, {density}% density")
        print(f"{'='*80}")

        # Storage for timing statistics per algorithm
        config_times = {
            (graph_type, mst_algo): []
            for graph_type, mst_algo in combinations
        }

        for maze_num in range(MAZES_PER_CONFIG):
            config_num += 1

            # Generate ONE UNIQUE maze
            graph_matrix = AdjacencyMatrixGraph(rows, cols)
            for r in range(rows):
                for c in range(cols):
                    graph_matrix.addVertex(Coordinate(r, c))

            maze = Maze(graph_matrix)
            maze.setStart(entrance)
            generateMazeDFS(graph_matrix, density, 25)

            # Convert to list representation (SAME maze structure)
            graph_list = convert_matrix_to_list(graph_matrix, rows, cols)

            # Verify both representations have same edge count
            edges_matrix = sum(len(graph_matrix.neighbours(v)) for v in graph_matrix.getVertices()) // 2
            edges_list = sum(len(graph_list.neighbours(v)) for v in graph_list.getVertices()) // 2

            if maze_num == 0:
                print(f"Maze 1: {edges_matrix} edges (verified: matrix={edges_matrix}, list={edges_list})")

            # Test ALL 4 combinations on THIS SAME maze
            maze_results = []

            for graph_type, mst_algo in combinations:
                # Select appropriate graph representation
                graph = graph_matrix if graph_type == "matrix" else graph_list
                mst_func = primMST if mst_algo == "prims" else kruskalMST

                # Warmup runs (stabilize CPU cache, branch prediction)
                for _ in range(WARMUP_RUNS):
                    _ = mst_func(graph)

                # Actual timed run
                start = time.perf_counter()
                mst = mst_func(graph)
                end = time.perf_counter()

                runtime = end - start
                config_times[(graph_type, mst_algo)].append(runtime)

                maze_results.append({
                    'algo': f"{graph_type}+{mst_algo}",
                    'runtime': runtime
                })

                # Record individual result
                results.append({
                    'size': n,
                    'density': density,
                    'graph_type': graph_type,
                    'mst_algo': mst_algo,
                    'maze_num': maze_num,
                    'runtime': runtime
                })

            # Progress indicator - show results for this maze
            progress = (config_num / total_configs) * 100
            print(f"  [{progress:5.1f}%] Maze {maze_num+1}/10: " +
                  " | ".join([f"{r['algo']:15s} {r['runtime']*1000:6.2f}ms" for r in maze_results]))

        # Print statistics for this configuration
        print(f"\n  Configuration Summary ({n}×{n}, {density}%):")
        print(f"  {'Algorithm':<20} | {'Mean (ms)':<12} | {'Median (ms)':<12} | {'Std Dev':<10} | {'Range':<15}")
        print(f"  {'-'*80}")

        for graph_type, mst_algo in combinations:
            times = config_times[(graph_type, mst_algo)]
            mean_ms = statistics.mean(times) * 1000
            median_ms = statistics.median(times) * 1000
            stdev_ms = statistics.stdev(times) * 1000 if len(times) > 1 else 0
            min_ms = min(times) * 1000
            max_ms = max(times) * 1000

            algo_name = f"{graph_type}+{mst_algo}"
            print(f"  {algo_name:<20} | {mean_ms:>10.2f}ms | {median_ms:>10.2f}ms | "
                  f"{stdev_ms:>8.2f}ms | [{min_ms:.1f}, {max_ms:.1f}]")

print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed results to CSV
with open('task_c_results_fair.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['size', 'density', 'graph_type', 'mst_algo', 'maze_num', 'runtime'])
    writer.writeheader()
    writer.writerows(results)

print(f"✅ Detailed results saved to 'task_c_results_fair.csv' ({len(results)} measurements)")

# Also save aggregated statistics
aggregated = []
for n in sizes:
    for density in densities:
        for graph_type, mst_algo in combinations:
            # Get all runtimes for this configuration
            config_results = [r['runtime'] for r in results
                            if r['size'] == n and r['density'] == density
                            and r['graph_type'] == graph_type and r['mst_algo'] == mst_algo]

            if config_results:
                aggregated.append({
                    'size': n,
                    'density': density,
                    'graph_type': graph_type,
                    'mst_algo': mst_algo,
                    'mean': statistics.mean(config_results),
                    'median': statistics.median(config_results),
                    'stdev': statistics.stdev(config_results) if len(config_results) > 1 else 0,
                    'min': min(config_results),
                    'max': max(config_results),
                    'count': len(config_results)
                })

with open('task_c_aggregated_fair.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['size', 'density', 'graph_type', 'mst_algo',
                                           'mean', 'median', 'stdev', 'min', 'max', 'count'])
    writer.writeheader()
    writer.writerows(aggregated)

print(f"✅ Aggregated statistics saved to 'task_c_aggregated_fair.csv'")
print("\n" + "="*80)
print("EXPERIMENT COMPLETE")
print("="*80)
