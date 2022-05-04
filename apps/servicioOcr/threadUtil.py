
from threading import Thread
import threading
import time
from apps.servicioOcr.util import extraerOcr
def countdown(name, delay, count):
    while count:
        time.sleep(delay)
        print (f'{name, time.ctime(time.time()), count}')
        count -= 1

class newThread():
    def __init__(self, name, count, slug,nombreDoc):
        threading.Thread.__init__(self)
        self.name = name
        self.count = count
        self.slug = slug
        self.nombreDoc = nombreDoc
    def run(self):
        
        print("Starting: " + self.name + "\n")
        countdown(self.name, 1,self.count)
        extraerOcr(self.nombreDoc,self.slug)
        print("Exiting: " + self.name + "\n")
