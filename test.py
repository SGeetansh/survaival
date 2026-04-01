import threading
import time


def download():
    print("Downloading...")
    time.sleep(5)
    print("Download complete")


t = threading.Thread(target=download)
t.start()

for i in range(5):
    print("Doing other work", i)
    time.sleep(1)

t.join()
print("Program finished")
