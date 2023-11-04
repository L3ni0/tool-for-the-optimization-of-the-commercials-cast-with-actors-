import numpy as np

class Genetic_algorithm_knapsack:

    def __init__(self,weights,values,max_weight,num_of_items=np.inf) -> None:
        assert len(weights) == len(values)
        self.weights = np.array(weights)
        self.max_weight = max_weight
        self.values = np.array(values)
        self.liczba_bitow = len(weights)
        self.liczba_populacji = 180
        self.prawdopodobienstwo_krzyzowania = 0.8
        self.prawdopodobienstwo_mutacji = 0.1
        self.num_of_items = num_of_items
        self.treshold = 1.1




    def fitness_function(self,x):

        x = np.array(x)
        weight_sum = np.sum(x * self.weights)

        if weight_sum > self.max_weight or np.sum(x) > self.num_of_items: # if value doesn't mach constraint give it as 0

            return 0
        else:

            return np.sum(x * self.values)
        
  
    

    def crossover(self,r1, r2, p_krzyzowania):
        d1, d2 = r1.copy(), r2.copy() # at the starts kids are parents copies

        if np.random.rand() < p_krzyzowania:

            pt = np.random.randint(1, len(r1)-2) # shuffling crosssover
           
            d1 = r1[:pt] + r2[pt:]
            d2 = r2[:pt] + r1[pt:]

        return [d1, d2] 

    def selection(self,populacja, wyniki):

        wybrane = np.random.randint(len(populacja)) # first selection is random

        for i in np.random.randint(0, len(populacja), 2):
            
            if wyniki[i] > wyniki[wybrane]: # comparing
                wybrane = i

        return populacja[wybrane]
    
    

    def mutation(self,bits, p_mutacji):

        for i in range(len(bits)):

            if np.random.rand() < p_mutacji: # check if mutate
                bits[i] = 1 - bits[i] # mutation
        
        return bits
        

    def algorithm(self):

        populacja = [np.random.randint(0, 2, self.liczba_bitow).tolist() for _ in range(self.liczba_populacji)] # population Initialization
        best_bytes, best_results = 0, self.fitness_function(populacja[0])
        gen = 0
        best_gen = 0
        BF_list = []

        for _ in range(1000):

            gen += 1
            # calculating values
            results = [self.fitness_function(c) for c in populacja]
            
            
            # finding best result
            for i in range(self.liczba_populacji):
                if results[i] > best_results:
                    best_bytes, best_results = populacja[i], results[i]
                    best_gen = gen
                    # print(f"w generacji {gen}, najlepsza populacja {populacja[i]} ma wynik {results[i]}")

            BF_list.append(best_results)
            
            # wybieranie rodzicow
            parents = [self.selection(populacja, results) for _ in range(self.liczba_populacji)]
        
            # kolejna generacja
            kids = list()
            for i in range(0, self.liczba_populacji, 2):

                
                r1, r2 = parents[i], parents[i+1]

                for kid in self.crossover(r1, r2, self.prawdopodobienstwo_krzyzowania):
                    kid = self.mutation(kid, self.prawdopodobienstwo_mutacji)
                    kids.append(kid) # zapisanie dziecka

            populacja = kids # podmiana populacji
            # print(gen)
            # if gen == 1 or best_results == 0:
            #     continue

            # running_mean = ((1/gen)*np.sum([(BFi - best_results)**2 for BFi in BF_list]))
            # print(running_mean)
            # if running_mean<self.treshold:
            #     break

        return [best_bytes, best_results]
    

# g1 = Genetic_algorithm_knapsack([1,2,3,4,6,3,1,6,1,5,8,3,12,1,7,32,7],[7,6,5,4,4,6,2,3,52,4,2,3,4,11,5,8,3],12,2)
# naj_bity,naj_wynik = g1.algorithm()
# print(f'najlepszy wynik ma populacja {naj_bity} ma wynik {naj_wynik}')