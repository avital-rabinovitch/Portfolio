import math
import decimal
import copy

#from notes
def almostEqual(d1, d2):
	epsilon = 10**-10
	return (abs(d2 - d1) < epsilon)

#from notes
def roundHalfUp(d):
	# Round to nearest with ties going away from zero.
	rounding = decimal.ROUND_HALF_UP
	# See other rounding options here:
	# https://docs.python.org/3/library/decimal.html#rounding-modes
	return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#does the math to get hexagon points given rad of pixel and local center
def getHexPts(localCX, localCY, pixSize, angle = 30):
	pts = []
	shapeSides = 6 #hexagonal pixels
	theta = angle
	delta = 360 / shapeSides
	for i in range(6):
		x = localCX + pixSize*math.cos(math.radians(theta))
		y = localCY - pixSize*math.sin(math.radians(theta))
		x = round(x)
		y = round(y)
		theta += delta
		pts.append((x,y))
	return pts

def getNeighbours(x, y):
	neighbours = set()
	moves = {	'NE':( 0, 1), 'E':( 1, 0), 'SE':( 1,-1), 
				'SW':( 0,-1), 'W':(-1, 0), 'NW':(-1, 1)	}
	for move in moves.values():
			#get new x and new y with moves as deltas
			newX = x + move[0]
			newY = y + move[1]
			neighbours.add((newX,newY))

	return neighbours
	
#returns distance between two points
def ptDist(pt0, pt1):
	x0 = pt0[0]
	y0 = pt0[1]
	x1 = pt1[0]
	y1 = pt1[1]
	
	#distance formula
	return ((x1-x0)**2+(y1-y0)**2)**0.5
	




