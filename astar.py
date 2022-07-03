from cgitb import grey
from curses import KEY_DOWN
import pygame
import math
import time
import sys
from queue import PriorityQueue

pygame.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path-Finding Algorithms")

RED = (238, 44, 44)
ENDS = (0, 0, 0)
GREEN = (0, 201, 87)
BACKGROUNDGREY = (179, 179, 179)
BLACK = (46, 46, 46)
KINDAWHITE = (205,200,177)
LEADGREY = (125, 125, 125)
GREY = (77, 77, 77)
SKYBLUE = (135,206,235)

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = KINDAWHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == GREY

	def is_open(self):
		return self.color == LEADGREY

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == GREEN

	def is_end(self):
		return self.color == RED

	def reset(self):
		self.color = KINDAWHITE

	def make_start(self):
		self.color = GREEN

	def make_closed(self):
		self.color = GREY

	def make_open(self):
		self.color = LEADGREY

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = RED

	def make_path(self):
		self.color = KINDAWHITE
	
	def make_ends(self):
		self.color = ENDS

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def paused(ROWS, width, start, end, grid, cleared):

	pause = True

	while pause:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)
					cleared = True
					return start, end, grid, cleared
				if event.key == pygame.K_q:
					pygame.quit()
				elif event.key == pygame.K_r:
					pause = False
					return start, end, grid, cleared

# def better_prim(mazearray=False, start_point=False, visualise=VISUALISE):

#         # If a maze isn't input, we just create a grid full of walls
#         if not mazearray:
#             mazearray = []
#             for row in range(ROWS):
#                 mazearray.append([])
#                 for column in range(ROWS):
#                     if row % 2 != 0 and column % 2 != 0:
#                         mazearray[row].append(Node('dormant'))
#                     else:
#                         mazearray[row].append(Node('wall'))
#                     if visualise:
#                         draw_square(row,column,grid=mazearray)

#         n = len(mazearray) - 1

#         if not start_point:
#             start_point = (random.randrange(1,n,2),random.randrange(1,n,2))
#             mazearray[start_point[0]][start_point[1]].update(nodetype='blank')
        
#         if visualise:
#             draw_square(start_point[0], start_point[1], grid=mazearray)
#             pygame.display.flip()

#         walls = set()

#         starting_walls = get_neighbours(start_point, n)

#         for wall, ntype in starting_walls:
#             if mazearray[wall[0]][wall[1]].nodetype == 'wall':
#                 walls.add(wall)

#         # While there are walls in the list (set):
#         # Pick a random wall from the list. If only one of the cells that the wall divides is visited, then:
#         # # Make the wall a passage and mark the unvisited cell as part of the maze.
#         # # Add the neighboring walls of the cell to the wall list.
#         # Remove the wall from the list.
#         while len(walls) > 0:
#             wall = random.choice(tuple(walls))
#             visited = 0
#             add_to_maze = []

#             for wall_neighbour, ntype in get_neighbours(wall,n):
#                 if mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype == 'blank':
#                     visited += 1

#             if visited <= 1:
#                 mazearray[wall[0]][wall[1]].update(nodetype='blank')
                
#                 if visualise:
#                     draw_square(wall[0],wall[1],mazearray)
#                     update_square(wall[0],wall[1])
#                     time.sleep(0.0001)
                
#                 # A 'dormant' node (below) is a different type of node I had to create for this algo
#                 # otherwise the maze generated doesn't look like a traditional maze.
#                 # Every dormant eventually becomes a blank node, while the regular walls
#                 # sometimes become a passage between blanks and are sometimes left as walls
#                 for neighbour, ntype in get_neighbours(wall,n):
#                     if mazearray[neighbour[0]][neighbour[1]].nodetype == 'dormant':
#                         add_to_maze.append((neighbour[0],neighbour[1]))
                
#                 if len(add_to_maze) > 0:
#                     cell = add_to_maze.pop()
#                     mazearray[cell[0]][cell[1]].update(nodetype='blank')
                    
#                     if visualise:
#                         draw_square(cell[0],cell[1],mazearray)
#                         update_square(cell[0],cell[1])
#                         time.sleep(0.0001)
                    
#                     for cell_neighbour, ntype in get_neighbours(cell,n):
#                         if mazearray[cell_neighbour[0]][cell_neighbour[1]].nodetype == 'wall':
#                             walls.add(cell_neighbour)

#             walls.remove(wall)

#         mazearray[END_POINT[0]][END_POINT[1]].update(nodetype='end')
#         mazearray[START_POINT[0]][START_POINT[1]].update(nodetype='start')

