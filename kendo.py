#!/usr/bin/python2

import multiprocessing

class Kendo():
    """Arbitrator through which all lock requests must go through.

    Members:
    num_locks - number of available locks
    clocks    - deterministic logical times for each process
    lrlt_list - last release times for each lock
    lock_held_list - list of which locks are held/free
    """

    def __init__(self, max_processes, num_locks, debug = False):
        """Initialize a Kendo arbitrator.

        Args:
        max_processes - the maximum possible number of processes that will run
        num_locks     - number of locks available to all processes
        debug         - whether or not to be verbose
        """

        # Create a global mutex for bookkeeping and dumping debug messages
        self.global_lock = multiprocessing.Lock()

        self.debug = debug
        self.num_locks = num_locks
        self.max_processes = max_processes
        self.processes = []

        # Initialize all locks that could be used
        manager = multiprocessing.Manager()
        self.locks = [manager.Lock() for i in xrange(num_locks)]
        
        # Initialize deterministic logical clocks
        self.clocks = manager.list([0] * max_processes)

        # Initialize lock release times
        self.lrlt_list = manager.list([0] * num_locks)

        # ...and lock statuses
        self.lock_held_list = manager.list([False] * num_locks)

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
            if self.try_lock(lock_number):
                self.global_lock.release()
                if self.lrlt_list[lock_number] >= self.clocks[pid]:
                    # Atomically release and label lock as not held
                    # XXX edge case when starting processes must wait one turn wheen lrlt_list is all zeros
                    self.global_lock.acquire()
                    self.locks[lock_number].release()
                    self.lock_held_list[lock_number] = False
                    self.global_lock.release()
                else:
                    if self.debug:
                        self.global_lock.acquire()
                        print "Process", pid, "Locking Lock", lock_number
                        print "CLOCKS", self.clocks
                        print '\n'
                        self.global_lock.release()
                    break
            else:
                self.global_lock.release()

            # Increment the process's logical time while it's spinning
            self.clocks[pid] += 1

        # Increment the process's logical time after acquisition
        self.clocks[pid] += 1

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
        self.locks[lock_number].release()
        self.clocks[pid] += 1

        if self.debug:       	
            print "Process", pid, "Unlocking Lock", lock_number
            print "CLOCKS", self.clocks
            print "LAST RELEASE TIME", self.lrlt_list[lock_number]
            print '\n'

        self.global_lock.release()

    def try_lock(self, lock_number):
        """Try to obtain a lock.

        Args:
        lock_number - index of the desired lock

        Returns True if lock is free, False if acquisition failed
        """

        # Check if the lock is free
        if not self.lock_held_list[lock_number]:
            self.lock_held_list[lock_number] = True
            self.locks[lock_number].acquire()
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
            if self.debug:
            	self.global_lock.acquire()
            	'''
            	print "PID", "CLOCK VALUE"
                print pid, self.clocks
                '''
                self.global_lock.release()
        
            if process_clock_value == min(self.clocks) and pid == self.clocks.index(min(self.clocks)):
                break

    def pause_logical_clock(self):
        pass
    
    def resume_logical_clock(self):
        pass
    
    def increment_logical_clock(self):
        pass

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

    def register_process(self, process):
        """Register a process to be run with this arbitrator

        Args:
        process - the process to be run

        Returns the PID of the process, None if something went awry.
        """
        if len(self.processes) < self.max_processes:
            self.processes.append(process)
            return len(self.processes) - 1


if __name__ == "__main__":
    pass
