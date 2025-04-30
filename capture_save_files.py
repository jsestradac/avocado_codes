# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 17:23:26 2024

@author: sebas
"""
import requests 
import os
from time import sleep
from natsort import natsorted

def save_img(name,last_directory,image_directory,
             img_save_path, camera):
    
    img_name = camera + '/files/' + last_directory + '/' + image_directory+'/' + name                          
    file = requests.get(img_name,
                       stream = True)
    file_directory = img_save_path  + last_directory + '/' + image_directory
    
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)
        
    file_path = file_directory +'/' + name
    
    if os.path.isfile(file_path):
        return 0

    with open(file_path, 'wb') as f:
        for chunk in file.iter_content(1024):
            f.write(chunk)
    return 0



camera = r"http://192.168.10.254/"
path = r"C:/Users/sebas/Documents/Micasense_experiments/"
#%%

def main():

    for i in range(10):
    
        capture_params = { 'store_capture' : True, 'block' : True }
        capture_data = requests.post("http://192.168.10.254/capture", json=capture_params)
        
        capture_data = capture_data.json()
        
        status = capture_data['status']
        id_1 = capture_data['id']
        while status != 'complete':
            
            new_message = camera + '/capture/' + id_1
            
            r = requests.get(new_message)
            status = r.json['id']
            print(status)
            sleep(0.01)
            
            
            
        
        print(i)
        
    sleep(3)
    
    #status = requests.get("https://192.168.137.127/files")
    
    #%%
    read_files_command = camera + '/files'
    
    files = requests.get(read_files_command)
    
    print(files.json())
    #%%
    
    files_json = files.json()    
    directories = files_json['directories']
    directories = natsorted(directories)
    print(directories)
    last_directory = directories[-2]
    print(last_directory)
    
    #%%
    read_last_directory = camera + '/files/' + last_directory
    message = requests.get(read_last_directory)
    message_json = message.json()
    name_params = message_json['files']
    image_directory = message_json['directories'][0]
    print(image_directory)
    
    #%%
    images_msg = camera + '/files/' + last_directory + '/' + image_directory
    images_from_camera = requests.get(images_msg)
    
    print (images_msg)
    print(images_from_camera.json())
    images_json = images_from_camera.json()
    
    files = images_json['files']
    
    for file in files:
        file_name = file['name']
        save_img(file_name,last_directory,image_directory,path,camera)
        
if __name__ == '__main__':
    main()

    
    
    








    
    
    