class HexGrid(object):

	

	def __init__(self, pixSize, layers, globalCX, globalCY, color, angle = 0):
		#pixSize is effective hexagon RADIUS
		self.pixSize = pixSize
		self.layers = layers
		self.globalCX = globalCX
		self.globalCY = globalCY
		self.angle = angle
		self.edgeReached = False #flag for when cell on edge is added
		#cells is collection of hexagons in grid
		self.cells = dict() #x, y pos: HexCell obj
		self.height = pixSize * math.sin(math.radians(60))
		#dictionary mapping pixel of point to count scene in grid 
		#R^2 -> {1,2,3}
		self.globalPoints = dict()
		#index of point corresponds to order drawn
		self.boundaryPoints = []
		self.holePoints = [] #empty list until holes added
		#length of hexagon side
		#self.size = self.pixSize
		self.ptsToAdd = []
		self.color = color
		
		self.size = None
		
		
		
		def initializePoints(h):
			if h.layers == 1:
				pts = h.getLocalPixels((0,0))
				for p in pts:
					self.globalPoints[p] = 1
				h.cells[(0,0)] = HexCell((0,0), pts)
				self.boundaryPoints = pts
	
			else:
				#iterate through all "square" points of grid
				for x in range(-(layers-1), layers):
					for y in range(-(layers-1), layers):
						#parts outside I and III quadrants
						if x * y  > 0 and abs(x + y) > layers - 1:
							continue
						#all other points included
						h.cells[(x,y)] = HexCell((x,y))
						#h.addSingleGridCell((x,y))
						#h.addSingleHex((x, y))
			
		initializePoints(self)
		
	#makes dictionary of cells to hexCells
	def addSingleGridCell(self, coord):
		#if dictionary of cells is empty add first hex
		if (len(self.cells) == 0):
			self.cells[coord] = HexCell(coord, None, 1) #pts none state 1 center pt
		else:
			self.cells[coord] = HexCell(coord)
			
	#sets boundary points to given list of points
	def setBoundaryPoints(self, L):
		self.boundaryPoints = copy.deepcopy(L)
			
	#returns global origin of grid
	def getGlobalOrigin(self):
		return self.globalCX, self.globalCY



	#gets position of cX, cY for each hex on grid
	#WAS getPixels
	def getLocalOrigin(self, coord):
		x = coord[0]
		y = coord[1]

		localCX = self.globalCX + (2*x+y)*self.height
		localCY = self.globalCY - 3/2 * y * self.pixSize
		return  localCX, localCY
		
		
	#gets edge pixels of local hexagon
	def getLocalPixels(self, coord):
		localCX, localCY = self.getLocalOrigin(coord)
		pts = getHexPts(localCX, localCY, self.pixSize)
		return pts

	#gets radius of hexgrid
	def getGridSize(self):
		if self.size == None:
			x, y = self.getGlobalOrigin()
			ptCount = len(self.boundaryPoints)
			maxDist = 0
			for p in self.boundaryPoints[:ptCount//12 +1]:
				dist = ptDist((x,y), p)
				if dist > maxDist:
					maxDist = dist
			self.size = roundHalfUp(maxDist)
		return self.size

	#coord is x y tuple of hex coordinate grid position
	def addSingleHex(self, coord):
		
		#given list returns true if list contains a zero
		def containsZeroIndex(self, L):
			bPIndices = []
			containsOne = False
			containsMax = False
			hi = len(self.boundaryPoints)-1
			for i in L:
				#index of point in L in bp
				place = self.boundaryPoints.index(i)
				bPIndices.append(place)
				if place == 0: return True
				if place == 1: containsOne = True
				if place == hi: containsMax = True
			m = min(bPIndices)
			M = max(bPIndices)
			if (M-m > len(self.boundaryPoints)//2): return True
			return (containsOne or containsMax)
		
		#gets tentative 6 points to add
		pts = self.getLocalPixels(coord)
		ptsToInsert = []
		#if dictionary of cells is empty add first hex
		if len(self.globalPoints) == 0:
			#initiate globalPoints
			for p in pts:
				self.globalPoints[p] = 1
			#initiate boundaryPoints
			self.boundaryPoints = pts
		else: 
			newBounds = []			
			localCounts = []
		
			for p in pts:
				if p in self.globalPoints and p in self.boundaryPoints:
					self.globalPoints[p] +=1
					if self.globalPoints[p] == 3 and p in self.boundaryPoints:
				
						self.boundaryPoints.remove(p)
					localCounts.append(self.globalPoints[p])
				else:
					localCounts.append(1)
					self.globalPoints[p] = 1							
			ones = []
			twos = []
			oddFourCase = False
			##########
			###ONES###
			##########
			if 1 in localCounts:
				if localCounts == [1,1,1,1,1,1]: return
				
				for c in localCounts:
					if c == 1:
						ones.append(1)
				
				#shift pts and  localCounts such that local counts starts with 1s
				while(localCounts[0:len(ones)] != ones):
					
					localCounts = localCounts[1:] + [localCounts[0]]
					pts = pts[1:] +[ pts[0]]
				
				newBounds += pts[0:len(ones)]
				
				start = pts[len(ones)]
				
				i = 1
				while (self.boundaryPoints[0] != start):
					
					if i > len(self.boundaryPoints): break
					self.boundaryPoints = self.boundaryPoints[1:] + [self.boundaryPoints[0]]
					i += 1
				
				endIndex = self.boundaryPoints.index(pts[-1])
				newBounds += self.boundaryPoints[:endIndex +1]
			
			##########		
			###TWOS###
			##########
			elif 2 in localCounts:
				#print("did a 2")
				for c in localCounts:
					if c == 2:
						twos.append(2)
						
						
				#check for 223322 case:
				if localCounts[0:3] == localCounts[3:]:
					oddFourCase = True
					while(localCounts[0:2] != twos[0:2]):
						localCounts = localCounts[1:] + [localCounts[0]]
						pts = pts[1:] +[ pts[0]]
						
				else:
					#shift pts and  localCounts such that local counts starts with 2s
					
					while(localCounts[0:len(twos)] != twos):
						
						localCounts = localCounts[1:] + [localCounts[0]]
						pts= pts[1:] +[ pts[0]]
					
			
				
				#lc = [2, 2, 3, 3, 3, 3]
				if len(twos) == 2:
					
					newBounds += pts[0:2]
					start = pts[1]	
				
					i = 1
					while (self.boundaryPoints[0] != start):
						if i > len(self.boundaryPoints): break
						self.boundaryPoints = self.boundaryPoints[1:] + [self.boundaryPoints[0]]
					
						i += 1
						
					try:
						endIndex = self.boundaryPoints.index(pts[-1])
						newBounds += self.boundaryPoints[:endIndex +1]
					except:
						return
				
					
					
				#lc = [2, 2, 2, 2, 3, 3]
				elif (len(twos) == 4) and (not oddFourCase):
					
					#if local points contain index 0 pt
					while(containsZeroIndex(self, pts[0:4])): #todo: fix so that if 0 is in 3 that popped
						#shift boundary pts
						self.boundaryPoints = self.boundaryPoints[1:] + [self.boundaryPoints[0]]
						
					# get two indexes of line 1 and line 2
					p0 = self.boundaryPoints.index(pts[0])
					p1 = self.boundaryPoints.index(pts[1])
					p2 = self.boundaryPoints.index(pts[2])
					p3 = self.boundaryPoints.index(pts[3])
					
					# compare delta index for each line
					d1 = abs(p0 - p1)
					d2 = abs(p2 - p3)
					
					# longer delta is one the is in border
					if d1 > d2:
						minP = min(p0, p1)
						maxP = max(p0, p1)
						
					else:
						minP = min(p2, p3)
						maxP = max(p2, p3)
						
					newBounds = self.boundaryPoints[:minP+1]
					newBounds += self.boundaryPoints[maxP:]
					
					
				#########oddFourCase is True
				else:
					
					#if local points contain index 0 pt
					while(containsZeroIndex(self, pts[0:2]+pts[3:5])): 
						#shift boundary pts
						self.boundaryPoints = self.boundaryPoints[1:] + [self.boundaryPoints[0]]
						
					# get two indexes of line 1 and line 2
					p0 = self.boundaryPoints.index(pts[0])
					p1 = self.boundaryPoints.index(pts[1])
					p2 = self.boundaryPoints.index(pts[3])
					p3 = self.boundaryPoints.index(pts[4])
					#print("pNEW",p0,p1,p2,p3,len(self.boundaryPoints))
					
					# compare delta index for each line
					d1 = abs(p0 - p1)
					d2 = abs(p2 - p3)
					
					# longer delta is one the is in border
					if d1 > d2:
						
						minP = min(p0, p1)
						maxP = max(p0, p1)
						
					else:
						minP = min(p2, p3)
						maxP = max(p2, p3)
						
					newBounds = self.boundaryPoints[:minP+1]
					newBounds += self.boundaryPoints[maxP:]
					
			else:
				return
					
			self.boundaryPoints = newBounds
			
	#given canvas draws a simple polygon of points of flakes color
	def drawHex(self, canvas):
		canvas.create_polygon(self.boundaryPoints, fill = self.color, width = 3)

	#add points to hexagon grid given a point
	#adds points so it is surrounded by points
	def addPoints(self, x, y, state = 0):
		neighbours = getNeighbours(x, y)
		for cell in neighbours:
			if cell not in self.cells:
				self.addSingleHex(cell, state)
				
	#sets angle to given value without rotating it
	#for reindexing
	def redefineAngle(self, angle):
		self.angle = angle

	#returns effective size of hexagon defined as longest diagonal
	def getSize(self):
		return self.layers * self.pixSize * 2
	
	#returns center x and y coordinate on grid and current angle oriantation	
	def getPosition(self):
		return self.globalCX, self.globalCY, self.angle

	#update center x and y position, angle
	#transform boundaryPoints accordingly
	def setPosition(self, x, y, angle = None):
		deltaX = x - self.globalCX
		deltaY = y - self.globalCY
		if angle !=  None:
			deltaAngle = angle - self.angle
		else: 
			deltaAngle = 0
		#transform the flake
		#properties updated in transform
		self.transform(deltaAngle,(deltaX, deltaY))
		
		

	#transforms hex grid given a rotation
	#in degrees and position as
	#delta x delta y about an origin
	def transform(self, rot, trans = (0,0)):
		self.angle += rot
		rot = math.radians(rot)
		#get global origin to "bring" points about center
		cX, cY = self.getGlobalOrigin()
		

		#iterate through the cells
		for i in range(len(self.boundaryPoints)):
			p = self.boundaryPoints[i]
			#get origin of rotation
			xO, yO = cX, cY
			tempX = p[0] - xO
			tempY = p[1] - yO
			#scale origin by linear translation
			xO += trans[0]
			yO += trans[1]
			#rotation 
			x = tempX*math.cos(rot)-tempY*math.sin(rot) + xO
			y = tempY*math.cos(rot)+tempX*math.sin(rot) + yO
			#translation and account for origin
			
			self.boundaryPoints[i]=(x,y)
				
			#self.cells[cell].setPoints(pts)
		#update center	
		self.globalCX += trans[0]
		self.globalCY += trans[1]


class HexCell(object):

	def __init__(self, coord, points = None, state = 0):
		#coord is "hexagonal" coordiante point
		self.coord = coord
		self.points = points
		self.state = state

	#returns pseudo-cartesian coordinate 
	def getCoord(self):
		return self.coord

	#returns 6 pixel poitns
	def getPoints(self):
		return self.points
	
	#sets 6 pixel points
	def setPoints(self, pts):
		self.points = pts

	#gets state
	def getState(self):
		return self.state

	#setes state and updates receptive cells --> cells who have or 
	#are boarding cell with state >= 1
	def setState(self, state, hexGrid, currentReceptive, cells):
		#check if boundary changed
		if self.state < 1 and state >= 1:
			#update receptive
			currentReceptive.add(self.coord)
			currentReceptive |= getNeighbours(self.coord[0], self.coord[1])
			currentReceptive &= cells
			if (self.coord[0] == hexGrid.layers - 1 or
				self.coord[1] == hexGrid.layers - 1):
				hexGrid.edgeReached = True
			#add cell to boundary Points
			hexGrid.addSingleHex(self.coord)

		#update state
		self.state = state