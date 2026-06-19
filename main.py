import multiprocessing
import time
import os
import random

# This class simulates a simplified shared memory area, analogous to PostgreSQL's
# shared buffer cache, transaction log, or other shared data structures.
# multiprocessing.Manager allows Python objects to be shared between processes.
class SharedMemory:
    def __init__(self, manager):
        # A dictionary to hold shared data, like buffer pages and a transaction counter.
        self.data = manager.dict({
            'buffer_cache': {},
            'transaction_counter': 0
        })
        # A lock to simulate latches or mutexes used in PostgreSQL for concurrent access
        # to shared memory, preventing race conditions.
        self.lock = manager.Lock()

    def read_buffer(self, page_id):
        with self.lock:
            # Simulate reading a data page from the shared buffer cache.
            return self.data['buffer_cache'].get(page_id, f"Page {page_id} not in cache")

    def write_buffer(self, page_id, content):
        with self.lock:
            # Simulate writing (modifying) a data page in the shared buffer cache.
            self.data['buffer_cache'][page_id] = content
            print(f"[Backend {os.getpid()}] Wrote '{content}' to page {page_id} in shared buffer.")

    def increment_transaction_counter(self):
        with self.lock:
            # Simulate incrementing a global transaction counter, a common shared state.
            self.data['transaction_counter'] += 1
            current_count = self.data['transaction_counter']
            print(f"[Backend {os.getpid()}] Transaction counter incremented to {current_count}.")
            return current_count

# This function simulates a PostgreSQL Backend Process.
# Each backend handles a single client connection and executes queries.
def backend_process(process_id, shared_mem_proxy):
    pid = os.getpid()
    print(f"[Backend {pid}] Started for client connection {process_id}.")
    time.sleep(random.uniform(0.1, 0.5)) # Simulate connection setup time

    # Backends interact with shared memory to perform database operations.
    print(f"[Backend {pid}] Starting transaction {shared_mem_proxy.increment_transaction_counter()}.")

    page_to_access = random.randint(1, 5)
    action = random.choice(['read', 'write'])

    if action == 'write':
        content = f"Data from client {process_id}"
        shared_mem_proxy.write_buffer(page_to_access, content)
    else:
        read_data = shared_mem_proxy.read_buffer(page_to_access)
        print(f"[Backend {pid}] Read from page {page_to_access}: '{read_data}'.")

    time.sleep(random.uniform(0.2, 1.0)) # Simulate query execution time

    print(f"[Backend {pid}] Finished processing for client connection {process_id}.")

# This function simulates the PostgreSQL Postmaster Process.
# The Postmaster is the main server process that starts, manages, and monitors
# all other PostgreSQL processes.
def postmaster_process():
    print(f"[Postmaster {os.getpid()}] PostgreSQL server starting...")

    # The Postmaster initializes shared memory segments at startup.
    # Here, multiprocessing.Manager is used to create sharable objects.
    manager = multiprocessing.Manager()
    shared_mem = SharedMemory(manager)
    print(f"[Postmaster {os.getpid()}] Shared memory initialized.")

    backend_processes = []
    num_clients = 3 # Simulate 3 concurrent client connections

    print(f"[Postmaster {os.getpid()}] Spawning {num_clients} backend processes for clients...")
    for i in range(num_clients):
        # For each client connection, the Postmaster forks a new backend process.
        # This new process receives a proxy to the shared memory.
        p = multiprocessing.Process(target=backend_process, args=(i+1, shared_mem))
        backend_processes.append(p)
        p.start()
        time.sleep(0.1) # Give a little time for processes to start

    print(f"[Postmaster {os.getpid()}] All backend processes started. Waiting for them to complete...")

    # The Postmaster waits for all backend processes to complete their tasks.
    # In a real PostgreSQL server, it would continuously monitor them.
    for p in backend_processes:
        p.join()

    print(f"[Postmaster {os.getpid()}] All backend processes finished.")
    print(f"[Postmaster {os.getpid()}] Final shared buffer cache state: {shared_mem.data['buffer_cache']}")
    print(f"[Postmaster {os.getpid()}] Final transaction counter: {shared_mem.data['transaction_counter']}")

    manager.shutdown() # Clean up the shared memory manager resources.
    print(f"[Postmaster {os.getpid()}] PostgreSQL server shutting down.")

if __name__ == "__main__":
    postmaster_process()
