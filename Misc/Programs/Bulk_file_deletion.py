import os
from time import sleep



def mass_del(extension_type, search="ALL"):
    # Get the current directory
    wd_path = os.getcwd()

    print(wd_path)
    if search.upper() == "ALL":
        folders = [wd_path] + next(os.walk('.'))[1] + [x[0] for x in os.walk(wd_path)] 
    if search.upper() == "SUB":
        folders = next(os.walk('.'))[1]
    if search.upper() == "REC SUB":
        folders = [x[0] for x in os.walk(wd_path)] 

    
    filename_list = []
    for i in range(len(folders)):
        filenames = next(os.walk(folders[i]), (None, None, []))[2] 
        for p in range(len(filenames)):
            if filenames[p].endswith(extension_type):
                complete_filename = f"{folders[i]}/{filenames[p]}"
                print(complete_filename)
                sleep(2)





# RUN

mass_del(".pyc")