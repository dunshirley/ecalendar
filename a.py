from tendo import singleton
me = singleton.SingleInstance()
import time
i = 0
while True:
    print i
    i += 1
    time.sleep(1)
