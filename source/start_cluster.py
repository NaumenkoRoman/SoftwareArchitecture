import hazelcast
import subprocess
import multiprocessing as mp
import threading
import time


def optimistic_func(increment_count):
    client = hazelcast.HazelcastClient(cluster_name="hello-world")
    local_map = client.get_map("my-distributed-map").blocking()
    local_map.put_if_absent("counter", 0)
    for i in range(increment_count):
        while True:
            old_value = local_map.get("counter")
            new_value = old_value + 1
            if local_map.replace_if_same("counter", old_value, new_value):
                break


def blocking_func(increment_count):
    client = hazelcast.HazelcastClient(cluster_name="hello-world")
    local_map = client.get_map("my-distributed-map").blocking()
    local_map.put_if_absent("counter", 0)
    for i in range(increment_count):
        local_map.lock("counter")
        value = local_map.get("counter")
        value = value + 1
        local_map.put("counter", value)
        local_map.unlock("counter")


def non_blocking_func(increment_count):
    client = hazelcast.HazelcastClient(cluster_name="hello-world")
    local_map = client.get_map("my-distributed-map").blocking()
    local_map.put_if_absent("counter", 0)
    for i in range(increment_count):
        value = local_map.get("counter")
        value = value + 1
        local_map.put("counter", value)


def increment_test(num_process, increment_count, increment_func):
    local_processes = []
    client = hazelcast.HazelcastClient(cluster_name="hello-world")
    local_map = client.get_map("my-distributed-map").blocking()
    local_map.put("counter", 0)

    for i in range(num_process):
        proc = mp.Process(target=increment_func, args=(increment_count,))
        local_processes.append(proc)
    for proc in local_processes:
        proc.start()
    for proc in local_processes:
        proc.join()

    return local_map.get("counter")


def consumer(max_elements):
    client = hazelcast.HazelcastClient(cluster_name="hello-world")
    local_queue = client.get_queue("queue")

    for i in range(max_elements):
        head = local_queue.take().result()
        # poisson pill
        if head == -1:
            local_queue.offer(-1, )
            break
        print(f"Consuming {head}")
    print("Consumer finished his job.")
    client.shutdown()


def producer(num_elements):
    client = hazelcast.HazelcastClient(cluster_name="hello-world")
    local_queue = client.get_queue("queue")
    for i in range(num_elements):
        if local_queue.offer(i):
            print(f"Produced: {i}")
            pass
        time.sleep(0.5)
    # push poisson pill
    local_queue.offer(-1)
    print("Producer finished his job.")
    client.shutdown()


def normal_queue():
    producer_thread = threading.Thread(target=producer, args=(100, ))
    consumer_threads = [
        threading.Thread(target=consumer, args=(100,)),
        threading.Thread(target=consumer, args=(100,))
    ]
    consumer_threads[0].start()
    consumer_threads[1].start()
    producer_thread.start()
    producer_thread.join()
    consumer_threads[0].join()
    consumer_threads[1].join()

def non_consumed_queue():
    agent = mp.Process(target=producer, args=(100,))
    agent.start()
    agent.join()


def main():
    increment_test_map = {
        "non-blocking": non_blocking_func,
        "blocking": blocking_func,
        "optimistic": optimistic_func
    }

    queue_test_map = {
        "normal": normal_queue,
        "non-consumed": non_consumed_queue
    }

    script_path = "..\\scripts\\start_member.bat"
    ports = [5701, 5702, 5703]
    processes = []
    for port in ports:
        proc = subprocess.Popen(f'start  cmd.exe /k "{script_path} {port} member-{port}"', shell=True)
        processes.append(proc)

    while True:
        command = input("cluster$ ").split(" ")
        if "help" in command:
            print("help\n"
                  "    - show this message.\n"
                  "exit\n"
                  "    - exit the console.\n"
                  "increment <type> <num-clients> <increment-count>\n"
                  "    - run increment test.\n"
                  "    args:\n"
                  "        - type : blocking|non-blocking|optimistic\n"
                  "        - num-clients : number of clients\n"
                  "        - increment-count : number of increments.\n"
                  "queue <test-type>\n"
                  "    - run bounded queue test\n"
                  "    args:\n"
                  "        - test-type : normal (1 producer, 2 consumers); non-consumed (only producer)")

        elif "exit" in command:
            break
        elif "increment" in command:
            num_clients, increment_count = int(command[2]), int(command[3])
            increment_function = increment_test_map[command[1]]
            result = increment_test(num_clients, increment_count, increment_function)
            print(f"Expected value: {num_clients * increment_count}; actual: {result}")
        elif "queue" in command:
            queue_test_type = command[1]
            queue_test = queue_test_map[queue_test_type]
            print(f"Running queue {queue_test_type} test...")
            queue_test()
        else:
            print("Command is not supported! Type \"help\" to see available commands")

    for process in processes:
        process.kill()


if __name__ == '__main__':
    # On Windows, the following function call is necessary for multiprocessing
    mp.freeze_support()
    main()
