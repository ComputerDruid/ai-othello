# Torbert, 12.2.2004
# Additions by Kassing 1.20.06

# Changelog:
# ----------
# * Modified the imports, the show method, the play_one method.
# * Added a play_one_modified method that is (supposed to be) compatible with the original.
# * Added a play_round method that plays a certain number of games and keeps score solely 
#   by number of pieces, which is valid for a two-round match. It also alternates who starts. 
# * Added a second play round method that counts by games, so a higher number of games can be 
#   played, and it still flips black/white, has tie breakers for all cases (except always tie)
#   and cuts off when the outcome is inevitable (one player has more than half the rounds minus ties)
# * Added a tournament system that takes 2^n players in one bracket, filling in left over spots with
#   jrandom instances. Has bracket drawing capabilities

from os import system, listdir
from sys import argv, stdout	#need stdout for printing without newlines or spaces on the end
from time import time, sleep
from random import randint, shuffle

tourney = False
graphic_tourney=True

if len(argv) > 1:
	tourney = True
time_pool, allowed_time = 50.0, 1.5

black, white, empty, outer = 1, 2, 0, 3
directions = [-11, -10, -9, -1, 1, 9, 10, 11]

def show(board, player_one, player_two, wins=None):			#now with ANSI power!
	system('clear')
	stdout.write('\033[0;0H')		# return to 0,0
	print 'The Players:'
	print 'Black:',player_one
	print 'White:',player_two
	print
	print "  " + " ".join(map(str,range(1,9)))
	for row in range(10, 90, 10):
		s = str(row) + "" 
		for col in range(1, 9):
			square = board[row + col]
			if square is empty:
				s += chr(27) + "[32;42" 		# The chr(27) can be replaced with "\033"
			elif square is white:
				s += chr(27) + "[37;42"
			else:
				s += chr(27) + "[30;42"
			s += "m"
			s += chr(27) + "[1m";
			if square is empty:
				s += "  "
			else:
				s += "* "
		print s + chr(27) + "[0m"
	print
	print 'Pieces: '
	print 'Black:',count(board,black),' '			# draw extra spaces to overwrite previous counts
	print 'White:',count(board,white),' '
	print
	
	if wins!=None:
		print 'Wins:'
		print player_one+':',wins[1],'     '
		print player_two+':',wins[2],'     '
		print 'Ties: ',wins[0],'     '

def show2(board): 						# Old
	print "  " + "".join(map(str,range(1,9)))
	for row in range(10, 90, 10):
		s = str(row) + "" 
		for col in range(1, 9):
			square = board[row + col]
			if square is empty:
				s += chr(27) + "[32;42"
			elif square is white:
				s += chr(27) + "[37;42"
			else:
				s += chr(27) + "[30;42"
			s += "m"
			s += chr(27) + "[1m";
			if square is empty:
				s += " "
			else:
				s += "+"
		print s + chr(27) + "[0m"
	print

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

def count(board, player):
	total = 0
	for row in range(10, 90, 10):
		for col in range(1, 9):
			square = board[row + col]
			if square is player:	
				total = total + 1
	return total

def play_one(strategies, flag, player_one, player_two):
	system("clear")
	board = [empty] * 100
	board[0:10] = [outer] * 10
	board[90:100] = [outer] * 10
	for k in range(10, 90, 10):
		board[k + 0] = outer
		board[k + 9] = outer
	board[44], board[55] = white, white
	board[45], board[54] = black, black
	if flag:
		show(board, player_one, player_two)
	player, squares, stuck = black, 4, 0
	one, two = 0, 0
	while squares < 64 and stuck < 2:
		start = time()
		square = strategies[player].pick(board[:], player)
		finish = time()
		total_time = finish - start
		if player is white:
			two += total_time
			if two > time_pool and total_time > allowed_time:
				if flag:
					print "White is disqualified for taking too much time."
				return black
		else:
			one += total_time
			if one > time_pool and total_time > allowed_time:
				if flag:
					print "Black is disqualified for taking too much time."
				return white
		possible = get_legal_moves(board, player)
		if square is not None:
			if square not in possible:
				if player is white:
					if flag:
						print "White is disqualified for an illegal move."
					return black
				else:
					if flag:
						print "Black is disqualified for an illegal move."
					return white
			board[square] = player
			bracket(board, player, square)
			squares += 1
			stuck = 0
		elif len(possible) == 0:
			stuck += 1
		else:
			if player is white:
				if flag:
					print "White is disqualified for passing illegally."
				return black
			else:
				if flag:
					print "Black is disqualified for passing illegally."
				return white			
		player = opponent_color(player)
		if flag:
			show(board, player_one, player_two)
	w, b = count(board, white), count(board, black)
	#if flag:
	#	print "White:", w  # already shown in def show(board):
	#	print "Black:", b
	#	print
	if w == b:
		return 0
	elif w > b:
		return white
	else:
		return black

