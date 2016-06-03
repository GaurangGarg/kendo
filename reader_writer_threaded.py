import threading
import time


class ReadWriteLock(object):
    def __init__(self):
        self._print_lock = threading.Lock()
        self._lock = threading.Lock()
        self._readGo = threading.Condition(self._lock)
        self._writeGo = threading.Condition(self._lock)
        self._activeReaders = 0
        self._activeWriters = 0
        self._waitingReaders = 0
        self._waitingWriters = 0

    def start_read(self):
        self._print_lock.acquire()
        print "Entered start_read"
        print time.time()
        self._print_lock.release()
        self._lock.acquire()
        self._print_lock.acquire()
        print "Got lock in start_read"
        print time.time()
        self._print_lock.release()
        self._waitingReaders += 1
        self.print_state_vars()
        while self._read_should_wait():
            self._readGo.wait()
        self._waitingReaders -= 1
        self._activeReaders += 1
        self.print_state_vars()
        self._lock.release()

    def done_read(self):
        self._print_lock.acquire()
        print "Entered done_read"
        print time.time()
        self._print_lock.release()
        self._lock.acquire()
        self._print_lock.acquire()
        print "Got lock in done_read"
        print time.time()
        self._print_lock.release()
        self._activeReaders -= 1
        print self.print_state_vars()
        if self._activeReaders == 0 and self._waitingWriters > 0:
            self._writeGo.notify()
        self._lock.release()

    def start_write(self):
        self._print_lock.acquire()
        print "Entered start_write"
        print time.time()
        self._print_lock.release()
        self._lock.acquire()
        self._print_lock.acquire()
        print "Got lock in start_write"
        print time.time()
        self._print_lock.release()
        self._waitingWriters += 1
        self.print_state_vars()
        while self._write_should_wait():
            self._writeGo.wait()
        self._waitingWriters -= 1
        self._activeWriters += 1
        self.print_state_vars()
        self._lock.release()

    def done_write(self):
        self._print_lock.acquire()
        print "Entered done_write"
        print time.time()
        self._print_lock.release()
        self._lock.acquire()
        self._print_lock.acquire()
        print "Got lock in done_write"
        print time.time()
        self._print_lock.release()
        self._activeWriters -= 1
        print self.print_state_vars()
        if self._waitingWriters > 0:
            self._writeGo.notify()
        elif self._waitingReaders > 0:
            self._readGo.notify_all()
        self._lock.release()

    def _read_should_wait(self):
        return self._activeWriters > 0 or self._waitingWriters > 0

    def _write_should_wait(self):
        return self._activeWriters > 0 or self._activeReaders > 0

    def print_state_vars(self):
        self._print_lock.acquire()
        print "Active Readers: {0}".format(self._activeReaders)
        print "Active Writers: {0}".format(self._activeWriters)
        print "Waiting Readers: {0}".format(self._waitingReaders)
        print "Waiting Writers: {0}".format(self._waitingWriters)
        self._print_lock.release()


if __name__ == "__main__":

    rw_lock = ReadWriteLock()
    lst = []

    def reader(lock, shared_data, sleep_amount):
        time.sleep(sleep_amount)
        lock.start_read()
        print 'Start Read'
        try:
            print 'Content Read {0}'.format(shared_data)
        except Exception as e:
            print e
        print 'Done Read'
        lock.done_read()

    def writer(lock, shared_data, sleep_amount):
        time.sleep(sleep_amount)
        lock.start_write()
        print 'Start Write'
        shared_data.append(1)
        print 'Done Write'
        lock.done_write()


    r1 = threading.Thread(target=reader, args=(rw_lock, lst, 0))
    w1 = threading.Thread(target=writer, args=(rw_lock, lst, 0))
    r2 = threading.Thread(target=reader, args=(rw_lock, lst, 0))
    # r1 = threading.Thread(target=reader, args=(rw_lock, lst, 2))
    # w2 = threading.Thread(target=writer, args=(rw_lock, lst, 3))
    # r2 = threading.Thread(target=reader, args=(rw_lock, lst, 4))
    r2.start()
    w1.start()
    r1.start()
    # w2.start()
    # r2.start()

    # With Kendo, RW problem wont support multiple readers + 1 writer, it will be 1 reader and 1 writer