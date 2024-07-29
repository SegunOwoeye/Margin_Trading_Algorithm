# Program conducts a regression analysis to produce the best line of best fit depending on the degree of the polynomial

# IMPORTS
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


class Regression_Analysis:
    # Initialising Variables
    def __init__(self, dataset, degree):
        self.dataset = dataset
        self.degree = degree


    # Linear Regression Analysis
    def linear_function(self, x, m, c):
        return m*x + c
    
    # WIP
    def linear_analysis(self):
        data_list = self.dataset
        r2_list = []
        try:
            for p in range(len(data_list)):
                data = data_list[p:]
                #data = data_list
                x =  np.linspace(1, len(data), num=len(data))
                plt.plot(x, data, 'b-', label='data')
                popt, pcov = curve_fit(self.linear_function, x, data)
                #print(popt)
                
                actual_y = data
                predictive_y = []
                for i in range(len(data)):
                    y = self.linear_function(x[i], popt[0], popt[1])
                    predictive_y.append(y)

                r2 = round(r2_score(actual_y, predictive_y),4)

                plt.plot(x, self.linear_function(x, *popt), 'r-', label='fit: m=%5.3f, c=%5.3f' % tuple(popt)+ f" R2: {r2}")

                plt.xlabel('x')
                plt.ylabel('y')
                plt.legend()
                #plt.show()
                r2_list.append(r2)

        except:
            pass

        print(r2_list)

        

        
        
        


""" TESTING """

# Variables
dataset = [63700, 63994.01, 64116, 64414, 65135.9, 65747.04, 65836.77, 66419.43, 66755.42, 66787.99, 67157.26, 66931.8, 66892.28, 66721.19, 66660,
           66419.88, 66361.99, 66570.57, 66602.01, 66660.84, 66537.32, 
           66625.77, 66562.28, 66510.71, 66582.79, 66524.99, 66483.69, 66476.28]
degree = 1


# RUN
main = Regression_Analysis(dataset, degree)
main.linear_analysis()