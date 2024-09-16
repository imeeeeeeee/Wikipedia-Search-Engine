this_file='pagerank.py'
print(this_file,': loading imports.')
import pickle
import numpy as np

def multiply_transpose_with_vector(C, L, I, V):
    n = len(V)
    P = np.zeros(n)

    for i in range(n-1):  # Stop loop one index earlier
        if L[i] != L[i+1]:
            for k in range(L[i], L[i+1]):
                j = I[k]
                P[j] += C[k] * V[i]
        else:
            for j in range(n):
                P[j] += (1/n) * V[i]

    if L[-1] != len(C):  # Handle last row separately
        for k in range(L[-1], len(C)):
            j = I[k]
            P[j] += C[k] * V[-1]
    else:
        for j in range(n):
            P[j] += (1/n) * V[-1]

    return P

def pagerank(C, L, I, n, epsilon=1/4, max_iter=100, tol=1e-6):
    Pi = np.ones(n) / n  # Initialize PageRank vector Pi uniformly
    one_over_n = np.ones(n) / n  # Vector for the teleportation effect, uniformly distributed

    DEBUG_COUNTER = 0

    for _ in range(max_iter):  
        new_Pi = multiply_transpose_with_vector(C, L, I, Pi)  # Update Pi using modified function

        DEBUG_COUNTER+=1
        if DEBUG_COUNTER%(max_iter//5)==0:
            print(this_file,':',(100*DEBUG_COUNTER/max_iter),'% done...')
        
        # Apply damping factor epsilon and add teleportation effect
        Pi = (1 - epsilon) * new_Pi + epsilon * one_over_n

    return Pi

# I = [1/2, 1/2, 1, 1/3, 1/3, 1/3] 
# L = [0, 2, 3, 3, 6]  
# C = [1, 3, 0, 0, 1, 2]  
# res = pagerank(C, L, I, 4)  
# print(res) 

if __name__ == "__main__":
    C,L,I = None,None,None
    
    print(this_file,': loading relevant files.')

    with open('C_matrix.pkl','rb') as file:
        C = pickle.load(file)
    with open('L_matrix.pkl','rb') as file:
        L = pickle.load(file)
    with open('I_matrix.pkl','rb') as file:
        I = pickle.load(file)

    print(this_file,': starting pagerank.')
    
    res = pagerank(C,L,I,1010)

    print(this_file,' : PageRank sum = ',sum(res),'. Saving result.', sep='')

    with open('pagerank.pkl', 'wb') as outfile:
        pickle.dump(res, outfile)