import multiprocessing
import time


class ReadWriteLock(object):
    """ A lock that allows multiple readers and one writer.

    Members:
    print_lock - lock to print debug information
    lock - lock to make ReadWriteLock operations atomic
    readGo - Condition Variable that Readers wait on
    writeGo - Condition Variable that Writers wait on
    activeReaders - # of active Readers (must be >= 0)
    activeWriters - # of active Writers (must be >= 0 and <= 1)
    waitingReaders - # of waiting Readers (must be >= 0)
    waitingWriters - # of waiting Writers (must be >= 0)

    """

    def __init__(self):
        """Initialize a ReadWriteLock."""

        manager = multiprocessing.Manager()
        self._print_lock = manager.Lock()
        self._lock = manager.Lock()
        self._readGo = manager.Condition(self._lock)
        self._writeGo = manager.Condition(self._lock)
        self._activeReaders = 0
        self._activeWriters = 0
        self._waitingReaders = 0
        self._waitingWriters = 0

    def start_read(self):
        """
        Acquire RWLock
        Check if ok to Read else wait on cv
        Release RWLock
        """
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
        """
        Acquire RWLock
        Decrement number of activeReaders
        Notify a waitingWriter
        Release RWLock
        """
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
        """
        Acquire RWLock
        Check if ok to Write else wait on cv
        Release RWLock
        """
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
        """
        Acquire RWLock
        Decrement activeWriters
        Wake a waitingWriters if any
        If no waitingWriters, wake a waitingReader if any
        Release RWLock
        """
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
        """
        Read should wait if theres any active or waiting writers
        """
        return self._activeWriters > 0 or self._waitingWriters > 0

    def _write_should_wait(self):
        """
        Write should wait if there's any active writer or readerss
        """
        return self._activeWriters > 0 or self._activeReaders > 0

    def print_state_vars(self):
        self._print_lock.acquire()
        print "Active Readers: {0}".format(self._activeReaders)
        print "Active Writers: {0}".format(self._activeWriters)
        print "Waiting Readers: {0}".format(self._waitingReaders)
        print "Waiting Writers: {0}".format(self._waitingWriters)
        self._print_lock.release()
