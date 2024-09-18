import fileinput
import sys
from .Transformer import Transformer

# Main program
transformer = Transformer()
for cur_line in fileinput.input():
    transformer.process_line(cur_line)
print(transformer.get_sql())
