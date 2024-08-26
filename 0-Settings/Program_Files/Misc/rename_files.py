import os


def file_mame_change(path, exclusion_criteria):
    file_list = []
    for filename in os.listdir(path):
        file_list.append(filename)
    

    #Loops through list and removes excluded file names from name change
    exclusion_list = []
    for i in range(len(file_list)):
        for n in range(len(exclusion_criteria)):
            if exclusion_criteria[n] in file_list[i]:
                exclusion_list.append(file_list[i])

            else:
                pass
    
    print(file_list)
    for o in range(len(exclusion_list)):
        file_list.remove(exclusion_list[o])
    
    
        

    print(file_list)

exclusion_criteria_list = ["1m", "5m", "15m", "1h", "4h", "1d"] # Time

file_mame_change("2-DataProcessing\Programs\BTCUSDT", exclusion_criteria_list)