import inkml
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw


def draw_trace(trace_grp, box_size, thickness):
    placeholder = np.ones(shape=(box_size, box_size), dtype=np.uint8) * 255
    for trace in trace_grp['traces']:
        for coord_idx in range(1, len(trace)):
            cv2.line(
                placeholder,
                trace[coord_idx - 1],
                trace[coord_idx],
                color=(0),
                thickness=thickness)
    return placeholder


def inkml2img(source, out_dir, filename):
    print(source, out_dir)
    # TODO: Add more sizes and more options...
    trace_grps = inkml.extract_trace_grps(source)
    for trace_grp in trace_grps:
        x_points, y_points, width, height = inkml.get_tracegrp_properties(
            trace_grp)
        trace_grp = inkml.shift_trace_group(
            trace_grp, x_points[0], y_points[0])

        # padding for all borders
        padding = 30
        img = Image.new('L', (width+padding, height+padding), color=255)
        draw = ImageDraw.Draw(img)

        offset = padding // 2
        for traces in trace_grp["traces"]:
            for i in range(1, len(traces)):
                x_0 = traces[i-1][0] + offset
                y_0 = traces[i-1][1] + offset
                x = traces[i][0] + offset
                y = traces[i][1] + offset

                draw.line([(x_0, y_0), (x, y)], width=10)

        width, height = img.size
        aspect_ratio = width / height

        new_width = new_height = 26

        if aspect_ratio > 1:
            new_height = round(new_width / aspect_ratio)
        else:
            new_width = round(new_height * aspect_ratio)

        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        final_img = Image.new('L', (28, 28), color=255)
        final_img.paste(img, ((28-new_width)//2, (28-new_height)//2))
        out_dir_path = f'{out_dir}/{trace_grp["label"]}'

        if not os.path.exists(out_dir_path):
            os.makedirs(out_dir_path)

        out_path = os.path.join(out_dir_path, filename)
        final_img.save(out_path)
