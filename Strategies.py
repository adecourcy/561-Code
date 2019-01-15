import math
import learn_capacity_reliability
import optimize
from copy import deepcopy
from numpy import random

# These are likely to be our common variables
PACKETS_RETURNED = 'traffic_response'
COST = 'cost'
SPEED = 'speed'
CAPACITY = 'capacity'
RELIABILITY = 'reliability'
PRIOR_VALUES = 'prior_vals'
PRIOR_MU = 'prior_mu'
PRIOR_VAR = 'prior_var'
PRIOR_ALPHA = 'prior_alpha'
PRIOR_BETA = 'prior_beta'

# Any strategy must conform to the following parameters:
#
# It must have exactly 4 outward functions, taking the exact parameters listed,
# (where "strategyname" may be substituted for any name consistent across all
#  functions):
#
#     strategyname_initial_info(numberOfNetworks,
#                               priorityWeights) -> currentStrategyInfo
#
#     strategyname_initial_load_balance(currentStrategyInfo,
#                                       numberOfNetworks,
#                                       priorityWeights) -> packetDistribution
#
#     strategyname_update_info(currentStrategyInfo,
#                              trafficSentToNetwork,
#                              networkResponse,
#                              priorityWeights,
#                              packetGenerationParameters) -> currentStrategyInfo
#
#     strategyname_update_load(currentStrategyInfo,
#                              numNetworks,
#                              priorityWeights,
#                              packetDistribution
#                              packetGenerationParameters) ->
#                                   packetDistribution
#
# Parameter names are not strict. Further, currentStategyInfo may be of any type.
# Finally, the parameters  have the following, specific structure:
#
# numberOfNetworks:
#   An integer, representing the number of networks in the simulation
#
# priorityWeights:
#   A dictionary mapping network parameter names to normalized priority weight
#   values. 'traffic_response' is guaranteed to be in this dictionary, all
#   other values are subjective to the specific parameters provided to the
#   program. The parameter names in this dictionary correspond directly to the
#   network parameter names.
#
# trafficSentToNetwork:
#   A list of integers, with each entry corresponding to the number of packets
#   sent to that entry's network number on the previous time step. For example,
#   [3,5,2] means the node sent 3 packets to the first network, 5 to the second
#   network, and 2 packets to the third network
#
# networkResponse:
#   A list of dictionaries. Each dictionary in the list represents the response
#   of a network (ordered). Each dictionary has all of the dictionary response
#   values, such as the capacity, reliability, and number of packets returned 
#   in that round. For our purposes, the capacity and reliability values should
#   remain hidden from the source node, but they are there for testing purposes.
#   The keys of the dictionary are dependent on the given network parameters,
#   but the number of packets return is set to the variable PACKETS_RETURNED.
#   There are variables for the other standard values of COST, SPEED, RELIABILITY,
#   and CAPACITY
#
# packetGenerationParameters:
#   A list of integers, where the first entry represents the mean number of
#   packets the node generates, and the second represents the standard deviation
#
# packetDistribution:
#   A list of floats, the length of numberOfNetworks. The floats sum to 1, with
#   each entry representing the percentage of generated packets the node should
#   send to that number network.
#
#
# The exact meaning of these variables will be determined by the specific strategy.
# However, the first entry of 'networkParameters' will always be 'packets_returned',
# which is the global constant PACKETS_RETURNED in this file


###############################################################################
#
# Final learning strategy (need to update optimization)
#
###############################################################################
  

def final_initial_info(numNetworks,
                       priorityWeights):

  prior_vals = {PRIOR_MU: 1.0,
                PRIOR_VAR: 0.1,
                PRIOR_ALPHA: 1.0,
                PRIOR_BETA: 1.0}
  
  prior_capacity = {PRIOR_MU: 0,
                    PRIOR_VAR: 0,
                    PRIOR_ALPHA: 0,
                    PRIOR_BETA: 0}

  prior_reliability = {PRIOR_MU: 0}

  prior_vars = {COST: deepcopy(prior_vals),
                SPEED: deepcopy(prior_vals),
                CAPACITY: deepcopy(prior_capacity),
                RELIABILITY: deepcopy(prior_reliability)}
  
  #keep_number_of_packets = max(5*numNetworks,10)
  keep_number_of_packets = 10
  
  current_iteration = 0
  
  packet_record = [[] for i in range(keep_number_of_packets)]
  
  return {PRIOR_VALUES: [deepcopy(prior_vars) for i in range(numNetworks)],
          'packet_record': [deepcopy(packet_record) for i in range(numNetworks)],
          'keep_packets': keep_number_of_packets,
          'current_iteration': current_iteration}



def final_initial_load_balance(initialInfo,
                                numNetworks,
                                weights):
  
  return [1/numNetworks for i in range(numNetworks)]




