from inkml import extract_trace_grps
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


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


path = os.path.join(os.getcwd(), "equation.inkml")
trace_grps = extract_trace_grps(path)
for trace_grp in trace_grps:
    ls = trace_grp['traces']
    for subls in ls:
        data = np.array(subls)
        x, y = zip(*data)
        plt.plot(x, y, color='black')
    plt.gca().invert_yaxis()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().get_xaxis().set_visible(False)
    plt.gca().get_yaxis().set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    #plt.savefig(f"{trace_grp['label']}.png", dpi=100)
    plt.show()
