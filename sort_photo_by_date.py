import exifread
import pyheif
import io
import typing
import glob
import subprocess

SOURCE_DIR = "./source/*"
DEST_DIR = "./dest/"
DATE_TAKEN_TAG = 'EXIF DateTimeOriginal'

def get_photo_taken_date(input_stream: typing.BinaryIO) -> str:
    tags = exifread.process_file(input_stream)
    dateTaken = tags.get(DATE_TAKEN_TAG)
    if dateTaken is None:
        dateTaken = tags.get("Image DateTime")
    if dateTaken is None:
        if tags is None:
            return None
        for k in tags:
            print (f"key = {k} ")
            return None

    return str(dateTaken)
  

def getfile(file_name):
    with open(file_name, 'rb') as fh:
      return get_photo_taken_date(fh)

def getfile_heic(file_name):
  heif_file = pyheif.read(file_name)
  exif_data =  heif_file.metadata[0].get("data")
  mem_bytes_io = io.BytesIO(exif_data[6:])
  return get_photo_taken_date(mem_bytes_io)

def main():
    
    file_list = glob.glob(SOURCE_DIR)
    #print(SOURCE_DIR)
    #print(file_list)
    for file_name in file_list:
        date_extracted = None
        try:
            if file_name[-3:].upper() == "JPG":
                date_extracted = getfile(file_name)
            elif file_name[-4:] == "HEIC":
                date_extracted = getfile_heic(file_name)
            if date_extracted is None:
                continue
        except Exception as e:
            print(f"not able to find taken time {file_name} becase of {e}")
            continue
        
        year = date_extracted[0:4]
        month = date_extracted[5:7]
        #day = date_extracted[8:10]
        dest_filename = f"{DEST_DIR}/{year}/{month}"
        print(f"{file_name} should go to {dest_filename}")
        subprocess.run(["rsync","-tuv","--remove-source-files", file_name, dest_filename])

if __name__ == "__main__":
    main()

