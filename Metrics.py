import math
import random
from copy import deepcopy


# Any metric must conform to the following parameters
#
# It must have exactly one outward function, taking exactly the parameters listed:
#
#     metricName(trafficRecieved,
#                networkParameters) -> (networkResponse, chosenParameters)
#
# Parameters and return values are defined strictly as follows, but parameter
# naming is not strict:
#
# trafficRecieved:
#   trafficRecieved is a list of integers. Each entry in the list represents
#   the number of packets recieved by a source node (consistently ordered by
#   node order to program)
#
# networkParameters:
#   networkParameters is a dict associating network parameter names with tuple
#   values containing network parameter distribution values
#
# networkResponse:
#   networkRespone is a list of of lists of dicts. Each element of the list
#   corresponds to the networkResponse to a particular source node. The
#   dictionary maps parameter names to returned parameter values. The parameter
#   names in the dict must match exactly with the node parameter names, and
#   must include the name 'traffic_response'
#
# chosenParameters:
#   A dict containing the randomly select parameters for the network at this
#   particular time-step. For example, if we are considering network capacity
#   and cost only, and the 5 is randomly selected for the network capacity on
#   this time step, and 2 as the cost, the return value would be
#   {capacity: 5, cost: 2}
#
#
# Metrics functions may use the internal function _returnTraffic to generate
# the returned packets, rather than implementing a specific return function
# to calculate this.




# !!!!!!! MAKE SURE TO LOWER BOUND ALL RANDOM PARAMETERS BY 0 !!!!!!!


def _repeatedPacketList(traffic):
  
  packetRepetitions = []
  
  for entryNum in range(len(traffic)):
    for i in range(traffic[entryNum]):
      packetRepetitions.append(entryNum)
  
  return packetRepetitions


def _compressRepeatedPacketList(repeatedPacketList,
                                numSources):
  
  compressedList = []
  
  for i in range(numSources):
    compressedList.append(0)
  
  for entry in repeatedPacketList:
    compressedList[entry] += 1
  
  return compressedList



def _returnTraffic(trafficRecieved,
                   networkCapacity,
                   networkReliability,
                   rounding=round):
  """
    Takes traffic and network information and returns traffic sent back
    
    Input:
      
      trafficRecieved:
        A list of integers, each entry corresponding to the number of packets
        sent from a specific node
      
      networkCapacity:
        An integer representing the total number of packets the network can
        carry on this time-step
      
      networkReliability:
        A float <= 1, which represents the percentage of packets that are 
        returned in total (i.e. 0.8 means that 20% of packets are lost)
  """
  
  totalPackets = sum(trafficRecieved)
  
  if totalPackets <= networkCapacity:
    carriedThrough = totalPackets
  else:
    carriedThrough = networkCapacity
  
  carriedThrough = rounding(carriedThrough * networkReliability)
  
  if carriedThrough == 0:
    returnedTraffic = []
    for i in range(len(trafficRecieved)):
      returnedTraffic.append(0)
    return returnedTraffic
  
  returnedTraffic = \
      _compressRepeatedPacketList(
          random.sample(
              _repeatedPacketList(trafficRecieved),
              carriedThrough),
      len(trafficRecieved))
  
  return returnedTraffic




def testMetric(trafficRecieved,
               networkParameters):
  
  chosenParams = {}
  returnedParams = {}
  
  for param in networkParameters:
    paramVal = max(random.gauss(networkParameters[param][0],
                                networkParameters[param][1]),0)
    chosenParams[param] = paramVal
    if param != 'capacity' or param != 'reliability':
      returnedParams[param] = paramVal
  
  chosenParams['reliability'] = min(chosenParams['reliability'], 1)
  
  packetsReturned = _returnTraffic(trafficRecieved,
                                   chosenParams['capacity'],
                                   chosenParams['reliability'])
  
  response = []
  for packets in packetsReturned:
    copiedRetParams = deepcopy(returnedParams)
    copiedRetParams['traffic_response'] = packets
    response.append(copiedRetParams)
  
  return (response, chosenParams)



if __name__ == '__main__':
  response = testMetric(100, [(0,1),(100,1)], ['bob', 'bill'])
  
#  repeatedPackets = _repeatedPacketList([3,2,1])
#  print(repeatedPackets)
#  compressed = _compressRepeatedPacketList(repeatedPackets, 4)
#  print(compressed)
































