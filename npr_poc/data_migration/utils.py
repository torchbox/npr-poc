from urllib.parse import urlparse


def is_valid_url(source):
    result = urlparse(source)
    return all([result.scheme, result.netloc, result.path])


class LineBreakWriter:

    def __init__(self, out):
        self.out = out

    def write(self, text):
        text += '\n'
        self.out.write(text)
