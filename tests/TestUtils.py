# from ../rec2sqlite import Transformer
from .context import rec2sqlite
import os
import subprocess

class TestUtils:
    def write_file(self, file_name, content):
        f = open(file_name, "w", encoding="utf-8")
        f.write(content)
        f.close()

    def test(self, test_id):
        print("Running test " + test_id)
        in_fname = 'test-data/{}.in.txt'.format(test_id)
        exp_out_fname = 'test-data/{}.exp_out.txt'.format(test_id)
        act_out_fname = 'test-data/{}.act_out.txt'.format(test_id)
        in_file = open(in_fname, 'r')
        in_lines = in_file.readlines()  
        sut = rec2sqlite.Transformer()
        for cur_line in in_lines:
            sut.process_line(cur_line)
        in_file.close()
        act_sql = sut.get_sql()
        self.write_file(act_out_fname, act_sql)
        comp_res = subprocess.getoutput("cmp --silent test-data/{}.exp_out.txt test-data/{}.act_out.txt && echo 'Identical' || echo 'Different'".format(test_id, test_id))
        return comp_res
