import sys

frame = sys._getframe()
print(frame.f_code.co_filename)
