from os import walk, remove

class bulk_delete:
    # Initialising variables
    def __init__(self, dir_list: list, extension: list):
        self.dir_list = dir_list
        self.extension = extension


    def gathering_subfolders(self):
        folder_list = []
        for i in range(len(self.dir_list)):
            folders = [x[0] for x in walk(self.dir_list[i])] 
            folder_list.append(folders)

        return folder_list


    def gathering_filenames(self):
        folders_list = self.gathering_subfolders()
        filename_list = []
        for a in range(len(folders_list)): # Dir folder
            subfolders = folders_list[a]
            for b in range(len(subfolders)): # Subfolder
                filenames = next(walk(subfolders[b]), (None, None, []))[2] 
                for c in range(len(filenames)): # Filenames
                    for d in range(len(self.extension)):
                        if filenames[c].endswith(self.extension[d]):
                            complete_filename = f"{subfolders[b]}/{filenames[c]}"
                            filename_list.append(complete_filename)

        return filename_list
                        

    def delete_files(self):
        files_to_delete = self.gathering_filenames()
        if len(files_to_delete) == 0: # List is empty
            pass
        else:
            for i in range(len(files_to_delete)):
                remove(files_to_delete[i])



def run(dir_list: list, extension: list):
    main = bulk_delete(dir_list, extension)
    main.delete_files()




dir_list = ["1-DataGathering/", "2-DataProcessing/"]
extension = [".db", ".txt"]
# RUN
run(dir_list, extension)
