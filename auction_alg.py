import random
import timeit
import subprocess
from collections import deque

class Auction(object): 
	"""Auction class used to naively solve the assignment problem.

		This class includes methods to generate a random matrix n x n and 
		methods to convert the auction algorithm into a runnable glkp linear program.

	Attributes:
		matrix: A two dimensional square list representing object/agent utility mappings.
		assignments: A dictionary containing object / agent pairings (indexed by object).
		q: A queue (implemented with a deque) that keeps track of unassigned agents.
		n: An integer representing the number of objects / agents there are.
		price_arr: An array representing the prices of the bids on the objects by the agents.
		epsilon: A small float added to the bids to ensure the algorithm terminates.
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
			print '(A{0}), (O{1})'.format(value + 1, key + 1)
	
	@matrix.setter
	def matrix(self, matrix):
		n = len(matrix)

		# check to make sure there is the same number of agents and objects
		if n is 0: raise Exception("matrix must be larger than 0")
		for i in matrix:
			if len(i) is not n: raise Exception("matrix must have same number of rows and columns")

		# set values
		self._matrix = matrix
		self._n = len(matrix)
		self._q = deque(range(0, self._n))
		self._price_arr = [0] * self._n
		self._epsilon = 1.0 / (1 + self._n)

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
		bid_increment = px - py + self._epsilon
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

	def convert_to_glpk(self, filename):
		with open(filename, 'a') as data_file:
			# will convert matrix to the proper output file formal
			width = 3
			n = len(self._matrix)

			s = '1'
			for num in range(2, n + 1):
				s += '{0:10}'.format(num)
			data_file.write('param m := {};\n'.format(n))
			data_file.write('param n := {};\n'.format(n))
			data_file.write('param c : {} :=\n'.format(s))
			s = ''
			for i, row in enumerate(self._matrix):
				s += '{0:7}'.format(i + 1)
				s += ' '
				for x in row:
					s += '{0:10}'.format(x)
				s += '\n'
			# somehow append ';' to the end
			data_file.write('{} ;\n'.format(s))
			data_file.write('end;')

	def execution_via_glpk(self, filename):
		model_file = 'auction.mod'
		args = ['glpsol', '--model', model_file, '--data', filename]
		
		start_time = timeit.default_timer()
		# run glpk version
		subprocess.call(args)
		elapsed = timeit.default_timer() - start_time
		return elapsed
