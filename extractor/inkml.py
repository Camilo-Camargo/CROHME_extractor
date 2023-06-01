import xml.etree.ElementTree as ET
import numpy as np
import cv2


def extract_trace_grps(inkml_file):
    trace_grps = []

    tree = ET.parse(inkml_file)
    root = tree.getroot()
    doc_namespace = "{http://www.w3.org/2003/InkML}"

    # Find traceGroup wrapper - traceGroup wrapping important traceGroups
    traceGrpWrapper = root.findall(doc_namespace + 'traceGroup')[0]
    traceGroups = traceGrpWrapper.findall(doc_namespace + 'traceGroup')
    for traceGrp in traceGroups:
        latex_class = traceGrp.findall(doc_namespace + 'annotation')[0].text
        traceViews = traceGrp.findall(doc_namespace + 'traceView')
        # Get traceid of traces that refer to latex_class extracted above
        id_traces = [traceView.get('traceDataRef') for traceView in traceViews]
        # Construct pattern object
        trace_grp = {'label': latex_class, 'traces': []}

        # Find traces with referenced by latex_class
        traces = [trace for trace in root.findall(
            doc_namespace + 'trace') if trace.get('id') in id_traces]
        # Extract trace coords
        for idx, trace in enumerate(traces):
            coords = []
            for coord in trace.text.replace('\n', '').split(','):
                # Remove empty strings from coord list (e.g. ['', '-238', '-91'] -> [-238', '-91'])
                coord = list(filter(None, coord.split(' ')))
                # Unpack coordinates
                x, y = coord[:2]
                # print('{}, {}'.format(x, y))
                if not float(x).is_integer():
                    # ! Get rid of decimal places (e.g. '13.5662' -> '135662')
                    # x = float(x) * (10 ** len(x.split('.')[-1]) + 1)
                    x = float(x) * 10000
                else:
                    x = float(x)
                if not float(y).is_integer():
                    # ! Get rid of decimal places (e.g. '13.5662' -> '135662')
                    # y = float(y) * (10 ** len(y.split('.')[-1]) + 1)
                    y = float(y) * 10000
                else:
                    y = float(y)

                # Cast x & y coords to integer
                x, y = round(x), round(y)
                coords.append([x, y])
            trace_grp['traces'].append(coords)
        trace_grps.append(trace_grp)

        # print('Pattern: {};'.format(pattern))
    return trace_grps


def get_tracegrp_properties(trace_group):
    x_mins, y_mins, x_maxs, y_maxs = [], [], [], []
    for trace in trace_group['traces']:

        x_min, y_min = np.amin(trace, axis=0)
        x_max, y_max = np.amax(trace, axis=0)
        x_mins.append(x_min)
        x_maxs.append(x_max)
        y_mins.append(y_min)
        y_maxs.append(y_max)
    # print('X_min: {}; Y_min: {}; X_max: {}; Y_max: {}'.format(min(x_mins), min(y_mins), max(x_maxs), max(y_maxs)))
    return min(x_mins), min(y_mins), max(x_maxs) - min(x_mins), max(y_maxs) - min(y_mins)


def shift_trace_group(trace_grp, x_min, y_min):
    shifted_traces = []
    for trace in trace_grp['traces']:
        shifted_traces.append(np.subtract(trace, [x_min, y_min]))
    return {'label': trace_grp['label'], 'traces': shifted_traces}


def get_scale(width, height, box_size):
    ratio = width / height
    if ratio < 1.0:
        return box_size / height
    else:
        return box_size / width


def rescale_trace_group(trace_grp, width, height, box_size):
    # Get scale - we will use this scale to interpolate trace_group so that it fits into (box_size X box_size) square box.
    scale = get_scale(width, height, box_size)
    rescaled_traces = []
    for trace in trace_grp['traces']:
        # Interpolate contour and round coordinate values to int type
        rescaled_trace = np.around(np.asarray(
            trace) * scale).astype(dtype=np.uint8)
        rescaled_traces.append(rescaled_trace)

    return {'label': trace_grp['label'], 'traces': rescaled_traces}


def draw_trace(trace_grp, box_size, thickness):
    placeholder = np.ones(shape=(box_size, box_size), dtype=np.uint8) * 255
    for trace in trace_grp['traces']:
        for coord_idx in range(1, len(trace)):
            cv2.line(placeholder, tuple(
                trace[coord_idx - 1]), tuple(trace[coord_idx]), color=(0), thickness=thickness)
    return placeholder


def convert_to_img(trace_group, box_size, thickness):
    # Calculate Thickness Padding
    thickness_pad = (thickness - 1) // 2
    # Convert traces to np.array
    trace_group['traces'] = np.asarray(trace_group['traces'])
    # Get properies of a trace group
    x, y, width, height = get_tracegrp_properties(trace_group)

    # 1. Shift trace_group
    trace_group = shift_trace_group(trace_group, x_min=x, y_min=y)
    x, y, width, height = get_tracegrp_properties(trace_group)
    # 2. Rescale trace_group
    trace_group = rescale_trace_group(
        trace_group, width, height, box_size=box_size-thickness_pad*2)
    x, y, width_r, height_r = get_tracegrp_properties(trace_group)
    # Shift trace_group by thickness padding
    trace_group = shift_trace_group(
        trace_group, x_min=-thickness_pad, y_min=-thickness_pad)
    # Center inside square box (box_size X box_size)
    margin_x = (box_size - (width_r + thickness_pad*2)) // 2
    margin_y = (box_size - (height_r + thickness_pad*2)) // 2
    trace_group = shift_trace_group(
        trace_group, x_min=-margin_x, y_min=-margin_y)
    image = draw_trace(trace_group, box_size, thickness=thickness)
    # Get pattern's width & height
    pat_width, pat_height = width_r + thickness_pad*2, height_r + thickness_pad*2

    # ! TESTS
    # cv2.imshow('image', image)
    # cv2.waitKey(0)
    if width < box_size and height < box_size:
        raise Exception('Trace group is too small.')
    if x != 0 or y != 0:
        raise Exception('Trace group was inproperly shifted.')
    if pat_width == 0 or pat_height == 0:
        raise Exception('Some sides are 0 length.')
    if pat_width < box_size and pat_height < box_size:
        raise Exception('Both sides are < box_size.')
    if pat_width > box_size or pat_height > box_size:
        raise Exception('Some sides are > box_size.')
    return image
