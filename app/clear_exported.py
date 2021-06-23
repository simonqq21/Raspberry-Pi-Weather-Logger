from config import APP_DATA_PATH, EXPORTEDS_FOLDER
import os 

files = os.listdir(APP_DATA_PATH + EXPORTEDS_FOLDER)
print(files)
for file in files:
	os.remove(APP_DATA_PATH + EXPORTEDS_FOLDER + file)
	print(f"deleted {file}")
print("done")
