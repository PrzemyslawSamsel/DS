from collections import namedtuple
from random import choice, randint
from time import sleep
from threading import Thread
from datetime import datetime, timedelta
from os import system

class Site:
  def __init__(self, name, holder=None):
    # Queue stores info about neighbors that have sent a request for the token to he site Si
    # Non-empty indicates that the site has sent a REQ to the root
    self.request_q : list[Site] = []
    # Pointing to a neighbor 
    self.holder:Site = holder
    self.name = name
    self.workedInCS = False
  #
  def request(self, requestingNode):
    sleep(1)
    # If not the root node
    if self.holder:
      # If request_q is empty, send request to parent
      if not len(self.request_q):
        self.push(self)
        self.push(requestingNode)
        print("Inside request. Sending request => ", self.holder.name)
        # If haven't already worked in CS, request it
        if not self.workedInCS:
          self.holder.request(self)
    # If its root node, and work is finished, pass token
    else:
      self.push(requestingNode)
      print("Waiting for work to finish, then passing token")
      # Wait until token is released
      while System.csTaken:
        sleep(0.25)
        System.csTaken = System.checkCS()
      descendant = self.pop()
      self.holder = descendant
      self.holder.passToken()
  #
  def pop(self):
    return self.request_q.pop()
  #
  def push(self, value):
    self.request_q.append(value)
  #
  def setHolder(self, holder):
    self.holder = holder
  #
  def passToken(self):
    print("Token passed to me : ", self.name)
    sleep(1)
    if len(self.request_q):
      # If current node has only itself on the queue
      descendant = self.pop()
      if descendant == self:
        print("Descendant is me - ", descendant.name, " I am new root!")
        System.currentCS = self
        self.workedInCS = True
        System.doCSWork()
        System.done.append(self)
        System.printState()

        # Wait for critical section to finish
        #while System.csTaken:
        #  sleep(0.25)
        #System.csTaken = System.checkCS()
        #descendant.passToken()
        #last step here?
      
      # If current node has another descendant in the queue
      # Pass token to first descendant
      else:
        print("Token passed to NEW descendant => ", descendant.name)
        # reverse the tree
        self.holder = descendant
        descendant.passToken()
        if len(self.request_q):
          descendant.request(self)
#

# A (B(D,E),C(F,G))
class System:
  csTaken    = False
  deadlineCS = None
  currentCS  = None
  newCSCandidate= None
  done = []
  nodes = None

  def __init__(self):
    names = ['A','B','C','D','E','F','G']
    nodeslist = namedtuple('nodes', names)
    System.nodes = nodeslist(*[Site(name) for name in names])
    # Current root is also CS node
    System.currentCS = self.nodes.A
    System.currentCS.workedInCS = True
    System.done.append(System.currentCS) # nodes that already finished their CS
    self.setStructure()
  #

  def getRandomNode(self):
    return choice(list(set(self.nodes) - set(System.done)))
  #

  def setStructure(self):
    System.nodes.E.setHolder(System.nodes.B)
    System.nodes.D.setHolder(System.nodes.B)
    System.nodes.F.setHolder(System.nodes.C)
    System.nodes.G.setHolder(System.nodes.C)
    System.nodes.B.setHolder(System.nodes.A)
    System.nodes.C.setHolder(System.nodes.A)
  #

  @classmethod
  def doCSWork(cls, timeToWork=randint(3,8)):
    System.csTaken = True
    # time for the current CS node to 
    # finish its work and pass token
    System.deadlineCS = datetime.now() +\
       timedelta(seconds=timeToWork)
    #

  # Check whether node finished its CS
  @classmethod
  def checkCS(cls):
    return datetime.now() > System.deadlineCS
  #

  def animate(self):
    # First node that enters its CS
    System.doCSWork()

    try:
      print(f"[*] Currently in CS: [{System.currentCS.name}]  Deadline: [{System.deadlineCS}]")
      for node in self.nodes:
        state = 'Waiting'
        if System.newCSCandidate == node:
          state = 'Applying'
        if node.workedInCS:
          state = 'Done'
        print(f"[*] Node [{state}][{node.name}] ::=> [{node.holder.name if node.holder else None}] :: Que => {[x.name for x in node.request_q]}")
      while True:
        # Started with B. Problem is, when D finishes it's job, it needs to ping B back, but B it's not in its que. 
        # How comes? 
        System.newCSCandidate = self.getRandomNode() #self.nodes.G # F? 
        print("the new node: ", System.newCSCandidate.name)
        print("Sending request to => ", System.newCSCandidate.holder.name)
        System.newCSCandidate.push(System.newCSCandidate)
        System.newCSCandidate.holder.request(System.newCSCandidate)
        if len(self.done) == 7:
          print([x.name for x in self.done])
          print("Finished. Exiting. ")
          exit(0)

    except KeyboardInterrupt:
      exit(0)
    #
  
  # prints current state of the network
  @classmethod
  def printState(cls):
        print(f"[*] Currently in CS: [{System.currentCS.name}]  Deadline: [{System.deadlineCS}]")
        for node in System.nodes:
          state = 'Waiting'
          if System.newCSCandidate == node:
            state = 'Applying'
          if node.workedInCS:
            state = 'Done'
          print(f"[*] Node [{state}][{node.name}] ::=> [{node.holder.name if node.holder else None}] :: Que => {[x.name for x in node.request_q]}")
        #sleep(0.1)
        #system('cls')
#


net = System()
net.animate()