from inkml2img import inkml2img
import os

current_dir = os.getcwd()
val_path = os.path.join(
    current_dir, "WebData_CROHME23/WebData_CROHME23/val/INKML/CROHME2016_test")
train_path = os.path.join(
    current_dir, "WebData_CROHME23/WebData_CROHME23/train/INKML/CROHME2019_train")

print(len(os.listdir(val_path)))
print(len(os.listdir(train_path)))

out_val_path = os.path.join(current_dir, 'val')
out_train_path = os.path.join(current_dir, 'train')


def dir_inkml2img(input_dir, output_dir):
    for i, filename in enumerate(os.listdir(input_dir)):
        file_abs = os.path.join(input_dir, filename)
        try:
            inkml2img(file_abs, output_dir, f'{i}.png')
        except:
            continue

dir_inkml2img(train_path, out_train_path)
