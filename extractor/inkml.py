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
                coords.append((x, y))
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

    width_points = (min(x_mins),  max(x_maxs))
    height_points = (min(y_mins), max(y_maxs))
    width = width_points[1]-width_points[0]
    height = height_points[1]-height_points[0]
    x_min = min(x_mins)
    return width_points, height_points, width, height


def shift_trace_group(trace_grp, x_min, y_min):
    shifted_traces = []
    for trace in trace_grp['traces']:
        shifted_traces.append(np.subtract(trace, [x_min, y_min]))
    return {'label': trace_grp['label'], 'traces': shifted_traces}
