import multiprocessing
from read_write_lock import ReadWriteLock


class RWKendo(object):
    """Arbitrator through which all lock requests must go through.

    Members:
    num_locks - number of available locks
    clocks    - deterministic logical times for each process
    lrlt_list - last release times for each lock
    lock_held_list - list of which locks are held/free
    shared_mem - shared memory map
    priorities - thread 'priorities' for acquiring locks
    readers - list that keeps track of reader processes PIDs
    writers - list that keeps track of writer processes PIDs
    """

    def __init__(self, max_processes, priorities=None, debug=False):
        """Initialize a RWKendo arbitrator.

        Args:
        max_processes - the maximum possible number of processes that will run
        debug         - whether or not to be verbose
        priorities    - iterable of thread priorities
        """

        # Create a global mutex for bookkeeping and dumping debug messages
        self.global_lock = multiprocessing.Lock()

        self.debug = debug
        self.max_processes = max_processes
        self.processes = []

        self.readers = []
        self.writers = []

        # Initialize priorities. By default, every thread has the same
        # priority
        if priorities is None:
            priorities = [1 for _ in xrange(max_processes)]

        self.priorities = priorities

        # Initialize all locks that could be used
        manager = multiprocessing.Manager()
        self.locks = [ReadWriteLock()]

        # Initialize shared memory
        self.shared_mem = manager.dict()

        # Initialize deterministic logical clocks
        self.clocks = manager.list([0] * max_processes)

        # Initialize lock release times
        self.lrlt_list = manager.list([0] * 1)

        # ...and lock statuses
        self.lock_held_list = manager.list([False] * 1)

    def det_mutex_lock(self, pid, lock_number):
        """Attempt to acquire a mutex

        Args:
        pid - ID/index of process
        lock_number - index of lock the process wants
        """

        while True:
            self.wait_for_turn(pid)

            if self.debug:
                self.global_lock.acquire()
                print "Process", pid, "'s Turn with Lock", lock_number
                print "CLOCKS", self.clocks
                print "LAST RELEASE TIME", self.lrlt_list
                print '\n'
                self.global_lock.release()

            # TODO: docs
            self.global_lock.acquire()
            if self.try_lock(lock_number, pid):
                self.global_lock.release()
                # NOTE: Reader Writer Implementation will not have issue of nested locks as there is only one lock - RWLock.
                # Naive implementation of Kendo is used
                break
            else:
                self.global_lock.release()

            # Increment the process's logical time while it's spinning
            self.clocks[pid] += 1

        # Increment the process's logical time after acquisition
        self.clocks[pid] += self.priorities[pid]

    def det_mutex_unlock(self, pid, lock_number):
        """Deterministically unlock a mutex.

        Args:
        pid         - ID/index of the calling process
        lock_number - index of the lock to unlock
        """

        # Atomically release and label lock as not held
        self.global_lock.acquire()
        self.lock_held_list[lock_number] = False
        self.lrlt_list[lock_number] = self.clocks[pid]
        if pid in self.readers:
            self.locks[lock_number].done_read()
        else:
            self.locks[lock_number].done_write()
        self.clocks[pid] += 1

        if self.debug:
            print "Process", pid, "Unlocking Lock", lock_number
            print "CLOCKS", self.clocks
            print "LAST RELEASE TIME", self.lrlt_list[lock_number]
            print '\n'

        self.global_lock.release()

    def try_lock(self, lock_number, pid):
        """Try to obtain a lock.

        Args:
        lock_number - index of the desired lock

        Returns True if lock is free, False if acquisition failed
        """

        # Check if the lock is free
        if not self.lock_held_list[lock_number]:
            self.lock_held_list[lock_number] = True
            if pid in self.readers:
                self.locks[lock_number].start_read()
            else:
                self.locks[lock_number].start_write()
            return True

        return False

    def wait_for_turn(self, pid):
        """Wait until the given process can proceed

        Args:
        pid - ID/index of the process
        """

        # Get the process's logical time
        process_clock_value = self.clocks[pid]

        # Spin while it's either not its turn, or it has to wait until a certain
        # logical time.
        while True:

            if process_clock_value == min(self.clocks) and pid == self.clocks.index(min(self.clocks)):
                break

    def run(self):
        """Run all processes"""

        if self.debug:
            print "Starting to run all processes..."

        threads = []

        for p in self.processes:
            t = multiprocessing.Process(target=p.run)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        if self.debug:
            print "Done!"

    def register_process(self, process, process_type):
        """Register a process to be run with this arbitrator

        Args:
        process - the process to be run
        process_type - pass either reader or writer so arbitrator can keep track of reader and writer processes

        Returns the PID of the process, None if something went awry.
        """
        if len(self.processes) < self.max_processes:
            self.processes.append(process)
            if process_type == "reader":
                self.readers.append(len(self.processes)-1)
            else:
                self.writers.append(len(self.processes) - 1)
            return len(self.processes) - 1

    def mutate_shared(self, name, value):
        """Add/mutate a shared object to simulate shared memory.

        Args:
        name - name of the value
        value - value
        """

        self.shared_mem[name] = value
