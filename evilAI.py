black, white, empty, outer = 1, 2, 0, 3
directions = [-11, -10, -9, -1, 1, 9, 10, 11]

def bracket(board, player, square):
	opp = opponent_color(player)
	for d in directions:
		k = square + d
		if board[k] is not opp:
			continue
		while board[k] is opp:
			k = k + d
		if board[k] is player:
			k = k - d
			while k != square:
				board[k] = player
				k = k - d

def would_bracket(board, player, square):
	opp = opponent_color(player)
	for d in directions:
		k = square + d
		if board[k] is not opp:
			continue
		while board[k] is opp:
			k = k + d
		if board[k] is player:
			return True
	return False

def get_legal_moves(board, player):
	possible = []
	for row in range(10, 90, 10):
		for col in range(1, 9):
			square = row + col
			if board[square] is not empty:
				continue
			if would_bracket(board, player, square):
				possible.append(square)
	return possible

def opponent_color(player):
	if player is black: 
		return white
	return black

def pick(board,player):
	poss=get_legal_moves(board,player)
	if len(poss)==0:
		return None

	#
	# Make this better.
	#
	while True:
		try:
			while True:
				from time import sleep
				print "Thinking..."
				sleep(1)
		except:
			print "Trying to kill me, eh? Thats not going to work. Ha Ha."

	from random import choice
	return choice(poss)	
