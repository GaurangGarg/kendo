import threading


class ReadWriteLock(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._readGo = threading.Condition()
        self._writeGo = threading.Condition()
        self._activeReaders = 0
        self._activeWriters = 0
        self._waitingReaders = 0
        self._waitingWriters = 0

    def start_read(self):
        self._lock.acquire()
        self._waitingReaders += 1
        while self._read_should_wait():
            with self._readGo:
                # print 'Waiting to read {0}'.format(self)
                self._readGo.wait()
        self._waitingReaders -= 1
        self._activeReaders += 1
        self._lock.release()

    def done_read(self):
        self._lock.acquire()
        self._activeReaders -= 1
        if self._activeReaders == 0 and self._waitingWriters > 0:
            with self._writeGo:
                self._writeGo.notify()
        self._lock.release()

    def start_write(self):
        self._lock.acquire()
        self._waitingWriters += 1
        while self._write_should_wait():
            with self._writeGo:
                # print 'Waiting to write {0}'.format(self)
                self._writeGo.wait()
        self._waitingWriters -= 1
        self._activeWriters += 1
        self._lock.release()

    def done_write(self):
        self._lock.acquire()
        self._activeWriters -= 1
        if self._waitingWriters > 0:
            with self._writeGo:
                self._writeGo.notify()
        elif self._waitingReaders > 0:
            with self._readGo:
                self._readGo.notify_all()
        self._lock.release()

    def _read_should_wait(self):
        return self._activeWriters > 0 or self._waitingWriters > 0

    def _write_should_wait(self):
        return self._activeWriters > 0 or self._activeReaders > 0


if __name__ == "__main__":

    rw_lock = ReadWriteLock()
    lst = []

    class SimpleReader(threading.Thread):
        def run(self):
            rw_lock.start_read()
            print self, 'Start Read'
            try:
                print 'Content Read by {0}: {1}'.format(self, lst)
            except Exception as e:
                print e
            print self, 'Done Read'
            rw_lock.done_read()

    class SimpleWriter(threading.Thread):
        def run(self):
            rw_lock.start_write()
            print self, 'Start Write'
            lst.append(1)
            print self, 'Done Write'
            rw_lock.done_write()

    reader1 = SimpleReader()
    writer1 = SimpleWriter()
    reader2 = SimpleReader()
    writer2 = SimpleWriter()
    writer1.start()
    reader1.start()
    writer2.start()
    reader2.start()
    writer1.join()
    reader1.join()
    writer2.join()
    reader2.join()