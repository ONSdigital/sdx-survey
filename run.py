import sys

from app import cloud_config


class OutputFilter:
    """
        Custom filter to stop "Observed recoverable stream error 503"
        message from filling up the logs in GCP.
    """

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr_name):
        return getattr(self.stream, attr_name)

    def write(self, data):
        if '[code=8a75]' not in data:
            self.stream.write(data)
            self.stream.flush()

    def flush(self):
        self.stream.flush()


if __name__ == '__main__':
    print('Starting sdx-survey')
    sys.stdout = OutputFilter(sys.stdout)
    cloud_config()
    from app import subscriber
    subscriber.start()
