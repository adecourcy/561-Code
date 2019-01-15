from scipy.stats import norm
import numpy as np
from scipy.optimize import curve_fit

def learn_prior(observe, traffic_mu, traffic_std):

	def learn_capacity_prior(observe, traffic_mu, traffic_std):
		learn_c = True

		qualityOfService = np.array(list(item[1]*1.0/item[0] for item in observe))
		censored = qualityOfService == 1
		uncensored_prec = 1 - sum(censored)*1.0/len(censored)
		PacketSent_obs = list(item[0] for item in observe)
		PacketReceive_obs = list(item[1] for item in observe)


		# max([qualityOfService]) <= reliability
		# for a certain time point
		# qualityOfService = 1 -> PacketSent <= capacity
		# qualityOfService < 1 -> packetReceive = capacity

		if min(qualityOfService) == 1: 
		# never hit capacity => unid, guess capacity >= max(PacketSent)
		# min(qualityOfService) =1 => max(qualityOfService) = 1
			capacity_mu = max(traffic_mu + 2*traffic_std,max(PacketSent_obs))
			capacity_std = 5
			learn_c = False
		# print('No learn capacity')

		elif max(qualityOfService) < 1: 
		# max(qualityOfService) < 1 => min(qualityOfService) < 1
		# PacketReceive = capacity at each time point
		# MLE will be mean and std of the observed packetReceive
			capacity_mu = np.mean(PacketReceive_obs)
			capacity_std = np.std(PacketReceive_obs)

		else: 
		# max(qualityOfService) == 1 and min(qualityOfService) < 1
		# hit capacity some time (when qualityOfService < 1)
			uncensored_PacketReceive_observe = [] # hit capacity, PacketReceive = capacity
			censored_PacketReceive_observe = []
			for i in range(len(observe)):
				if censored[i] < 1:
					uncensored_PacketReceive_observe.append(observe[i][1])
				else:
					censored_PacketReceive_observe.append(observe[i][1])

			def logl(observe,mean,std):
			  # P(c|mean,std) = \Pi (if hit) p(c = packetReceive |mean,std) * (not hit)p(c > packetSent = packetreceive  | mean,std)
			    ll = 0
			    for item in observe:
			        if item[1] == item [0]: # not hit
			            ll += np.log(1-norm.cdf(item[1],loc = mean,scale = std))
			        else:
			            ll += np.log(norm.pdf(item[1],loc = mean,scale = std))
			    return ll  

			# find the grid search bound for mean
			low_mean = round(np.mean(uncensored_PacketReceive_observe))
			# [todo]: when traffic_std is big
			upper_mean = max(round(traffic_mu + 2*traffic_std),low_mean + 1)

			# find the grid search bound for std
			low_std = np.std(uncensored_PacketReceive_observe)
			if low_std == 0:
				low_std = 5
				upper_std = 10
			else:
				upper_std = max(low_std*min(1.0/uncensored_prec,5),low_std+0.1)

			# print('capacity mean search range: ', low_mean,upper_mean)
			# print('capacity std search range: ', low_std,upper_std)
			# print('percentage of data uncensored: ', uncensored_prec)

			ll_result = []
			for mean in np.arange(low_mean,upper_mean):
				for std in np.arange(low_std,upper_std,step = 0.1):
					ll_result.append([mean,std,logl(observe,mean,std)]) 

			ll_result = sorted(ll_result,key=lambda x: x[2],reverse = True)
			capacity_mu = ll_result[0][0] 
			capacity_std = ll_result[0][1]

			if capacity_mu == low_mean:
				upper_mean = low_mean + 1
				low_mean = max(censored_PacketReceive_observe) + 1
				# print('Expend mean search lower bound to ', low_mean)
				for mean in np.arange(low_mean,upper_mean):
					for std in np.arange(low_std,upper_std,step = 0.1):
						ll_result.append([mean,std,logl(observe,mean,std)]) 

				ll_result = sorted(ll_result,key=lambda x: x[2],reverse = True)
				capacity_mu = ll_result[0][0] 
				capacity_std = ll_result[0][1]      

		return capacity_mu,capacity_std,learn_c

	observe = [x for x in observe if x[0] > 0 and x[1] > 0]

	if len(observe) == 0:
		capacity_mu = traffic_mu + 2*traffic_std
		capacity_std = 5
		reliability = 0.8
		learn_c = False
	else:
		qualityOfService = list(item[1]*1.0/item[0] for item in observe)
		PacketSent_obs = list(item[0] for item in observe)
		PacketReceive_obs = list(item[1] for item in observe)


		if max(qualityOfService) == 1:
			reliability = 1
			capacity_mu,capacity_std,learn_c = learn_capacity_prior(observe, traffic_mu, traffic_std)
		else:
			reliability = max(qualityOfService)
			observe_adj = list([item[0],min(item[0],np.ceil(item[1]*1.0/reliability))] for item in observe)
			# assume at least one data < capacity
			capacity_mu_nah,capacity_std_nah,learn_c_nah = learn_capacity_prior(observe_adj, traffic_mu, traffic_std)

			# assume all above capacity
			capacity_mu_ah,capacity_std_ah,learn_c_ah = learn_capacity_prior(observe, traffic_mu, traffic_std)
			reliability = (reliability+0.9)/2
			capacity_mu_ah = capacity_mu_ah/reliability

			p_nah = 1 - norm.cdf(min(PacketSent_obs),capacity_mu_nah,capacity_std_nah)
			# p_ah1 = norm.cdf(min(PacketSent_obs),capacity_mu_ah,capacity_std_ah)
			p_ah = 1
			for x in PacketSent_obs:
				p_ah = p_ah*norm.cdf(x,capacity_mu_ah,capacity_std_ah)

			if p_nah > 0.8 and p_ah < 0.2:
				capacity_mu = capacity_mu_nah
				capacity_std = capacity_std_nah
				learn_c = learn_c_nah
			elif p_nah < 0.2 and p_ah > 0.8:
				capacity_mu = capacity_mu_ah
				capacity_std = capacity_std_ah
				learn_c = False
			else:
				if p_nah > p_ah:
					capacity_mu = capacity_mu_nah
					capacity_std = capacity_std_nah
					learn_c = learn_c_nah
				else:
					capacity_mu = capacity_mu_ah
					capacity_std = capacity_std_ah
					learn_c = False
	return capacity_mu,capacity_std,reliability,learn_c

