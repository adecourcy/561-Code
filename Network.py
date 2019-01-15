import Metrics

NAME = 'net_name'
PARAMS = 'net_params'
MET_FUNC = 'met_func'


def generateNetworkResponse(network,
                            traffic):
  
  return network[MET_FUNC](traffic,
                           network[PARAMS])



def createNetwork(netName,
                  parameters,
                  metricsFunction):
  
  """
    Takes network parameters and returns a network object (dictionary)
    
    Input:
      
      netName:
        A string naming the current network
      
      parameters:
        A dictionary mapping parameter names to tuples containing parameter
        distribution values.
      
      metricsFunction:
        A string naming the function for generating the networks parameters
        
  """
  
  
  return {NAME: netName,
          PARAMS: parameters,
          MET_FUNC: getattr(Metrics, metricsFunction)}