def final_update_info(currentStrategyInfo,
                       trafficSentToNetwork,
                       networkResponse,
                       weights,
                       trafficDistributionParameters):
  
  changePacket = \
      currentStrategyInfo['current_iteration'] % \
      currentStrategyInfo['keep_packets']
  
  currentStrategyInfo['current_iteration'] += 1
  
  for netNum in range(len(networkResponse)):
    
    currentStrategyInfo['packet_record'][netNum][changePacket] = \
        [trafficSentToNetwork[netNum], networkResponse[netNum][PACKETS_RETURNED]]
    
    currentPacketRecord = currentStrategyInfo['packet_record'][netNum]
    
    observedCost = networkResponse[netNum][COST]
    observedSpeed = networkResponse[netNum][SPEED]
    
    cost_mu, cost_v, cost_a, cost_b = \
        learn_capacity_reliability.NormGamma_update(observedCost,
                         currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_MU],
                         currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_VAR],
                         currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_ALPHA],
                         currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_BETA])
    
    currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_MU] = cost_mu
    currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_VAR] = cost_v
    currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_ALPHA] = cost_a
    currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_BETA] = cost_b
    
    
    speed_mu, speed_v, speed_a, speed_b = \
        learn_capacity_reliability.NormGamma_update(observedSpeed,
                         currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_MU],
                         currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_VAR],
                         currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_ALPHA],
                         currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_BETA])
    
    currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_MU] = speed_mu
    currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_VAR] = speed_v
    currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_ALPHA] = speed_a
    currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_BETA] = speed_b
    
    if currentStrategyInfo['current_iteration'] % currentStrategyInfo['keep_packets'] == 0:
      if currentStrategyInfo['current_iteration'] == currentStrategyInfo['keep_packets']:
        
        capacity_mu,capacity_std,reliability,learn_c = \
            learn_capacity_reliability.learn_prior(currentPacketRecord,
                                 trafficDistributionParameters[0],
                                 trafficDistributionParameters[1])
        
        currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_MU] = capacity_mu
        currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_VAR] = 2.0
        currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_ALPHA] = 2.0
        currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_BETA] = \
          (capacity_std**2) * currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_ALPHA]
        currentStrategyInfo[PRIOR_VALUES][netNum][RELIABILITY][PRIOR_MU] = reliability
        
      else:
        capacity_mu,capacity_std,reliability,learn_c = \
            learn_capacity_reliability.learn_prior(currentPacketRecord,
                                 trafficDistributionParameters[0],
                                 trafficDistributionParameters[1])

        reliability_mem = currentStrategyInfo[PRIOR_VALUES][netNum][RELIABILITY][PRIOR_MU]
        currentStrategyInfo[PRIOR_VALUES][netNum][RELIABILITY][PRIOR_MU] = (reliability+reliability_mem)/2
        if learn_c:
          prior_mu, prior_v, prior_a, prior_b = \
                learn_capacity_reliability.NormGamma_update(capacity_mu,
                                 currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_MU],
                                 currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_VAR],
                                 currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_ALPHA],
                                 currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_BETA])
            
          currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_MU] = prior_mu
          currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_VAR] = prior_v
          currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_ALPHA] = prior_a
          currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_BETA] = prior_b 

  return currentStrategyInfo




def final_update_load(currentStrategyInfo,
                         numNetworks,
                         weights,
                         oldLoad,
                         trafficDistributionParameters):
  capacityMeans = []
  capacityStdDevs = []
  coefficients = []

  if currentStrategyInfo['current_iteration'] < currentStrategyInfo['keep_packets']:
    i = random.randint(low = 0, high = numNetworks)
    p = random.uniform(0,1)
    if p < 0.5 or numNetworks == 1:
      updatedLoad = [0] * numNetworks
      updatedLoad[i] = 1
    else:
      updatedLoad = [0.4/(numNetworks-1)] * numNetworks
      updatedLoad[i] = 0.6     

  elif currentStrategyInfo['current_iteration'] % currentStrategyInfo['keep_packets'] == 0:

    for netNum in range(numNetworks):
      capacityAlpha = currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_ALPHA]
      capacityBeta = currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_BETA]
      costMean = currentStrategyInfo[PRIOR_VALUES][netNum][COST][PRIOR_MU]
      speedMean = currentStrategyInfo[PRIOR_VALUES][netNum][SPEED][PRIOR_MU]
      
      capacityMeans.append(currentStrategyInfo[PRIOR_VALUES][netNum][CAPACITY][PRIOR_MU])
      capacityStdDevs.append(math.sqrt(capacityBeta / capacityAlpha))
      coefficients.append((costMean*weights[COST] + \
                          speedMean*weights[SPEED] + \
                          weights[PACKETS_RETURNED]) * \
                          currentStrategyInfo[PRIOR_VALUES][netNum][RELIABILITY][PRIOR_MU])
    
    #print(capacityMeans,capacityStdDevs,reliability)

    newLoad = optimize.solve_opt(capacityMeans,
                                 capacityStdDevs,
                                 coefficients,
                                 trafficDistributionParameters[0] + \
                                 trafficDistributionParameters[1])
    
    newLoadSum = sum(newLoad)
    newLoad = [x/newLoadSum for x in newLoad]
    
    updatedLoad = []
    for index in range(len(newLoad)):
      updatedLoad.append((newLoad[index] + oldLoad[index]) / 2)
  
  else:
    updatedLoad = oldLoad

  return updatedLoad

