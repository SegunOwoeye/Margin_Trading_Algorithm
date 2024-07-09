from os import getcwd, path, mkdir

def create_program_folder(trading_pair, i_path):
    try:
        current_directory = getcwd() #Gets path for the program
        directory = trading_pair # Folder Name
        new_folder = path.join(current_directory,i_path) #Ipath is the intemediate path from the current directory to the created folder
        new_folder = path.join(new_folder,directory)
        mkdir(new_folder)

    except FileExistsError as error:
        pass

def create_data_folder(trading_pair, i_path, tag):
    try:
        current_directory = getcwd() #Gets path for the program
        directory = trading_pair+tag # Folder Name
        new_folder = path.join(current_directory,i_path) #Ipath is the intemediate path from the current directory to the created folder
        new_folder = path.join(new_folder,directory)
        mkdir(new_folder)

    except FileExistsError as error:
        pass

def create_Subfolder_folder(trading_pair, i_path, sub_name, main_tag):
    try:
        current_directory = getcwd() #Gets path for the program
        subfolder =  trading_pair+main_tag
        directory =  str(sub_name) # Folder Name
        new_folder = path.join(current_directory,i_path)
        new_folder = path.join(new_folder,subfolder)
        new_folder = path.join(new_folder,directory)
        mkdir(new_folder)

    except FileExistsError as error:
        pass







#RUN PROGRAM 
#create_program_folder("BTCUSDT", "1-DataGathering\Programs")
#create_data_folder("BTCUSDT", "1-DataGathering\data_gathered")
#create_Subfolder_folder("BTCUSDT", "1-DataGathering\data_gathered", "Historical_Klines", "_data")
#create_Subfolder_folder("BTCUSDT", "1-DataGathering\data_gathered", "Live_Data", "_data")