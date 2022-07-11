import sys

import qoi
import y4m


class qoiv:

    def __init__(self, stream):
        self.y4m_inst = y4m.Reader(self.read_frame, verbose=True)
        self.stream = stream
        self.start()

    def read_frame(self, frame: y4m.Frame):
        print(frame.headers)

    def start(self):
        print("[qoipv] Started.")
        while True:
            data = self.stream.read(1024)
            if not data:
                print("Data stopped flowing. Breaking.")
            self.y4m_inst.decode(data)


if __name__ == '__main__':
    qoiv(sys.stdin)
