from PIL import Image
import os


def get_files(path):
    files = []
    for file in os.listdir(path):
        file_name = os.path.join(path, file)
        file_name = Image.open(file_name)
        files.append(file_name)
    print("finish appending")
    return files


def generate_gif(frames, name):
    frames[0].save(name+'.gif', format='GIF',
                   append_images=frames[1:], save_all=True, duration=1)


list = get_files("record")
generate_gif(list, "q")
