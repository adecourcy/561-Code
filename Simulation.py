import SourceNode
import Network

def _transposeList(inputMatrix):
  transposed = []
  
  for colNum in range(len(inputMatrix[0])):
    newRow = []
    for rowNum in range(len(inputMatrix)):
      newRow.append(inputMatrix[rowNum][colNum])
    transposed.append(newRow)
  
  return transposed



def _writeEntry(entry,
                outFile,
                timeStep,
                nodeNames,
                networks):
  
  with open(outFile, 'a+') as f:
    f.write('[{}]\n'.format(timeStep))
    
    for nodeName, \
        nodeTraffic, \
        nodeResponse, \
        loadBalance in zip(nodeNames, entry[0], entry[1], entry[3]):
      
      trafficString = ' '.join([str(x) for x in nodeTraffic])
      balanceString = ' '.join([str(x) for x in loadBalance])
      responseString = ' '.join([str(x) for x in nodeResponse])
      
      f.write('{1}_traffic = {2}\n{1}_load = {3}\n{1}_response = {4}\n'.format(nodeName,
                                                                               trafficString,
                                                                               balanceString,
                                                                               responseString))
      
      
    for network, params in zip(networks, entry[2]):
      netName = network[Network.NAME]
      paramString = ' '.join([str(x) for x in params])
      f.write('{}_parameters = {}'.format(netName, paramString))



def _getLoadBalance(nodes):
  loadBalance = []
  for node in nodes:
    loadBalance.append(node[SourceNode.CURRENT_LOAD_BALANCE][:])
  return loadBalance



def _getNames(nodes):
  names = []
  for node in nodes:
    names.append(node[SourceNode.NAME])
  return names



def _getNodeString(nodes,
                   values,
                   appendString):
  
  nodeString = []
  
  for node, value in zip(nodes, values):
    nodeString.append(node[SourceNode.NAME] + appendString + " = " + str(value))
  
  return '\n'.join(nodeString)



def _getNetworkString(networks,
                      values):
  
  networkString = []
  
  for network, value in zip(networks, values):
    networkString.append(network[Network.NAME] + " = " + str(value))
  
  return '\n'.join(networkString)



def _writeData(oldData,
               allTraffic,
               trafficResponses,
               selectedParams,
               outputFile,
               nodes,
               networks,
               timeStep,
               buffer):
  
  
  timeStepString = '[{}]\n'.format(timeStep)
  timeStepString += _getNodeString(nodes,
                                   allTraffic,
                                   '-traffic_sent') + '\n'
  timeStepString += _getNodeString(nodes,
                                   trafficResponses,
                                   '-traffic_response') + '\n'
  timeStepString += _getNodeString(nodes,
                                   [node[SourceNode.CURRENT_LOAD_BALANCE] for node in nodes],
                                   '-load_balance') + '\n'
  timeStepString += _getNodeString(nodes,
                                   [node[SourceNode.STRATEGY_INFO] for node in nodes],
                                   '-strategy_info') + '\n'
  timeStepString += _getNodeString(nodes,
                                   [node[SourceNode.WEIGHTS] for node in nodes],
                                   '-weights') + '\n'
  timeStepString += _getNetworkString(networks,
                                      selectedParams) + '\n\n'
  
  if len(oldData) >= buffer:
    with open(outputFile, 'a') as f:
      for entry in oldData:
        f.write(entry)
    oldData = []
  
  oldData.append(timeStepString)
  
  return oldData



# TODO: Data output
def executeSimulation(timeSteps,
                      nodes,
                      networks,
                      outFile):
  
  # Clear the output file contents, if the file exists
  f = open(outFile, 'w')
  f.close()
  
  numNetworks = len(networks)
  data = []
  
  for step in range(timeSteps):
    
    allTraffic = []
    for node in nodes:
      allTraffic.append(SourceNode.getTraffic(node))
    transposedTraffic = _transposeList(allTraffic)
    
    allResponses = []
    allSelectedParams = []
    
    for network, netTraffic in zip(networks, transposedTraffic):
      response, selectedParam = \
          Network.generateNetworkResponse(network, netTraffic)
      allResponses.append(response)
      allSelectedParams.append(selectedParam)
    allResponses = _transposeList(allResponses)
    
    
    newNodes = []
    for node, responseSet, trafficSent in zip(nodes, allResponses, allTraffic):
      newNodes.append(SourceNode.updateNodeStrategy(node,
                                                    numNetworks,
                                                    trafficSent,
                                                    responseSet))
    
    data = _writeData(data,
                      allTraffic,
                      [[nodeResponse['traffic_response'] for nodeResponse in response] for response in allResponses],
                      allSelectedParams,
                      outFile,
                      newNodes,
                      networks,
                      step,
                      1000) # buffer size.
    
    nodes = newNodes
  
  data = _writeData(data,
                    allTraffic,
                    [[nodeResponse['traffic_response'] for nodeResponse in response] for response in allResponses],
                    allSelectedParams,
                    outFile,
                    nodes,
                    networks,
                    step,
                    0)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    