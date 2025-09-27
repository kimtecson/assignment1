# -------------------------------------------------
# EDIT THIS FILE TO IMPLEMENT ADJACENCY LIST.
# Class for Adjacency List representation of Graph.
#
# __author__ = 'Kimberly Tecson'
# __copyright__ = 'Copyright 2025, RMIT University'
# -------------------------------------------------

from typing import List, Dict, Tuple
from graph.graph import Graph
from graph.coordinate import Coordinate


class AdjacencyListGraph(Graph):
    """
    Graph implementation using an adjacency list.
    Vertices are Coordinates (rooms), and edges are weighted paths.
    A weight of 0 between adjacent cells means a wall; weight > 0 means traversable with cost.
    """

    def __init__(self, rows: int, cols: int):
        """
        Initializes the graph with empty adjacency lists.

        @param rows: Number of rows in the maze.
        @param cols: Number of columns in the maze.
        """
        self.rows = rows
        self.cols = cols
        self.size = rows * cols

        # Set of all vertices
        self.vertices: List[Coordinate] = []

        # Adjacency list: Coordinate → List[Tuple[Coordinate, weight]]
        self.adj_list: Dict[Coordinate, List[Tuple[Coordinate, int]]] = {}

    def addVertex(self, label: Coordinate):
        """
        Adds a vertex to the graph.

        @param label: Coordinate of the room.
        """
        if label not in self.adj_list:
            self.adj_list[label] = []
            self.vertices.append(label)

    def addVertices(self, vertLabels: List[Coordinate]):
        """
        Adds multiple rooms to the graph.

        @param vertLabels: List of Coordinates.
        """
        for label in vertLabels:
            self.addVertex(label)

    def addEdge(self, vert1: Coordinate, vert2: Coordinate, weight: int = 1) -> bool:
        """
        Adds a traversable path between two rooms if:
        1) No edge already exists,
        2) Both rooms are in the graph,
        3) The rooms are adjacent (orthogonally).

        @param vert1: Source room.
        @param vert2: Destination room.
        @param weight: Movement cost. Default is 1.

        @returns True if edge added successfully, otherwise False.
        """
        # Condition: both must be in the graph and is adjacent
        if self._validateVertices(vert1, vert2) is False:
            return False

        # Condition: edge already exists (check if weight > 0)
        if self.hasEdge(vert1, vert2):
            return False

        # Add undirected edge
        self.adj_list[vert1].append((vert2, weight))
        self.adj_list[vert2].append((vert1, weight))

        return True

    def updateWall(self, vert1: Coordinate, vert2: Coordinate, hasWall: bool, weight: int = 1) -> bool:
        """
        Updates wall status between two rooms.

        @param vert1: First room.
        @param vert2: Second room.
        @param hasWall: True to add wall (remove edge), False to remove wall (add edge).
        @param weight: if we are removing a wall, what is the edge weight?

        @returns True if update successful.
        """
        # Condition: both must be in the graph and is adjacent
        if self._validateVertices(vert1, vert2) is False:
            return False

        # Remove existing edge first (if any)
        self.adj_list[vert1] = [(v, w) for v, w in self.adj_list[vert1] if v != vert2]
        self.adj_list[vert2] = [(v, w) for v, w in self.adj_list[vert2] if v != vert1]

        # If hasWall is False, add an edge with the specified weight
        # If hasWall is True, don't add anything (wall = no edge)
        if not hasWall:
            self.adj_list[vert1].append((vert2, weight))
            self.adj_list[vert2].append((vert1, weight))
        return True

    def print(self):
        """
        Prints the adjacency list of the graph to the terminal. Like

        (0, 0) -> [(0, 1), 1; (1, 0), 2]
        (0, 1) -> [(0, 0), 1; (1, 1), 3]
        ...

        Useful for debugging.

        @returns None
        """
        for u in self.vertices:
            edges = self.adj_list.get(u, [])
            edge_strs = [f"({v.getRow()}, {v.getCol()}), {w}" for v, w in edges]
            print(f"({u.getRow()}, {u.getCol()}) -> [{'; '.join(edge_strs)}]")

    def removeEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Removes the path between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if edge removed successfully.
        """
        return self.updateWall(vert1, vert2, hasWall=True)


    def hasVertex(self, label: Coordinate) -> bool:
        """
        Checks if a room exists in the graph.

        @param label: Coordinate of the room.

        @returns True if room exists.
        """
        return label in self.adj_list

    def hasEdge(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a traversable path exists between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if edge exists and is traversable.
        """
        if vert1 in self.adj_list and vert2 in self.adj_list:
            # Check if vert2 is in vert1's adjacency list
            for neighbor, weight in self.adj_list[vert1]:
                if neighbor == vert2:
                    return True
        return False

    def getWallStatus(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Checks if a wall exists between two rooms.

        @param vert1: First room.
        @param vert2: Second room.

        @returns True if wall exists (no edge), False otherwise.
        """
        # If vertices are adjacent but not in each other's adjacency lists, it's a wall
        if vert1.isAdjacent(vert2):
            return not self.hasEdge(vert1, vert2)

        # If not adjacent, it's not a wall (just not connected)
        return False

    def getWeight(self, vert1: Coordinate, vert2: Coordinate) -> int:
        """
        Returns the weight between two coordinates if an edge exists.

        @returns positive integer if edge exists, 0 otherwise.
        """
        if vert1 in self.adj_list and vert2 in self.adj_list:
            for neighbor, weight in self.adj_list[vert1]:
                if neighbor == vert2:
                    return weight
        return 0

    def getVertices(self) -> List[Coordinate]:
        return self.vertices

    def neighbours(self, label: Coordinate) -> List[Coordinate]:
        """
        Retrieves all accessible adjacent rooms.

        @param label: Coordinate of the room.

        @returns List of neighbouring Coordinates.
        """
        if not self.hasVertex(label):
            return []

        neighbors = []

        for neighbor, weight in self.adj_list[label]:
            # All edges in the adjacency list are traversable (no walls)
            neighbors.append(neighbor)

        return neighbors

    def _validateVertices(self, vert1: Coordinate, vert2: Coordinate) -> bool:
        """
        Helper method to validate that two vertices exist and are adjacent.

        @param vert1: First vertex to validate.
        @param vert2: Second vertex to validate.
        @returns True if both vertices exist in graph and are adjacent, False otherwise.
        """
        return (vert1 in self.adj_list and
                vert2 in self.adj_list and
                vert1.isAdjacent(vert2))
