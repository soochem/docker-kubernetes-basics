import logging
import sys
from contextlib import redirect_stdout

stdout_logger = logging.getLogger()
stdout_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
stdout_logger.addHandler(handler)

stdout_logger.write = lambda msg: stdout_logger.info(msg) if msg != '\n' else None

with redirect_stdout(stdout_logger):
    print("TEST")

print("TEST2")
# class StreamToLogger(object):
#     """
#     Fake file-like stream object that redirects writes to a logger instance.
#     """
#
#     def __init__(self, logger, log_level=logging.INFO):
#         self.logger = logger
#         self.log_level = log_level
#         self.linebuf = ''
#
#     def write(self, buf):
#         for line in buf.rstrip().splitlines():
#             self.logger.log(self.log_level, line.rstrip())
#
#
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
#     filename="out.log",
#     filemode='a'
# )
#
# stdout_logger = logging.getLogger('STDOUT')
# sl = StreamToLogger(stdout_logger, logging.INFO)
# sys.stdout = sl
#
# # stderr_logger = logging.getLogger('STDERR')
# # sl = StreamToLogger(stderr_logger, logging.ERROR)
# # sys.stderr = sl
#
# print("Test to standard out")
# raise Exception('Test to standard error')
