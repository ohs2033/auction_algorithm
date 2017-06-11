#-*- encoding: utf-8 -*-
import random
import timeit
import subprocess
from collections import deque

class Auction(object): 

    """
    변수 설명:
        matrix: bidder - goods 사이의 weight(value)를 나타내는 2차원 list
        assignments: 현재 상품(key)의 입찰자가 누구인지(value) 할당 관계를 나타내는 dictonary.
        q: 현재 goods에 할당되지 않은 bidder들을 담고 있는 queue(선입선출의 자료구조, python standard library로 구현)
        n: goods, 또는 bidder의 수(goods와 bidder의 수는 반드시 같아야 함.)
        price_arr: 입찰이 이루어질때마다 update되는 상품의 가격. (초기에 모두 0으로 시작함.)
        epsilon: 알고리즘의 종료를 보장하기 위한 실수값으로서 1/(n+1)로 계산된다.
    """

    def __init__(self):
        self._assignments = {}
        self._matrix = [[0]]
        self._q = deque()
        self._n = 1
        self._price_arr = [0] * self._n
        self._epsilon = 0

    @property
    def matrix(self):
        return self._matrix
    
    @property
    def assignments(self):
        # format below
        for key, value in self._assignments.iteritems():
            print '(A{1}), (O{0})'.format(value + 1, key + 1)
    
    @matrix.setter
    def matrix(self, matrix):
        n = len(matrix)

        # check to make sure there is the same number of agents and objects
        if n is 0: raise Exception("matrix must be larger than 0")
        for i in matrix:
            if len(i) is not n: raise Exception("matrix must have same number of rows and columns")

        # 변수들을 초기화한다.
        self._matrix = matrix
        self._n = len(matrix)
        self._q = deque(range(0, self._n))
        self._price_arr = [0] * self._n
        self._epsilon = 1.0 / (1 + self._n)
        _assignments = {}


    def solve_auction(self):
        """Return the string representing the solution to the assignment problem."""
        start_time = timeit.default_timer()
        while len(self._q) > 0:
            # remove unassigned agent from the stack
            agent = self._q.popleft()

            # calculate current utility of agent -- this is not calculating correctly
            utility_arr = self._compute_utility_arr(agent)

            # pull out two largest values
            (x, px, py) = self._two_largest(utility_arr)

            # need an if or else it'll keep going
            self._if_assigned_replace(x, agent)

            # modify the price
            self._make_bid(x, px, py)

        elapsed = timeit.default_timer() - start_time
        print elapsed

    def _if_assigned_replace(self, x, agent):
        if x in self._assignments:
            if self._assignments[x] is not agent:
                self._q.append(self._assignments[x])
        self._assignments[x] = agent

    def _compute_utility_arr(self, agent):
        return [u - p for u, p in zip(self._matrix[agent], self._price_arr)]

    def _two_largest(self, utility_arr):
        """Returns a list of the largest index and second_largest index"""
        largest, second_largest = None, None
        for x in utility_arr:
            if x >= largest:
                largest, second_largest = x, largest
            elif x > second_largest:
                second_largest = x
        return utility_arr.index(largest), largest, second_largest

    def _make_bid(self, x, px, py):
        #
        bid_increment =  self._epsilon
        self._price_arr[x] = self._price_arr[x] + bid_increment

    def _compute_total_value(self):
        """Return the optimal LP solution's final total"""
        total = 0
        for obj, agent in self._assignments.iteritems():
            total += self._matrix[agent][obj]

        print 'optimal solution: {}'.format(total)
        return total

    def gen_random(self, n, M):
        """Set the random sqaure matrix of size n"""
        m = []
        for i in range(0, n):
            m.append([])
            for j in range(0, n):
                m[i].append(random.randint(0, M-1))

        self.matrix = m

    def compute_per_agent_average(self):
        total = self._compute_total_value()
        avg = float(total) / self._n
        return avg

ac = Auction()

mat = [
    [30 , 37 , 40 , 28 , 40],
    [40 , 24 , 27 , 21 , 36],
    [40 , 32 , 33 , 30 , 35],
    [25 , 38 , 40 , 36 , 36],
    [29 , 62 , 41 , 34 , 39]
]

print setattr(ac, 'matrix', mat)
ac.solve_auction()
print ac.assignments
avg = ac.compute_per_agent_average()
print 'average value is:',avg