#         return mazearray

def Astaralgorithm(draw, grid, start, end,ROWS, width):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		cleared = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					start, end, grid, cleared = paused(ROWS, width, start, end, grid, cleared)
					if cleared:
						break
				if event.key == pygame.K_q:
					pygame.quit()
		if cleared:
			break
		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			start.make_ends()
			end.make_ends()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False

def bestfirstalgorithm(draw, grid, start, end,ROWS, width):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		cleared = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					start, end, grid, cleared = paused(ROWS, width, start, end, grid, cleared)
					if cleared:
						break
				if event.key == pygame.K_q:
					pygame.quit()
		if cleared:
			break
		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			start.make_ends()
			end.make_ends()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False

def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width, height):
	gap = width // rows
	for i in range(rows-2):
		pygame.draw.line(win, LEADGREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, LEADGREY, (j * gap, 0), (j * gap, height))


def draw(win, grid, rows, width):
	smallfont = pygame.font.Font(None, 32)
	text1 = smallfont.render('start' , True , KINDAWHITE)
	text2 = smallfont.render('clear' , True , KINDAWHITE)
	text3 = smallfont.render('quit' , True , KINDAWHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)
	pygame.draw.rect(win,(0,0,0),[60,760,90,30])
	win.blit(text1 , (60+20,760+6))

	pygame.draw.rect(win,(0,0,0),[190,760,90,30])
	win.blit(text2 , (190+20,760+6))

	pygame.draw.rect(win,(0,0,0),[640,760,90,30])
	win.blit(text3 , (640+20,760+6))

	draw_grid(win, rows, width, width-50)
	pygame.display.update()

# makes the background image opaque
def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)

def instructions(win, astar):
	# Loop until the user clicks the close button.
	done = False

	font1 = pygame.font.Font(None, 60)
	font2 = pygame.font.Font(None, 28)
	font3 = pygame.font.Font(None, 32)

	display_instructions = True
	instruction_page = 1
	img = pygame.image.load('path.png')

	smallfont = pygame.font.Font(None, 32)
	text3 = smallfont.render('next' , True , KINDAWHITE)
	text4 = smallfont.render('prev' , True , KINDAWHITE)
	text5 = smallfont.render('skip' , True , KINDAWHITE)
	text6 = smallfont.render('             A*' , True , KINDAWHITE)
	text7 = smallfont.render(' Best-first search' , True , KINDAWHITE)

	while not done and display_instructions:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
			if event.type == pygame.MOUSEBUTTONDOWN: 
				if 60 <= mouse[0] <= 150 and 600 <= mouse[1] <= 640:
					instruction_page += 1
				if instruction_page > 1 and 190 <= mouse[0] <= 280 and 600 <= mouse[1] <= 640:
					instruction_page -= 1
				if instruction_page == 3 and 130 <= mouse[0] <= 350 and 400 <= mouse[1] <= 460:
					astar = True
					instruction_page = 4
				if instruction_page == 3 and 450 <= mouse[0] <= 680 and 400 <= mouse[1] <= 460:
					instruction_page = 4
				if 640 <= mouse[0] <= 730 and 600 <= mouse[1] <= 640:
					instruction_page = 3   
				if instruction_page == 4:
					done = True
					display_instructions = False
 
		mouse = pygame.mouse.get_pos()
        # Set the screen background
		win.fill(KINDAWHITE)
		blit_alpha(win, img, (0,200), 128)

		if 60 <= mouse[0] <= 150 and 600 <= mouse[1] <= 640 and instruction_page < 3:
			pygame.draw.rect(win,GREY,[60,600,90,40])
			win.blit(text3 , (60+20,600+10))
			
		elif instruction_page < 3:
			pygame.draw.rect(win,(0,0,0),[60,600,90,40])
			win.blit(text3 , (60+20,600+10))

		if instruction_page > 1 and 190 <= mouse[0] <= 280 and 600 <= mouse[1] <= 640 and instruction_page < 3:
			pygame.draw.rect(win,GREY,[190,600,90,40])
			win.blit(text4 , (190+20,600+10))
			
		elif instruction_page > 1 and instruction_page < 3:
			pygame.draw.rect(win,(0,0,0),[190,600,90,40])
			win.blit(text4 , (190+20,600+10))

		if 640 <= mouse[0] <= 730 and 600 <= mouse[1] <= 640 and instruction_page < 3:
			pygame.draw.rect(win,GREY,[640,600,90,40])
			win.blit(text5 , (640+20,600+10))
			
		elif instruction_page < 3:
			pygame.draw.rect(win,(0,0,0),[640,600,90,40])
			win.blit(text5 , (640+20,600+10))
		
		if 130 <= mouse[0] <= 350 and 400 <= mouse[1] <= 460 and instruction_page == 3:
			pygame.draw.rect(win,GREY,[130,400,220,60])
			win.blit(text6 , (130+20,400+15))
			
		elif instruction_page == 3:
			pygame.draw.rect(win,(0,0,0),[130,400,220,60])
			win.blit(text6 , (130+20,400+15))

		if 450 <= mouse[0] <= 680 and 400 <= mouse[1] <= 460 and instruction_page == 3:
			pygame.draw.rect(win,GREY,[450,400,220,60])
			win.blit(text7 , (450+20,400+15))
			
		elif instruction_page == 3:
			pygame.draw.rect(win,(0,0,0),[450,400,220,60])
			win.blit(text7 , (450+20,400+15))

		posX = (WIDTH * 1/8)
		posY = (WIDTH * 1/8)
		position = posX, posY
	
		if instruction_page == 1:
			# Draw instructions, page 1
			# This could also load an image created in another program.
			# That could be both easier and more flexible.
	
			text1 = font1.render("Instructions", True, GREY)
			win.blit(text1, [270, 200])
			text = font2.render("1", True, GREY)
			win.blit(text, [400, 700])
	
		if instruction_page == 2:
			# Draw instructions, page 2
			text = ["     This program visualizes Path-Finding algorithms, ", "        to find the shortest path between two points.      ", "             You will be presented with a 50 x 50 grid.", " Select the starting point by clicking a box in the grid,   ", "             and the ending point by clicking another. ", "     You can then create obstacles by clicking any box", "                  and gliding above adjacent boxes."]
			label = []
			for line in text: 
				label.append(font3.render(line, True, GREY))
			
			for line in range(len(label)):
				win.blit(label[line],(position[0],position[1]+(line*32)+(15*line)))
	
			text = font2.render("2", True, GREY)
			win.blit(text, [400, 700])

		if instruction_page == 3:
			# Draw instructions, page 3
			text = ["    Please select the algorithm you want to see at work!"]
			label = []
			for line in text: 
				label.append(font3.render(line, True, GREY))
			
			for line in range(len(label)):
				win.blit(label[line],(position[0],position[1]+(line*32)+(15*line)))
	
			text = font2.render("3", True, GREY)
			win.blit(text, [400, 700])
		# Go ahead and update the screen with what we've drawn.
		pygame.display.flip()
	return astar

		

