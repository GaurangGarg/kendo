import reader_writer_kendo


class ReaderProcess(object):
    """A thread that computes part of a sum."""

    def __init__(self, arbitrator):
        """Construct a SumProcess.

        Args:
        arbitrator - the kendo (or other) arbitrator
        lock_num - lock protecting shared sum
        nums - iterable of numbers to addup
        delay_time - time to delay before starting work
        work_time - simulated time it takes to complete the work
        """

        self.arbitrator = arbitrator

        # Initialize the shared memory total
        # XXX: this is redundant since multiple threads will do this, but it's
        # OK since this is just for initialization before anything runs
        arbitrator.mutate_shared("total_sum", 0)

        # FIXME: horrible dependencies; processes need their own pids...
        self.pid = arbitrator.register_process(self, "reader")

    def run(self):
        """Run this SumProcess. Add up its numbers and update the total when
        done.
        """

        print "Reader Process, PID = ", self.pid, " starting..."

        self.arbitrator.det_mutex_lock(self.pid, 0)

        print "Reader Process, PID = {0} read the following: {1}".format(self.pid, self.arbitrator.shared_mem)

        self.arbitrator.det_mutex_unlock(self.pid, 0)

        # FIXME: remove this after the scheduling's fixed
        self.arbitrator.clocks[self.pid] = 10000

        print "Reader Process, PID = ", self.pid, " done!"


class WriterProcess():
    """A thread that computes part of a sum."""

    def __init__(self, arbitrator):
        """Construct a SumProcess.

        Args:
        arbitrator - the kendo (or other) arbitrator
        lock_num - lock protecting shared sum
        nums - iterable of numbers to addup
        delay_time - time to delay before starting work
        work_time - simulated time it takes to complete the work
        """

        self.arbitrator = arbitrator

        # Initialize the shared memory total
        # XXX: this is redundant since multiple threads will do this, but it's
        # OK since this is just for initialization before anything runs
        arbitrator.mutate_shared("total_sum", 0)

        # FIXME: horrible dependencies; processes need their own pids...
        self.pid = arbitrator.register_process(self, "writer")

    def run(self):
        """Run this SumProcess. Add up its numbers and update the total when
        done.
        """

        print "Writer Process, PID = ", self.pid, " starting..."

        self.arbitrator.det_mutex_lock(self.pid, 0)

        self.arbitrator.shared_mem["total_sum"] += self.pid

        self.arbitrator.det_mutex_unlock(self.pid, 0)

        # FIXME: remove this after the scheduling's fixed
        self.arbitrator.clocks[self.pid] = 10000

        print "Writer Process, PID = ", self.pid, " done!"


if __name__ == "__main__":

    print "Testing Reader and Writer Processes"

    kendo_arbitrator = reader_writer_kendo.RWKendo(max_processes=3)

    reader1 = ReaderProcess(kendo_arbitrator)
    writer1 = WriterProcess(kendo_arbitrator)
    reader2 = ReaderProcess(kendo_arbitrator)

    kendo_arbitrator.run()

    print "Done Testing Reader and Writer Processes"