def play_one_modified(strategies, flag, player_one='Player 1', player_two='Player 2', flip=False, rd=False, ws=None): 
# this is way modified, but is still compatible with the original play_one (which isn't in this file)
# player_one and player_two are strings that are names
# flip signals to flip the players
# rd signals to return the differential, not the winning player

	if flag: system("clear")
	ts=strategies[:]
	tw=ws[:]
	if flip:				# rather than physically flipping, I could just flip who goes first...
		t=player_one
		player_one=player_two
		player_two=t
		ts=[None, strategies[2], strategies[1]]
		if ws!=None:
			tw=[ws[0],ws[2],ws[1]]
		
	board = [empty] * 100
	board[0:10] = [outer] * 10
	board[90:100] = [outer] * 10
	for k in range(10, 90, 10):
		board[k + 0] = outer
		board[k + 9] = outer
	board[44], board[55] = white, white
	board[45], board[54] = black, black
	if flag:
		show(board, player_one, player_two, wins=tw)
	player, squares, stuck = black, 4, 0
	one, two = 0, 0
	while squares < 64 and stuck < 2:
		start = time()
		try:
			square = ts[player].pick(board[:], player)
		except:
			if player is white:
				if flag:
					print "White is disqualified, because the pick method crashed"
					sleep(3)
				return (64-count(board,empty))
			else:
				if flag:
					print "Black is disqualified, because the pick method crashed"
					sleep(3)
				return -1*(64-count(board,empty))
		finish = time()
		total_time = finish - start
		if player is white:
			two += total_time
			if two > time_pool and total_time > allowed_time:
				if flag:
					print "White is disqualified for taking too much time."
					sleep(3)
				return (64-count(board,empty))
		else:
			one += total_time
			if one > time_pool and total_time > allowed_time:
				if flag:
					print "Black is disqualified for taking too much time."
					sleep(3)
				return -1*(64-count(board,empty))
		possible = get_legal_moves(board, player)
		if square is not None:
			if square not in possible:
				if player is white:
					if flag:
						print "White is disqualified for an illegal move."
						sleep(3)
					return (64-count(board,empty))
				else:
					if flag:
						print "Black is disqualified for an illegal move."
						sleep(3)
					return -1*(64-count(board,empty))
			board[square] = player
			bracket(board, player, square)
			squares += 1
			stuck = 0
		elif len(possible) == 0:
			stuck += 1
		else:
			if player is white:
				if flag:
					print "White is disqualified for passing illegally."
					sleep(3)
				return (64-count(board,empty))
			else:
				if flag:
					print "Black is disqualified for passing illegally."
					sleep(3)
				return -1*(64-count(board,empty))
		player = opponent_color(player)
		if flag:
			show(board, player_one, player_two, wins=tw)
	w, b = count(board, white), count(board, black)
	#if flag:
	#	print "White:", w  # already shown in the modified show method
	#	print "Black:", b
	#	print
	if flag: sleep(4)
	
	if rd: return b-w
	if b==w:
		return 0
	if b>w:
		return b
	return w

def play_match(strategies, flag, player_one, player_two, rounds):
# This function just does a match where the games are played and the better differential wins.
# For 2 games this should be valid... the player with more overall pieces had to either have won both games or
# have taken the tiebreaker based on differential. After this number of rounds, the validity of the numbers declines
	score=0
	for i in range(rounds):
		if i%2==0:
			score += play_one_modified(strategies[:], flag, player_one, player_two, rd=True)
		else:
			score += -1 * play_one_modified(strategies[:], flag, player_one, player_two, flip=True, rd=True) 
			# flip differential, it might be overkill to replace the if statement with a boolean expression in the function call
			
	while score==0: # tie in differential, we don't like this, hopefully no infinite loops
		if randint(1,2)==1:
			score=play_one_modified(strategies[:], flag, player_one, player_two, rd=True)
		else:
			score=play_one_modified(strategies[:], flag, player_one, player_two, flip=True, rd=True)
			
	if score>0:
		return black
	else:
		return white