def NormGamma_update(observe,prior_mu,prior_v,prior_a,prior_b):
    prior_a = prior_a + 1.0/2
    prior_b = prior_b + prior_v/(prior_v+1)*(observe-prior_mu)**2/2
    prior_mu = (prior_v*prior_mu+observe)/(prior_v+1)
    prior_v = prior_v + 1
    return prior_mu,prior_v,prior_a,prior_b

def online_update(observe,reliability,prior_mu_c,prior_v_c,prior_a_c,prior_b_c):
  	# high risk of underestimate the capacity when reliability is overestimated because of rounding
    [packetSent,packetReceived] = observe
    packetReceived = min(round(packetReceived/reliability),packetSent)
    print([packetSent,packetReceived])
    mean = prior_mu_c
    std = np.sqrt(prior_b_c/prior_a_c)
    if packetSent == packetReceived: # didn't hit capacity
        if 1-norm.cdf(packetReceived,loc = mean,scale = std) < 0.85:
            (prior_mu_c,prior_v_c,prior_a_c,prior_b_c) = NormGamma_update(packetReceived + std,prior_mu_c,prior_v_c,prior_a_c,prior_b_c)
    else: # hit capacity, packReceived = capacity
        (prior_mu_c,prior_v_c,prior_a_c,prior_b_c) = NormGamma_update(packetReceived,prior_mu_c,prior_v_c,prior_a_c,prior_b_c)

    return prior_mu_c,prior_v_c,prior_a_c,prior_b_c

if __name__ == '__main__':
	print(learn_prior(package_observe[:10], traffic_mu = 100, traffic_std = 5))




