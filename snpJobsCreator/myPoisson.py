import math

""" p=F(x|k)=pow(e,-k)sum<0, floor(x)> pow(k, i)/fact(i)  """
def cdf(x, k):
    sum = 0.0
    for i in range(int(x)+1):
        sum += float(k**i)/math.factorial(i)
    c = math.exp(-k)
    return c*sum
    
