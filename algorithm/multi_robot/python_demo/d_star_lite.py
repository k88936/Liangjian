from priority_queue import PriorityQueue, Priority
from grid import OccupancyGridMap
import numpy as np
from utils import heuristic, Vertex, Vertices
from typing import Dict, List

from type import UNOCCUPIED, OBSTACLE


class DStarLite:
    def __init__(self, map: OccupancyGridMap, s_start: (int, int), s_goal: (int, int), cost, view_range=5):
        """
        :param map: the ground truth map of the environment provided by gui
        :param s_start: start location
        :param s_goal: end location
        """
        self.ground_truth_map = map
        self.raw_cost = cost.copy()
        self.view_range = view_range

        # algorithm start
        self.s_start = (s_start[0], s_start[1])
        self.s_goal = (s_goal[0], s_goal[1])
        self.s_last = (self.s_start[0], self.s_start[1])

        self.k_m = 0  # accumulation
        self.U = PriorityQueue()
        self.rhs = self.raw_cost.copy()

        self.g = self.raw_cost.copy()
        self.g[self.s_start] = np.inf

        self.slam_map = self.ground_truth_map.copy()


    def calculate_key(self, s: (int, int)):
        """
        :param s: the vertex we want to calculate key
        :return: Priority class of the two keys
        """
        k1 = min(self.g[s], self.rhs[s]) + heuristic(self.s_start, s) + self.k_m
        k2 = min(self.g[s], self.rhs[s])
        return Priority(k1, k2)

    def c(self, u: (int, int), v: (int, int)) -> float:
        """
        calcuclate the cost between nodes
        :param u: from vertex
        :param v: to vertex
        :return: euclidean distance to traverse. inf if obstacle in path
        """
        if not self.slam_map.is_unoccupied(u) or not self.slam_map.is_unoccupied(v):
            return float('inf')
        else:
            return heuristic(u, v)

    def contain(self, u: (int, int)) -> (int, int):
        return u in self.U.vertices_in_heap

    def update_vertex(self, u: (int, int)):
        if self.g[u] != self.rhs[u] and self.contain(u):
            self.U.update(u, self.calculate_key(u))
        elif self.g[u] != self.rhs[u] and not self.contain(u):
            self.U.insert(u, self.calculate_key(u))
        elif self.g[u] == self.rhs[u] and self.contain(u):
            self.U.remove(u)

    def compute_shortest_path(self):
        while self.U.top_key() < self.calculate_key(self.s_start) or self.rhs[self.s_start] > self.g[self.s_start]:
            u = self.U.top()
            k_old = self.U.top_key()
            k_new = self.calculate_key(u)

            if k_old < k_new:
                self.U.update(u, k_new)
            elif self.g[u] > self.rhs[u]:
                self.g[u] = self.rhs[u]
                self.U.remove(u)
                pred = self.slam_map.succ(vertex=u)
                for s in pred:
                    if s != self.s_goal:
                        self.rhs[s] = min(self.rhs[s], self.c(s, u) + self.g[u])
                    self.update_vertex(s)
            else:
                self.g_old = self.g[u]
                self.g[u] = float('inf')
                pred = self.slam_map.succ(vertex=u)
                pred.append(u)
                for s in pred:
                    if self.rhs[s] == self.c(s, u) + self.g_old:
                        if s != self.s_goal:
                            min_s = float('inf')
                            succ = self.slam_map.succ(vertex=s)
                            for s_ in succ:
                                temp = self.c(s, s_) + self.g[s_]
                                if min_s > temp:
                                    min_s = temp
                            self.rhs[s] = min_s
                    self.update_vertex(u)

    def rescan(self):
        global_position = self.s_start
        def update_changed_edge_costs(local_grid: Dict) -> Vertices:
            vertices = Vertices()
            for node, value in local_grid.items():
                # if obstacle
                if value == OBSTACLE:
                    if self.slam_map.is_unoccupied(node):
                        v = Vertex(pos=node)
                        succ = self.slam_map.succ(node)
                        for u in succ:
                            v.add_edge_with_cost(succ=u, cost=self.c(u, v.pos))
                        vertices.add_vertex(v)
                        self.slam_map.set_obstacle(node)
                else:
                    # if white cell
                    if not self.slam_map.is_unoccupied(node):
                        v = Vertex(pos=node)
                        succ = self.slam_map.succ(node)
                        for u in succ:
                            v.add_edge_with_cost(succ=u, cost=self.c(u, v.pos))
                        vertices.add_vertex(v)
                        self.slam_map.remove_obstacle(node)
            return vertices

        # rescan local area
        local_observation = self.ground_truth_map.local_observation(global_position=global_position,
                                                                    view_range=self.view_range)
        return update_changed_edge_costs(local_grid=local_observation)

    def replan(self, robot_position: (int, int)):
        self.s_start = robot_position

        if self.s_start == self.s_goal:
            return None

        # scan graph for changed costs
        changed_edges_with_old_cost = self.rescan()
        if not changed_edges_with_old_cost.isEmpty():
            self.k_m += heuristic(self.s_last, self.s_start)
            self.s_last = self.s_start

            # for all directed edges (u,v) with changed edge costs
            vertices = changed_edges_with_old_cost.vertices
            for vertex in vertices:
                v = vertex.pos
                succ_v = vertex.edges_and_c_old
                for u, c_old in succ_v.items():
                    c_new = self.c(u, v)
                    if c_old > c_new:
                        if u != self.s_goal:
                            self.rhs[u] = min(self.rhs[u], self.c(u, v) + self.g[v])
                    elif self.rhs[u] == c_old + self.g[v]:
                        if u != self.s_goal:
                            min_s = float('inf')
                            succ_u = self.slam_map.succ(vertex=u)
                            for s_ in succ_u:
                                temp = self.c(u, s_) + self.g[s_]
                                if min_s > temp:
                                    min_s = temp
                            self.rhs[u] = min_s
                        self.update_vertex(u)

            self.compute_shortest_path()

        if self.rhs[self.s_start] == float('inf'):
            return None

        min_s = float('inf')
        arg_min = None
        for s_ in self.slam_map.succ(self.s_start,avoid_obstacles=False):
            temp = self.c(self.s_start, s_) + self.g[s_]
            if temp < min_s:
                min_s = temp
                arg_min = s_

        return arg_min
