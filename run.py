from app import cloud_config

if __name__ == '__main__':
    print('Starting sdx-survey')
    cloud_config()
    from app import subscriber
    subscriber.start()
