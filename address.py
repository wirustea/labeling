import os
import sys
import json
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
print('cwd:'+cwd,';','basedir:'+basedir)

# image_folder_path = os.path.join(basedir,'images')
image_folder_path = os.path.join(cwd,'images')
json_file_path = os.path.join(cwd, 'result')
sample_folder_path = os.path.join(basedir,'sample')
congif_file_path = os.path.join(cwd,'config.json')

if not os.path.exists(json_file_path):
    os.mkdir(json_file_path)

def get_sample_image(label):
    return os.path.join(sample_folder_path, label + '.jpg')
def get_json_file_path(label):
    return os.path.join(json_file_path, label+'.json')