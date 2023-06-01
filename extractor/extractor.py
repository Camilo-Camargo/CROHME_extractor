from inkml import extract_trace_grps, convert_to_img
import os

path = os.path.join(os.getcwd(), "equation.inkml")
trace_grps = extract_trace_grps(path)
print(trace_grps)

print(trace_grps[0]["traces"])
