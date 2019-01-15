import configparser
import SourceNode
import Network

# Configuration files are somewhat flexible, but should follow a certain format.
#
# The first entry in the configuration file contain the following entries:
#     netParameters = a python list format of string descriptions of network
#                     parameters (ex. ['capacity', 'reliability', 'cost'])
#     nodeParameters = a python list format of string descriptions of network
#                      parameters the node is aware of. Using the example above,
#                      the entry would be ['cost'], as the node may be trying
#                      measure the network capacity and reliability but it does
#                      not get this information directly from the network.
#                      The entry "traffic_respons" will be automatically be
#                      added to this list.
#
# Both networks and nodes should not be expected to retain the configuration
# file ordering. If order is to be preserved, numbering should be provided.
#
# All networks, regardless of name, should contain the string 'network', and
# not contain the string 'node'
#
# All nodes, regardless of name, should contain the sting 'node', and not
# contain the string 'network'
#
# All networks should contain the following parameters:
#   metricParameters = list format, containing tuples of parameters, ordered
#                      by the parameters section at the top of the config file
#                     ex. [(5,2), (0.3,1), (6,2)]
#   metrics = the name of a metrics function to be used by the network
#
# All nodes should contain the following parameters, named exactly:
#   strategy = strategy name (as string)
#   parameters = traffic distribution parameters (as space separated numbers)
#   weights = priority weights for node parameters (list formatted numbers))
#             ex. [0.25, 0.3, 0.1, 0.35]. This should correspond to the ordering
#             of the node parameters entry, with 1 additional parameter for 
#             'traffic_response' at the end of the list.
#
# All nodes make have one additional parameter, defining their distribution
# (defaults to gaussian):
#   distribution = distribution name (string naming a distribution function
#                                     in the SourceNode file)

def _parseNodeInfo(nodes,
                   nodeName,
                   nodeInfo,
                   numNetworks,
                   paramNames):
  
  weights = {}
  for parameter, weight in zip(paramNames, eval(nodeInfo['weights'])):
    weights[parameter] = weight
  
  if 'distribution' not in nodeInfo:
    newNode = \
      SourceNode.createSourceNode(nodeName,
                                  numNetworks,
                                  tuple([float(x) for x in nodeInfo['parameters'].split()]),
                                  nodeInfo['strategy'],
                                  weights)
  else:
    newNode = \
      SourceNode.createSourceNode(nodeName,
                                  numNetworks,
                                  tuple([float(x) for x in nodeInfo['parameters'].split()]),
                                  nodeInfo['strategy'],
                                  weights,
                                  nodeInfo['distribution'])
  
  nodes.append(newNode)
  
  return nodes



def _parseNetworkInfo(networks,
                      netName,
                      networkInfo,
                      paramNames):
  
  metricFunction = networkInfo['metrics']
  parameterValues = eval(networkInfo['metricParameters'])
  parameters = {}
  
  for metrics, name in zip(parameterValues, paramNames):
    parameters[name] = metrics
  
  networks.append(Network.createNetwork(netName,
                                        parameters,
                                        metricFunction))
  
  return networks



def parseInput(fileName):
  
  config = configparser.ConfigParser()
  config.read(fileName)
  
  
  networks = []
  nodes = []
  
  netParams = eval(config['parameters']['netParameters'])
  nodeParams = eval(config['parameters']['nodeParameters'])
  nodeParams.append('traffic_response')
  
  for entry in config:
    if 'network' in entry:
      networks = _parseNetworkInfo(networks,
                                   entry,
                                   config[entry],
                                   netParams)
  
  for entry in config:
    if 'node' in entry:
      nodes = _parseNodeInfo(nodes,
                             entry,
                             config[entry],
                             len(networks),
                             nodeParams)
  
  return (nodes, networks)



if __name__ == '__main__':
  parseInput('test.conf')





































