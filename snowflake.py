import hexGrid
import random

def generatePosition(offSet = 50):
    x = random.randint()

class Snowflake(hexGrid.HexGrid):
    
    def __init__(self, pixSize, layers, alpha, beta, gamma, cX=250, cY=250, color = "white", angle = 30):
        super().__init__(pixSize, layers, cX, cY, color)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.receptiveCells = set()
        self.u = dict()
        self.v = dict()
        #self.speed = #TBD
        self.counter = 0
        self.dir = None
        
        #dirDeterminer = random.random()
        #if dirDeterminer < 0.5: self.dir = -1
        #else: self.dir = 1
        
        #set initial reception values
        for cell in self.cells:
            #set center to s0 (ie. 1)
            if cell == (0,0):
                self.cells[cell].setState(1, self, self.receptiveCells, self.cells.keys())
            else:
                self.cells[cell].setState(beta, self, self.receptiveCells, self.cells.keys())
            
    def __eq__(self, other):
        if  not isinstance(other, Snowflake):
            return False
        if (self.alpha == other.alpha
            and self.beta == other.beta 
            and self.gamma == other.gamma):
                return True

    #from doi:10.1016/j.chaos.2004.06.071
    def mainAlgorithm(self):
        
        
        for cell in self.cells:
            if cell in self.receptiveCells:
                self.u[cell] = 0
                self.v[cell] = self.cells[cell].getState()
            else:
                self.u[cell] = self.cells[cell].getState()
                self.v[cell] = 0

        uNew = dict()
        for u in self.u:
            neighbours = hexGrid.getNeighbours(u[0], u[1])
            sum = 0
            for cell in neighbours:
                if cell in self.cells:
                    sum += self.u[cell]
            c1 = 1/2
            c2 = 1/12
            uNew[u] = c1 * self.u[u] + c2 * sum
        self.u = uNew

        for v in self.receptiveCells:
            if v in self.v:
                self.v[v] = self.v[v] + self.gamma

        for cell in self.u:
            newState = self.u[cell] + self.v[cell]
            b = self.cells[cell].setState(newState, self, self.receptiveCells, self.cells.keys())
            if b: 
                print("return in mainalg")
                return True