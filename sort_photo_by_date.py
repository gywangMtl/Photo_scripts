import exifread
import pyheif
import io
import typing
import glob
import subprocess
import os
from time import gmtime, strftime
import xml.etree.ElementTree as ET

SOURCE_DIR = "./source/*"
DEST_DIR = "./dest/"

DATE_TAKEN_TAG = 'EXIF DateTimeOriginal'

def get_photo_taken_date(input_stream: typing.BinaryIO) -> str:
    tags = exifread.process_file(input_stream)
    dateTaken = tags.get(DATE_TAKEN_TAG)
    if dateTaken is None:
        dateTaken = tags.get("Image DateTime")
    if dateTaken is None:
        return None

    return str(dateTaken)
  

def getfile(file_name: str) -> str:
    with open(file_name, 'rb') as fh:
      return get_photo_taken_date(fh)

def getfile_heic(file_name: str) -> str:
  heif_file = pyheif.read(file_name)
  exif_data =  heif_file.metadata[0].get("data")
  mem_bytes_io = io.BytesIO(exif_data[6:])
  return get_photo_taken_date(mem_bytes_io)


def get_from_modified_time(file_name: str) -> str:
    take_date = gmtime(os.path.getmtime(file_name))
    return strftime("%Y-%m-%d", take_date)

def get_from_xmp(file_name: str) -> str:
    ns = "http://ns.adobe.com/photoshop/1.0/"
    root = ET.parse(file_name)
    date_created = root.findall('.//{'+ns+'}DateCreated')
    return date_created[0].text
    
    

def main():
    
    file_list = glob.glob(SOURCE_DIR)
    for file_name in file_list:
        if os.path.isdir(file_name):
            continue
        date_extracted = None
        try:
            if file_name[-3:].upper() == "JPG":
                date_extracted = getfile(file_name)
            elif file_name[-4:] == "HEIC":
                date_extracted = getfile_heic(file_name)
            elif file_name[-3:] == "xmp":
                date_extracted = get_from_xmp(file_name)
            if (date_extracted is None) or (date_extracted[0:4] < "1900"):
                date_extracted = get_from_modified_time(file_name)
        except Exception as e:
            print(f"not able to find taken time {file_name} becase of {e}")
            continue
        
        year = date_extracted[0:4]
        month = date_extracted[5:7]
        dest_filename = f"{DEST_DIR}/{year}/{month}"
        print(f"{file_name} should go to {dest_filename}")
        #subprocess.run(["rsync","-tuv","--remove-source-files", file_name, dest_filename])

if __name__ == "__main__":
    main()

