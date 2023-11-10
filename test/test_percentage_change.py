from time import sleep


def loop():
    count = 4

    while True:
        if count <= 0:
            break
        else:
            print(count)
            count = count - 1

            sleep(1)

    pass


if __name__ == '__main__':
    loop()
