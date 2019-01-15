import sys
import ParseFile
import Simulation


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print("This program takes exactly 3 arguments, structured as follows:")
    print("main.py [simulation time steps] [config file] [output file]")
    exit()
  
  sys.stdout = open("out.log", 'w')
  
  timeSteps = int(sys.argv[1])
  nodes, networks = ParseFile.parseInput(sys.argv[2])
  outFile = sys.argv[3]
  Simulation.executeSimulation(timeSteps, nodes, networks, outFile)