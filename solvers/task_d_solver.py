# -------------------------------------------------
# EDIT THIS FILE TO IMPLEMENT TASK D.
# Functions for your solver.
#
# __author__ = 'YOUR NAME HERE'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from graph.coordinate import Coordinate
from graph.graph import Graph
from solvers.util import estimate_subtree_weight, dfsBacktrack, generate_actions_from_paths


def task_d_explore(graph: Graph, current: Coordinate, visited: set,
                   all_paths: list[list[Coordinate]], explorer_id: int = 0) -> int:
    """
    Returns a solution to the maze using YOUR exploration strategy. See always_clone and no_clone for inspiration.

    The expectation is that all_paths contains a list of lists. Each list is a traversal that each clone/sorcerer completed
    For example:
    [[Coordinates(0, 0), Coordinates(0, 1), Coordinates(0, 2), Coordinates(1, 2), Coordinates(1, 3), Coordinates(2, 3),
    Coordinates(3, 3), Coordinates(3, 2), Coordinates(2, 2), Coordinates(2, 1), Coordinates(2, 0), Coordinates(3, 0), Coordinates(3, 1)],
    [Coordinates(1, 3), Coordinates(0, 3)],
    [Coordinates(2, 0), Coordinates(1, 0), Coordinates(1, 1)]]

    The above output implies that the original sorcerer walked from (0,0)->(0,1)->...->(1,3)->made a clone->(3,2)->...
    We made 2 clones because we have 3 sets of lists (one original sorcerer and 2 clones). Clones MUST start their
    journey from the exact cell they are made from.

    You only have to handle the path generation - calculating the cost is handled for you via generate_actions_from_paths

    @param graph: The maze graph to traverse. Each node represents a coordinate, and edges have associated weights.
    @param start: The starting coordinate for the original explorer. All traversal begins from this point.
    @param clone_cost: The fixed cost incurred each time a clone is spawned. This cost is added to both the spawner
                       and the clone.

    @return: clone_count: The total number of clones spawned (equal to len(all_paths) - 1).
    """
    if explorer_id == len(all_paths):
        all_paths.append([current])
    else:
        all_paths[explorer_id].append(current)

    path = all_paths[explorer_id]
    visited.add(current)

    # put your exploration below!
    while True:
        # Get all unvisited neighbors with their edge weights
        unvisited = [
            (neighbor, graph.getWeight(current, neighbor))
            for neighbor in graph.neighbours(current)
            if neighbor not in visited
        ]

        # Base case: no more unvisited neighbors
        if not unvisited:
            break

        # Single neighbor: just continue without branching
        if len(unvisited) == 1:
            neighbor, _ = unvisited[0]
            current = neighbor
            path.append(current)
            visited.add(current)
            continue

        # Multiple neighbors: need to decide on cloning strategy
        # Calculate cost metrics for each branch
        branch_metrics = []
        for neighbor, edge_weight in unvisited:
            # Estimate total weight of the subtree
            subtree_weight = estimate_subtree_weight(graph, neighbor, visited.copy())

            # Cost to explore and return = 2 × (edge_weight + subtree_weight)
            # We have to go there AND come back if we don't clone
            backtrack_cost = 2 * (edge_weight + subtree_weight)

            branch_metrics.append({
                'neighbor': neighbor,
                'edge_weight': edge_weight,
                'subtree_weight': subtree_weight,
                'backtrack_cost': backtrack_cost
            })

        # Sort by subtree weight (ascending) to handle smallest branches first
        branch_metrics.sort(key=lambda x: x['subtree_weight'])

        # Decision: clone for branches where backtracking is more expensive than cloning
        branches_to_clone = []
        main_branch = None

        for branch in branch_metrics[:-1]:  # All but the largest
            # Clone if: cost of backtracking > cost of cloning
            # The clone saves us: backtrack_cost - edge_weight (we still pay edge once)
            savings = branch['backtrack_cost'] - branch['edge_weight']

            if savings > clone_cost:
                branches_to_clone.append(branch)
            else:
                # Not worth cloning, we'll explore it ourselves later
                pass

        # The largest branch becomes our main path (we explore it personally)
        main_branch = branch_metrics[-1]

        # Spawn clones for beneficial branches
        for branch in branches_to_clone:
            neighbor = branch['neighbor']
            visited.add(neighbor)

            # Create new explorer path starting from current junction
            clone_id = len(all_paths)

            # Recursively explore with the clone
            task_d_explore(graph, neighbor, visited, all_paths, clone_id, clone_cost)

            # Add junction to start of clone's path (spawn point)
            all_paths[clone_id].insert(0, current)

        # Now explore branches we decided NOT to clone (if any)
        for branch in branch_metrics[:-1]:
            if branch not in branches_to_clone:
                neighbor = branch['neighbor']
                if neighbor not in visited:
                    # Explore this branch ourselves
                    path.append(neighbor)
                    visited.add(neighbor)

                    # Recursively explore the subtree
                    _explore_subtree(graph, neighbor, visited, path)

                    # Backtrack to junction
                    path.append(current)

        # Finally, commit to the main (largest) branch
        main_neighbor = main_branch['neighbor']
        current = main_neighbor
        path.append(current)
        visited.add(current)

    return len(all_paths) - 1  # number of current clones

def _explore_subtree(graph: Graph, node: Coordinate, visited: set, path: list[Coordinate]):
    """
    Helper function to explore a subtree using DFS without cloning.
    Used when we've decided to explore a branch ourselves rather than clone.
    """
    neighbors = [n for n in graph.neighbours(node) if n not in visited]

    for neighbor in neighbors:
        path.append(neighbor)
        visited.add(neighbor)
        _explore_subtree(graph, neighbor, visited, path)
        path.append(node)


def task_d_solver(graph: Graph, start: Coordinate, clone_cost: int) -> tuple[list[list[Coordinate]], int, int]:
    """
    Solves the maze using cost-aware clone-based DFS.

    Spawns clones only when the cost of exploring and returning from a subtree exceeds the clone cost.
    Tracks each explorer's path and actions, and returns the full traversal history.

    @param graph: The maze graph to traverse.
    @param start: The starting coordinate for the original explorer.
    @param clone_cost: Fixed cost incurred each time a clone is spawned.

    @return: A tuple containing:
        - all_paths: A list of paths taken by each explorer (original + clones).
        - max_total_cost: The highest cumulative cost incurred by any explorer (movement + clone costs).
        - clone_count: The total number of clones spawned (equal to len(all_paths) - 1).
    """
    visited = set()
    all_paths = []

    # the below function is your method for generating paths!
    task_d_explore(graph, start, visited, all_paths=all_paths)

    # Post-process actions from paths
    all_actions = generate_actions_from_paths(graph, all_paths, clone_cost)

    max_total_cost = max(sum(actions) for actions in all_actions)
    clone_count = len(all_paths) - 1

    return all_paths, max_total_cost, clone_count
