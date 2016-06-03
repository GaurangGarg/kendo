import reader_writer_kendo
import sys


class ReaderProcess(object):
    """A thread that reads from shared data."""

    def __init__(self, arbitrator):
        """Construct a ReaderProcess.

        Args:
        arbitrator - the RWkendo arbitrator
        """

        self.arbitrator = arbitrator

        # Initialize the shared memory total
        # XXX: this is redundant since multiple threads will do this, but it's
        # OK since this is just for initialization before anything runs
        arbitrator.mutate_shared("total_sum", 0)

        # FIXME: horrible dependencies; processes need their own pids...
        self.pid = arbitrator.register_process(self, "reader")

    def run(self):
        """Run this ReaderProcess.
        Acquire mutex, read shared data, Release mutex.
        """

        print "Reader Process, PID = ", self.pid, " starting..."

        self.arbitrator.det_mutex_lock(self.pid, 0)

        print "Reader Process, PID = {0} read the following: {1}".format(self.pid, self.arbitrator.shared_mem)

        self.arbitrator.det_mutex_unlock(self.pid, 0)

        # FIXME: Currently aribtrator doesn't remove process after it finishes from its list of processes; Set finished process's logical clock to maxint
        self.arbitrator.clocks[self.pid] = sys.maxint

        print "Reader Process, PID = ", self.pid, " done!"


class WriterProcess(object):
    """A thread that writes to shared data."""

    def __init__(self, arbitrator):
        """Construct a WriterProcess.

        Args:
        arbitrator - the RWkendo arbitrator
        """

        self.arbitrator = arbitrator

        # Initialize the shared memory total
        # XXX: this is redundant since multiple threads will do this, but it's
        # OK since this is just for initialization before anything runs
        arbitrator.mutate_shared("total_sum", 0)

        # FIXME: horrible dependencies; processes need their own pids...
        self.pid = arbitrator.register_process(self, "writer")

    def run(self):
        """Run this WriterProcess.
        Acquire mutex, write shared data, Release mutex.
        """

        print "Writer Process, PID = ", self.pid, " starting..."

        self.arbitrator.det_mutex_lock(self.pid, 0)

        self.arbitrator.shared_mem["total_sum"] += self.pid

        self.arbitrator.det_mutex_unlock(self.pid, 0)

        # FIXME: Currently aribtrator doesn't remove process after it finishes from its list of processes; Set finished process's logical clock to maxint
        self.arbitrator.clocks[self.pid] = sys.maxint

        print "Writer Process, PID = ", self.pid, " done!"


if __name__ == "__main__":

    print "Testing Reader and Writer Processes"

    kendo_arbitrator = reader_writer_kendo.RWKendo(max_processes=4)

    reader1 = ReaderProcess(kendo_arbitrator)
    writer1 = WriterProcess(kendo_arbitrator)
    writer_2 = WriterProcess(kendo_arbitrator)
    reader2 = ReaderProcess(kendo_arbitrator)

    kendo_arbitrator.run()

    print "Done Testing Reader and Writer Processes"