def play_match_by_wins(strategies, flag, player_one, player_two, rounds):
# supports any number of rounds, flips white/black
# tracks by wins, tiebreaker is differential
# differential tie forces another game, random starter
	totaldiff=0
	wins=[0,0,0]
	for i in range(rounds):
		retval=play_one_modified(strategies[:], flag, player_one, player_two, flip=(i%2==1), rd=True, ws=wins)
		if i%2==0:			# not flipped
			totaldiff+=retval
			if retval==0:
				wins[0]+=1
			elif retval>0:
				wins[1]+=1
			else:
				wins[2]+=1
		else:				# flipped
			totaldiff-=retval
			if retval==0:
				wins[0]+=1
			elif retval>0:
				wins[2]+=1
			else:
				wins[1]+=1
				
		if wins[1]>(rounds-wins[0])/2:	
			return black		# no point in continuing
		if wins[2]>(rounds-wins[0])/2:
			return white

	if wins[1]==wins[2]:
		while totaldiff==0:
			if randint(1,2)==1:
				retval=play_one_modified(strategies[:], flag, player_one, player_two, rd=True, ws=wins)
				totaldiff+=retval
			else:
				retval=play_one_modified(strategies[:], flag, player_one, player_two, flip=True, rd=True, ws=wins)
				totaldiff-=retval
		if totaldiff>0:
			return black
		elif totaldiff<0:
			return white
	
	if wins[1]>wins[2]:
		return black
	return white
	
def draw_bracket(rnd,players):
# For any round r, the column will be 15r, the first row will be 2^(r-1), and the other rows will be 2^r * i below, where i is the index
	irow = 2**(rnd-1)
	col = 17*(rnd-1)+1
	stdout.write('\033['+str(irow)+';'+str(col)+'H')	
	for i in range(len(players)-1):
		stdout.write(players[i][0])
		stdout.write('\033['+str(irow + (i+1) * (2**(rnd-1)))+';'+str(col)+'H')
	stdout.write(players[-1][0])
	print

def main():
	if not tourney:
		system("clear")
		files = [k[:-4] for k in listdir(".") if k[-3:] == "pyc"]
		k = 1
		print "The Players:"
		for f in files:
			print "%3d. %s" % (k, f)
			k += 1
		print
		player_one = files[int(raw_input("Black: "))-1]
		player_two = files[int(raw_input("White: "))-1]
		module_one = __import__(player_one)
		module_two = __import__(player_two)
		strategies = [None, module_one, module_two]
		result = play_match_by_wins(strategies, True, player_one, player_two, 2)
		if result == 0:
			print "It's a tie!"
		elif result == white:
			print "The winner is %s." % player_two
		else:
			print "The winner is %s." % player_one
	else:
		# added a simple 2^n tournament system, random players added to fill up brackets
		system("clear")
		
		ailist = open('ailist.txt').readlines()
		# File format for ailist.txt: 
		# one name per line, without file extension
		# files that don't exist will be replaced with jrandom instances
		
		files = [x[:-1] for x in ailist]
		players = []
		winners = []
		rnd = 1	#round is a reserved name
		for k in range(len(files)):
			try:
				players.append((ailist[k][:-1],__import__(files[k])))
			except:
				pass
			
		while len(players)!=4 and len(players)!=8 and len(players)!=16 and len(players)!=32 and len(players)!=64:
			players.append(("random"+str(len(players)),__import__("jrandom")))
		
		shuffle(players) # easier than shuffling by hand
		
		total=len(players) # this isn't actually needed, but could be useful in better bracket drawing
	
		rounds=[players[:]]
		
		while len(players)!=1:
			draw_bracket(rnd,players)
			sleep(3)
			for k in range(len(players)/2):
				player_one=players.pop(0)
				player_two=players.pop(0)
				strategies=[None, player_one[1], player_two[1]]
				winners.append([None,player_one,player_two][play_match_by_wins(strategies,graphic_tourney, player_one[0], player_two[0],2)])
				
				system("clear")
				for i in range(len(rounds)):
					draw_bracket(i+1,rounds[i])
				draw_bracket(rnd+1,winners) # draw as we go to show progress
				sleep(3)
			rounds.append(winners[:])	
			players=winners[:]
			winners=[]
			rnd+=1
		for i in range(len(rounds)):
			draw_bracket(i+1,rounds[i])
		draw_bracket(rnd,players)
  		print '\033['+str(total+2)+';1H'	

	print

if __name__ == "__main__":
	main()
