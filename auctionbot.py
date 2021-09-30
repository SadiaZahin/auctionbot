import random


class Bot(object):

	def __init__(self):
		self.name = "2026619" # Put your id number her. String or integer will both work
		# Add your own variables here, if you want to.
	
	"""
	Calculate whether the current painting will make a winning set
	Params:
		painting_collection_org: A dict of paintings collected so far by a bot
		painting: Current painting in the auction
	"""
	def is_winning_set(self, painting_collection_org, painting):
		painting_collection = painting_collection_org.copy()
		painting_collection[painting] += 1
		count_list = list(painting_collection.values())
		count_list = sorted(count_list)
		count_list.reverse()
		if count_list[0] < 3 or count_list[1] < 2 or count_list[2] < 1:  # check if not satisfy winning conditions
			return False
		return True

	"""
	Whether the current painting improves a collection set of a bot
	Params:
		painting_collection_org: A dict of paintings collected so far by a bot
		painting: Current painting in the auction
	"""
	def is_painting_required(self, painting_collection_org, painting):
		painting_collection = painting_collection_org.copy()
		painting_collection = sorted(painting_collection.items(), key=lambda x: x[1], reverse=True)
		painting_collection = dict(painting_collection)
		painting_freq = [0, 0, 0, 0]  # The frequency of all occurrences of the paintings
		for key in painting_collection:
			f = painting_collection[key]
			if f <= 3:
				painting_freq[f] += 1

		if painting_collection[painting] == 0:
			if painting_freq[1] + painting_freq[2] + painting_freq[3] < 3:  # Improve the set
				return True
			return False
		if painting_collection[painting] == 1:
			if painting_freq[2] + painting_freq[3] < 2:  # Improve the set
				return True
			return False
		if painting_collection[painting] == 2:  # Improve the set
			if painting_freq[3] < 1:
				return True
			return False

		return False

	"""
	Find the importance value of my bot
	Params:
		painting_collection: A dict of paintings collected so far by a bot
		current_painting: Current painting in the auction
	Expected Importance Values:
		0 - not important at all
		1 - definitely improve current set
		2 - must needed to complete the set
	"""
	def find_own_importance(self, painting_collection, current_painting):
		if self.is_winning_set(painting_collection, current_painting):  # Must needed
			return 2
		if self.is_painting_required(painting_collection, current_painting):  # Can improve the set
			return 1
		return 0

	"""
	Find the importance value of opponent bots
	Params:
		bots: List of bots with their painting collections
		current_painting: Current painting in the auction
	Expected Importance Values:
		0 - not important at all
		1 - definitely improve current set
		2 - must needed to complete the set
	"""
	def find_opponent_importance(self, bots, current_painting):
		flag_red = False  # Whether there exist a bot who will have a winning set using this painting
		flag_yellow = False  # Whether there exist a bot who will improve its set using this painting
		for bot in bots:
			if bot['bot_name'] == self.name:
				continue
			painting_collection = bot['paintings']
			if self.is_winning_set(painting_collection, current_painting):  # Will make winning set
				flag_red = True
			if self.is_painting_required(painting_collection, current_painting):  # Improve the set
				flag_yellow = True
		if flag_red:
			return 2
		if flag_yellow:
			return 1
		return 0

	"""
	Find the maximum opponent bid who are in position to win
	Params:
		bots: List of bots with their painting collections
		current_painting: Current painting in the auction
	"""
	def find_maximum_opponent_bid_to_win(self, bots, current_painting):
		max_bid = 0
		for bot in bots:
			if bot['bot_name'] == self.name:
				continue
			painting_collection = bot['paintings']
			if self.is_winning_set(painting_collection, current_painting):
				max_bid = max(max_bid, bot['budget'])
		return max_bid

	"""
	Find the maximum of the average optimal value a opponent can bid whose set improves with current painting
	Params:
		bots: List of bots with their painting collections
		current_painting: Current painting in the auction
	"""
	def find_opponent_average_bid_for_required_painting(self, bots, current_painting):
		max_bid = 0
		for bot in bots:
			if bot['bot_name'] == self.name:
				continue
			painting_collection = bot['paintings']
			if self.is_painting_required(painting_collection, current_painting):
				required_painting_count = self.required_painting(painting_collection)
				avg_bid = bot['budget'] / required_painting_count
				max_bid = max(max_bid, avg_bid)
		return max_bid

	"""
	Find the minimum number of paintings still required for a bot
	Params:
		bots: List of bots with their painting collections
		current_painting: Current painting in the auction
	"""
	def required_painting(self, painting_collection):
		count_list = list(painting_collection.values())
		count_list = sorted(count_list)
		count_list.reverse()
		req = 0
		if count_list[0] < 3:
			req += (3 - count_list[0])
		if count_list[1] < 2:
			req += (2 - count_list[1])
		if count_list[2] < 1:
			req += (1 - count_list[2])
		return req

	def get_bid_game_type_collection(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids, amounts_paid):

		my_budget = my_bot_details["budget"]
		my_importance = self.find_own_importance(my_bot_details['paintings'], current_painting)
		opponent_importance = self.find_opponent_importance(bots, current_painting)

		painting_required_to_win = self.required_painting(my_bot_details['paintings'])
		avg_budget = my_budget / painting_required_to_win

		if my_importance == 2:
			bid = my_budget
		elif opponent_importance == 2:
			opponent_max_budget = self.find_maximum_opponent_bid_to_win(bots, current_painting)
			bid = min(opponent_max_budget + 1, my_budget)
		elif my_importance == 1:
			bid = avg_budget + 5
			if opponent_importance == 1:
				opponent_bid = self.find_opponent_average_bid_for_required_painting(bots, current_painting)
				bid = opponent_bid + 1
			bid = min(bid, my_budget)
		elif opponent_importance == 1:
			bid = 0
		else:
			bid = 0

		if bid > my_budget:
			bid = my_budget
		return bid


	def get_bid_game_type_value(self, current_round, bots, game_type, winner_pays, artists_and_values, round_limit,
		starting_budget, painting_order, target_collection, my_bot_details, current_painting, winner_ids, amounts_paid):

		total_available_points = 0  # Sum of the points from the remaining paintings
		for round in range(current_round-1, round_limit):
			total_available_points += artists_and_values[painting_order[round]]
		total_bots_in_game = 0
		total_budget_available = 0  # Sum of the remaining budgets of all the bots
		for bot in bots:
			total_bots_in_game += 1
			total_budget_available += bot['budget']


		per_point_value = total_budget_available/total_available_points  # The optimal weight/price of a single point
		current_painting_point = artists_and_values[current_painting]  # The points of the current painting
		my_price = current_painting_point*per_point_value  # Optimal price to bid

		total_bot_scores = 0
		for bot in bots:
			total_bot_scores += bot['score']

		my_expected_score = total_bot_scores / total_bots_in_game
		my_current_score = my_bot_details['score']

		"""
		When the number of bots is very few and my bot is not getting the expected score, 
		then my bot will play slightly aggressively (adding a random value between 5 and 20 to the optimal price)
		"""
		if total_bots_in_game <= 2 and my_current_score < my_expected_score + 1:
			random_addition = random.randint(5, 20)
			my_price += random_addition


		my_budget = my_bot_details["budget"]

		if my_price > my_budget:
			my_price = my_budget
		return my_price
