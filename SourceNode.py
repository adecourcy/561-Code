import Strategies
import random
import math
from copy import deepcopy

NAME = 'name'
STRATEGY_UPDATE = 'strategy_update'
STRATEGY_INFO = 'strategy_info'
CURRENT_LOAD_BALANCE = 'current_load_balance'
LOAD_BALANCE_UPDATE = 'load_balance_update'
DISTRIBUTION = 'distribution'
WEIGHTS = 'weights'
DISTRIBUTION_PARAMETERS = 'distribution_parameters'



###############################################################################
#
# Internal Functions
#
###############################################################################



####################################
#
# Distributions
#
####################################

def _gaussian(nodeName,
              distributionParameters):
  
#  if "dist_mean" not in distributionParameters or \
#     "dist_variance" not in distributionParameters:
#    print()
#    print('Invalid parameters provided for {} distribution.'.format(nodeName))
#    print()
#    print('Need:\ndist_mean\ndist_variance')
#    print()
#    print('Given:')
#    for param in distributionParameters:
#      print(param)
#    print()
#    exit()
#    
    
  if len(distributionParameters) != 2:
    print("For node: {} expected 2 parameters, got {}".format(nodeName,
                                                              len(distributionParameters)))
  
  return (random.gauss,
            (distributionParameters[0],
             distributionParameters[1]))


####################################
#
# node Functions
#
####################################
  
def _normalizeWeights(priorityWeights):
  
  total = 0
  for entry in priorityWeights:
    total += priorityWeights[entry]
  
  for entry in priorityWeights:
    priorityWeights[entry] /= total
  
  return priorityWeights



def _updateNodeStrategyInfo_safe(node,
                                 trafficSent,
                                 networkResponse):
  
  newNode = deepcopy(node)
  
  newNode[STRATEGY_INFO] = \
      newNode[STRATEGY_UPDATE](newNode[STRATEGY_INFO],
                               trafficSent,
                               networkResponse,
                               newNode[WEIGHTS],
                               newNode[DISTRIBUTION_PARAMETERS])
  
  return newNode


def _updateNodeStrategyInfo_fast(node,
                                 trafficSent,
                                 networkResponse):
  
  node[STRATEGY_INFO] = \
      node[STRATEGY_UPDATE](node[STRATEGY_INFO],
                            trafficSent,
                            networkResponse,
                            node[WEIGHTS],
                            node[DISTRIBUTION_PARAMETERS])
  
  return node



def _updateLoadBalance_safe(node,
                            numNetworks):
  
  newNode = deepcopy(node)
  
  newNode[CURRENT_LOAD_BALANCE] = \
      newNode[LOAD_BALANCE_UPDATE](node[STRATEGY_INFO],
                                   numNetworks,
                                   newNode[WEIGHTS],
                                   newNode[CURRENT_LOAD_BALANCE],
                                   newNode[DISTRIBUTION_PARAMETERS])
  
  return newNode



def _updateLoadBalance_fast(node,
                            numNetworks):
  
  node[CURRENT_LOAD_BALANCE] = \
      node[CURRENT_LOAD_BALANCE](node[STRATEGY_INFO],
                                 numNetworks,
                                 node[WEIGHTS],
                                 node[CURRENT_LOAD_BALANCE],
                                 node[DISTRIBUTION_PARAMETERS])

  return node



def _generatePackets(node,
                     rounding=math.ceil):
  # Grab the distribution information from the node structure. This information
  # is a tuple of the form (distribution function, distribution parameters)
  # where the distribution parameters are a tuple themselves. Pass the parameters
  # to the function through tuple unpacking and round to the nearest integer
  # according to the provided method.
  return max(rounding(node[DISTRIBUTION][0](*node[DISTRIBUTION][1])), 0)



def _createCDF(loadPMF):
  loadCDF = []
  CDF = 0
  for PMF in loadPMF:
    CDF += PMF
    loadCDF.append(CDF)
  loadCDF[-1] = 1
  return loadCDF


###############################################################################
###############################################################################


###############################################################################
#
# Forward-facing Functions
#
###############################################################################
  
def updateNodeStrategy(node,
                       numNetworks,
                       trafficSent,
                       networkResponse):
  
  newNode = _updateNodeStrategyInfo_safe(node,
                                         trafficSent,
                                         networkResponse)
  
  newNode = _updateLoadBalance_safe(newNode,
                                    numNetworks)
  
  return newNode



def getTraffic(node):
  loadBalanceCDF = _createCDF(node[CURRENT_LOAD_BALANCE])
  numPackets = _generatePackets(node)
  
  trafficDistribution = []
  for load in node[CURRENT_LOAD_BALANCE]:
    trafficDistribution.append(math.floor(load * numPackets))
  
  numPackets -= sum(trafficDistribution)
  
  for i in range(numPackets):
    assignment = random.uniform(0, 1)
    for entry in range(len(loadBalanceCDF)):
      # _create CDF should ensure the last entry is 1
      if assignment <= loadBalanceCDF[entry]:
        trafficDistribution[entry] += 1
        break
  
  return trafficDistribution



# Need to incorporate current node strategy info (i.e. how node will act)
def createSourceNode(nodeName,
                     numNetworks,
                     distributionParameters,
                     nodeStrategy,
                     priorityWeights,
                     distribution='_gaussian'):
  """
    Takes node parameters and returns a node object (dictionary)
    
    Input:
      
      nodeName:
        A string naming the current node
      
      numNetworks:
        An integer telling how many networks there are on the system
      
      distributionParameters:
        A tuple of numbers representing distribution parameters. Values are
        dependent on the type of distribution from which the node is expected
        to generate traffic
      
      nodeStrategy:
        A string naming the node's update strategy
      
      priorityWeights:
        A dictionary network parameter names to node priority weight values.
        The values will be normalized.
      
      distribution:
        A function name for the distribution the node generates traffic from.
        Defaults to gaussian.
  """
  
  priorityWeights = _normalizeWeights(priorityWeights)
  
  initialInfo = \
      getattr(Strategies, nodeStrategy + '_initial_info')(numNetworks,
                                                          priorityWeights)
  
  initialLoadBalance = \
      getattr(Strategies, nodeStrategy + '_initial_load_balance')(initialInfo,
                                                                  numNetworks,
                                                                  priorityWeights)
  
  return {NAME: nodeName,
          STRATEGY_UPDATE: getattr(Strategies, nodeStrategy + '_update_info'),
          LOAD_BALANCE_UPDATE: getattr(Strategies, nodeStrategy + '_update_load'),
          CURRENT_LOAD_BALANCE: initialLoadBalance,
          STRATEGY_INFO: initialInfo,
          DISTRIBUTION: eval(distribution)(nodeName, distributionParameters),
          WEIGHTS: priorityWeights,
          DISTRIBUTION_PARAMETERS: distributionParameters}

###############################################################################
###############################################################################



if __name__ == '__main__':
  testNode = createSourceNode('testNode',
                              3,
                              (5,1),
                              'tStrat')
  
  print(getTraffic(testNode))
  print(getTraffic(testNode))
  print(getTraffic(testNode))
  
  testNode = updateNodeStrategy(testNode, 3, [3,5,1], [1,1,1], [1,1,1])

  input()
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  