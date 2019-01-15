import numpy as np
from cvxopt import solvers, matrix, spdiag
from scipy.stats import norm, truncnorm
import random
import scipy.integrate as integrate

# optimization problem is
# max f0(x) s.t. sum(x) = p and xi >= 0
# where:
# 
# OPTIMIZATION FUNCTION
# MAX f(x) = sum_i a_i * [ [x_i * (1 - cdf of N(mu_i, sig_i))] + [int_0^x_i N(mu_i, sig_i, x_i)*t dt] ]
#
# ARGS:
# 1. x is # packets sent to each router 
# (xi is # packets sent to router i)
#
# PARAMS:
# 1. p is total number of packets we can send
# 2. We model the number of packets router i accepts from us as
# N(mean=mu_i, stdev=sig_i) distribution
# 3. a_i is multiplicative factor for router i (function of speed, reliability)

######################
# Helper functions
######################

# since cvxopt does minimization instead of maximization
# we multiply everything by -1

# if g(x) is pdf of N(mu, sig)
# evaluate g'(x)
# mu, sig are floats
def eval_norm_deriv(x, mu, sig):
    # added -1 factor below
    return -1 * norm.pdf(x, mu, sig) * ((mu - x) / (sig**2))
    
# compute f(x)
def eval_f(mu, sig, a, x):
    # maybe i should vectorize this, but i'll do a for-loop soln for now
    n = mu.shape[0]
    ans = 0
    for i in range(n):
        # eval xi (1-Phi(xi))
        ans += a[i] * x[i] * (1 - norm.cdf(x[i], mu[i], sig[i]))
        # eval int_{0}^xi N(mu_i, sig_i, x_i)*t dt
        if x[i] > 1e-5:
            ans += a[i] * integrate.quad(lambda t: t*norm.pdf(t, mu[i], sig[i]), 0, x[i])[0]
    # added -1 factor below
    return -1 * ans

# compute column vector of gradient f(x)
def eval_f_grad(mu, sig, a, x):
    # again, doing for-loop soln for now
    n = mu.shape[0]
    f_grad = np.zeros([1,n])
    for i in range(n):
        # deriv of xi (1-Phi(xi))
        f_grad[0,i] = a[i] * (1 - norm.cdf(x[i], mu[i], sig[i]) - (x[i] * norm.pdf(x[i], mu[i], sig[i])))
        # deriv of int_{0}^xi N(mu_i, sig_i, x_i)*t dt
        f_grad[0,i] += a[i] * (x[i] * norm.pdf(x[i], mu[i], sig[i]))
    # added -1 factor below
    return matrix(-1 * f_grad)

# compute Hessian matrix of f
def eval_f_Hess(mu, sig, a, x):
    # cvxopt says to use a sparse matrix
    # so why not
    n = mu.shape[0]
    f_grad_diag = [0 for i in range(n)]
    for i in range(n):
        # second deriv of xi (1-Phi(xi))
        f_grad_diag[i] = a[i] * (-2*norm.pdf(x[i], mu[i], sig[i]) - (x[i] * eval_norm_deriv(x[i], mu[i], sig[i])))
        
        # second deriv of int_{0}^xi N(mu_i, sig_i, x_i)*t dt
        f_grad_diag[i] += a[i] * (x[i] * eval_norm_deriv(x[i], mu[i], sig[i]) + norm.pdf(x[i], mu[i], sig[i]))
        
        # added -1 factor below
        f_grad_diag[i] *= -1
    return spdiag(f_grad_diag)

######################
# Optimization solver
######################

# mu = list of means of capacity of our networks (ordered)
# sig = list of the standard deviations of our networks (ordered)
# a = list of coeffiecents for each network
# p = list of packets we expect to send on each turn
def solve_opt(mu, sig, a, p, init_point=None):
    mu = np.array(mu)
    sig = np.array(sig)
    a = np.array(a)
    n = mu.shape[0]

    # see all the requirements for F here:
    # http://cvxopt.org/userguide/solvers.html#problems-with-nonlinear-objectives
    
    def F(x=None,z=None, init_point=None):
        # if no x, return (0, point in domain of f)
        if x is None:
          if init_point == None:
            init_point = np.zeros(n)
            init_point[0] = p*1.0
          arr = matrix(init_point)
          return 0, arr
        # should be sum(x) != p but need some slack
        if np.abs(np.sum(x) - p) > 1e-5:
            return None
        # if x, calculate f(x) and gradient
        f = eval_f(mu, sig, a, x)
        Df = eval_f_grad(mu, sig, a, x)
        # if no z, then return f, grad
        if z is None:
            return f, Df
        # else, also need to return Hessian
        H = eval_f_Hess(mu, sig, a, x)
        return f, Df, H
    
    
    # compute matrices for linear constraints
    # 1. Gx <= h, G=-1 * I, h = zeros
    G = matrix(-1 * np.identity(n))
    h = matrix(np.zeros([n,1]))
    
    # 2. Ax = b, A = ones(n), b= p
    A = matrix(np.ones([1,n]))
    b = matrix(np.array([p * 1.0]))
    
    # run cvxopt!
    sol = solvers.cp(F, G=G, h=h, A=A, b=b)['x']
    return np.array(sol).flatten().tolist()

##################################################
##################################################
