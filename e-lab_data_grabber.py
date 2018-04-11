import urllib
import sys

if len(sys.argv) < 2:
    sys.exit("Error: Data type not specified")

elif sys.argv[1].lower() == "flux":
    save_location = "raw_data/flux/"

elif sys.argv[1].lower() == "raw":
    save_location = "raw_data/raw/"

elif sys.argv[1].lower() == "blessing":
    save_location = "raw_data/blessing/"

else:
    sys.exit("Error: Unrecognized data type")

url = raw_input("Enter url: ")
file_name = raw_input("Enter file name: ")

data = urllib.urlretrieve(url, save_location + file_name)
