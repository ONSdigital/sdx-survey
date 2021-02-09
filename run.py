
if __name__ == '__main__':
    print('Starting SDX Worker')
    from app import load_config
    load_config()
    from app import subscriber
    subscriber.start()
