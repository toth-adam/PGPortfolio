import numpy as np
from scipy.optimize import root

temp_var_v = np.random.rand(12)
omega_v = temp_var_v / np.sum(temp_var_v)
print(omega_v)

temp_var = np.random.rand(12)
omega = temp_var / np.sum(temp_var)
print(omega)

c_rate = 0.003

def calculate_pv_after_commission(w1, w0, commission_rate):

    iter_num = 0

    mu0 = 1
    mu1 = 1 - 2*commission_rate + commission_rate ** 2
    while abs(mu1-mu0) > 1e-10:

        iter_num += 1

        mu0 = mu1
        mu1 = (1 - commission_rate * w0[0] -
            (2 * commission_rate - commission_rate ** 2) *
            np.sum(np.maximum(w0[1:] - mu1*w1[1:], 0))) / \
            (1 - commission_rate * w1[0])
    print("iter_num: ", iter_num)
    return mu1


print(calculate_pv_after_commission(omega, omega_v, c_rate))


w1, w0 = omega, omega_v
spread = np.linspace(0.0001, 0.002, 11)

def calc_mu(mu):
    c_rate = 0.001
    mu = mu[0]

    return (1-c_rate)*w0[0]+np.sum((1-c_rate-spread)**2*(np.maximum(w0[1:] - mu*w1[1:], 0))) - (1-c_rate)*mu*w1[0]-\
    np.sum(np.maximum(mu*w1[1:] - w0[1:], 0))


res = root(calc_mu, np.array([1]), tol=1e-10)
print(res.x[0])