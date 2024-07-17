from time import sleep
import os 


# [1] Gets the name of the files in the database
def get_filenames(path):
    file_list = []
    for i in range(len(path)):
        files = os.listdir(path[i])
        file_list.append(files)
    return file_list

# [2] Determines if a file is empty and needs to be deleted
def get_files_to_delete(path):
    files = get_filenames(path)
    to_delete = []
    for n in range(len(path)):
        no_of_files = len(files[n]) # Gets the number of files that exists in the folder
        for i in range(no_of_files):
            complete_filenames = f"{path[n]}/{files[n][i]}"
            #print(complete_filenames)
            if os.path.exists(complete_filenames) == True:
                # Adds the filename to a list of files to delete if it's empty
                if os.stat(complete_filenames).st_size == 0: 
                    to_delete.append(complete_filenames)
                else:
                    pass
            else:
                pass
    return to_delete

# [3] Deletes the files
def delete_files(path):
    files_to_delete = get_files_to_delete(path)
    if len(files_to_delete) == 0: # Checks to see if the list is empty, If it is it means there's no files to delete
        #print("Skip")
        sleep(10)

    else:  
    
        try: 
            # Deletes the files that are blank
            for i in range(len(files_to_delete)):
                os.remove(files_to_delete[i])
                #print(f"Deleted: {files_to_delete[i]}")
        except:
            pass
    

# [4] Runs the Program

def run(path):
    sleep(10)
    while 1:
        try:
            delete_files(path)
        except:
            sleep(10) # Checks if files need to be deleted every 1 seconds
            pass

""" TESTING """

#path = ["1-DataGathering/data_gathered/BTCUSDT_data/Live_Data", "1-DataGathering/data_gathered/BTCUSDT_data/Historical_Klines"]

#print(get_files_to_delete(path)) 

#run(path)

"""trading_pairs = ["BTCUSDT"] #, "ETHUSDT"]

path_list = []
for i in range(len(trading_pairs)):
    file_path = f"2-DataProcessing/data_gathered/{trading_pairs[i]}_data"
    
    path_list.append(file_path)




(run(path_list))"""