from inkml2img import inkml2img
import os

out_dir = os.path.join(os.getcwd(), "test")
source = os.path.join(os.getcwd(), "equation.inkml")

inkml2img(source, out_dir, "1.png")