def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 50
	grid = make_grid(ROWS, width)

	start = None
	end = None

	ins = False
	run = True 
	astar = False    

		
	while run:
		while ins is False:
			astar = instructions(win, astar)
			ins = True
		smallfont = pygame.font.Font(None, 32)
		text1 = smallfont.render('start' , True , KINDAWHITE)
		text2 = smallfont.render('clear' , True , KINDAWHITE)
		text3 = smallfont.render('quit' , True , KINDAWHITE)
		mouse = pygame.mouse.get_pos()

		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN: 
				if 60 <= mouse[0] <= 150 and 740 <= mouse[1] <= 790 and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					if astar:
						Astaralgorithm(lambda: draw(win, grid, ROWS, width), grid, start, end, ROWS, width)
					else:
						bestfirstalgorithm(lambda: draw(win, grid, ROWS, width), grid, start, end, ROWS, width)
				if 190 <= mouse[0] <= 280 and 740 <= mouse[1] <= 790:
					start = None
					end = None
					grid = make_grid(ROWS, width)
				if 640 <= mouse[0] <= 730 and 740 <= mouse[1] <= 790:
					pygame.quit()
				
			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]

				if not start and spot != end and col < 47:
					start = spot
					start.make_start()

				elif not end and spot != start and col < 47:
					end = spot
					end.make_end()

				elif spot != end and spot != start and col < 47:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None
		if 60 <= mouse[0] <= 150 and 760 <= mouse[1] <= 790:
			pygame.draw.rect(win,GREY,[60,760,90,30])
			win.blit(text1 , (60+20,760+6))

		if 190 <= mouse[0] <= 280 and 760 <= mouse[1] <= 790:
			pygame.draw.rect(win,GREY,[190,760,90,30])
			win.blit(text2 , (190+20,760+6))

		if 640 <= mouse[0] <= 730 and 760 <= mouse[1] <= 790:
			pygame.draw.rect(win,GREY,[640,760,90,30])
			win.blit(text3 , (640+20,760+6))
			
		pygame.display.update()
	pygame.quit()

main(WIN, WIDTH)