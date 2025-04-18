import os
import glob

# Path to the folder where notification .txt files are stored
folder_path = "/data/data/com.termux/files/home/Job-Scraper-*/src/scripts/daily-notif-cmds"

# Loop through all .txt files in the folder
for txt_file in glob.glob(os.path.join(folder_path, "*.txt")):
    try:
        with open(txt_file, "r") as file:
            command = file.read().strip()

        os.system(command)
        os.remove(txt_file)
    except:
        continue