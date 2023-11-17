import numpy as np

class Genetic_algorithm_knapsack:

    def __init__(self,weights,values,max_weight,max_num_of_items=np.inf,min_num_of_items=1, /
                 num_of_population=10,p_crossing=0.8, p_mutation=0.1, treshold=0.5, starting_point=10) -> None:

        assert len(weights) == len(values), 'weights and values number is different'
        assert min(weights) <= max_weight, "solution doesn't exist"
        assert max_num_of_items < min_num_of_items, 'max num of items is lower than min num of items'

        self.weights = np.array(weights)
        self.max_weight = max_weight
        self.values = np.array(values)
        self.liczba_bitow = len(weights)
        self.num_of_population = num_of_population
        self.p_crossing = p_crossing
        self.p_mutation = p_mutation
        self.max_num_of_items = max_num_of_items
        self.min_num_of_items = min_num_of_items
        self.treshold = treshold
        self.starting_point = starting_point




    def fitness_function(self,bits):

        bits = np.array(bits)
        weight_sum = np.sum(bits * self.weights)

        if weight_sum > self.max_weight or np.sum(bits) > self.max_num_of_items or np.sum(bits) < self.min_num_of_items: # if value doesn't mach constraint give it as 0

            return 0
        else:

            return np.sum(bits * self.values)
        
  
    

    def crossover(self,r1, r2):
        d1, d2 = r1.copy(), r2.copy() # at the starts kids are parents copies

        if np.random.rand() < self.p_crossing:

            pt = np.random.randint(1, len(r1)-2) # shuffling crosssover
           
            d1 = r1[:pt] + r2[pt:]
            d2 = r2[:pt] + r1[pt:]

        return [d1, d2] 

    def selection(self,population, results):

        choosed = np.random.randint(len(population)) # first selection is random

        for i in np.random.randint(0, len(population), 2):
            
            if results[i] > results[choosed]: # comparing
                choosed = i

        return population[choosed]
    
    

    def mutation(self,bits):

        for i in range(len(bits)):

            if np.random.rand() < self.p_mutation: # check if mutate
                bits[i] = 1 - bits[i] # mutation
        
        return bits
    
    def repair_function(self,bits):

        if np.sum(bits) < self.min_num_of_items:

            choosed_bits = [np.random.randint(0, len(bits)) for _ in range(self.max_num_of_items)]

            for i in choosed_bits:
                bits[i] = 1

        elif np.sum(bits) >  self.max_num_of_items:

            while np.sum(bits) >  self.max_num_of_items:

                choosed_bits = [i for i,b in enumerate(bits) if b == 1]
                choosed_bit = np.random.choice(choosed_bits)
                bits[choosed_bit] = 0

        
        while self.fitness_function(bits) == 0:

            dic_choosed_prices = {i:self.weights[i] for i,b in enumerate(bits) if b == 1}
            most_wage = max(dic_choosed_prices, key=dic_choosed_prices.get)

            cheaper_bits = [i for i,b in enumerate(bits) if self.weights[most_wage] > self.weights[i]]

            replacing_bit = np.random.choice(cheaper_bits)

            bits[most_wage] = 0
            bits[replacing_bit] =  1
        
        return bits
                



            
        

    def algorithm(self):

        population = [np.random.randint(0, 2, self.liczba_bitow).tolist() for _ in range(self.num_of_population)] # population Initialization
        best_bytes, best_results = 0, self.fitness_function(population[0])
        gen = 0
        best_gen = 0
        BF_list = []

        while True:

            gen += 1


            # reparir bits
            population = [self.repair_function(c) for c in population]

            # calculating values
            results = [self.fitness_function(c) for c in population]
            print(results)

           
            
            
            
            # finding best result
            for i in range(self.num_of_population):
                if results[i] > best_results:
                    best_bytes, best_results = population[i], results[i]
                    best_gen = gen
                    # print(f"w generacji {gen}, najlepsza populacja {populacja[i]} ma wynik {results[i]}")

            BF_list.append(best_results)
            
            # wybieranie rodzicow
            parents = [self.selection(population, results) for _ in range(self.num_of_population)]
        
            # kolejna generacja
            kids = list()
            for i in range(0, self.num_of_population, 2):

                
                r1, r2 = parents[i], parents[i+1]

                for kid in self.crossover(r1, r2):
                    kid = self.mutation(kid)
                    kids.append(kid) # zapisanie dziecka

            population = kids # podmiana populacji

            if gen <= self.starting_point:
                continue

            running_mean = ((1/(gen - self.starting_point))*np.sum([(BFi - best_results)**2 for BFi in BF_list]))
            print(running_mean)
            if running_mean<self.treshold:
                break

        return [best_bytes, best_results]
    

g1 = Genetic_algorithm_knapsack([1,2,3,4,6,3,1,6,1,5,8,3,12,1,7,32,7],[7,6,5,4,4,6,2,3,52,4,2,3,4,11,5,8,3],12,max_num_of_items=2)
naj_bity,naj_wynik = g1.algorithm()
print(f'najlepszy wynik ma populacja {naj_bity} ma wynik {naj_wynik}')