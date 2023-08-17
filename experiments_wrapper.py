import os
import signal
import subprocess
import threading
import time

handle_1 = None
handle_2 = None

def run_process(program_command, program_type, wait_time):
    # completed = subprocess.run(["python", "timer.py", "10"],  check=True)
    
    # with subprocess.Popen(["python", "timer.py", "10"]) as process:
    #     print(process.pid) # the pid
    #     os.kill(process.pid, signal.SIGTERM) #or signal.SIGKILL 
    
    global handle_1
    global handle_2
    output = None
    if program_type == "device":
        try:
            handle_1 = subprocess.Popen(program_command, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            # handle_1 = subprocess.Popen(program_command, start_new_session=True, stdout=subprocess.PIPE)
            output = handle_1.stdout.read()
            # rc = handle_1.wait()   # at this point, if process is killed, the thread exits
            rc = handle_1.wait(timeout=wait_time)   # at this point, if process is killed, the thread exits
            print("DEVICE PROGRAM {0}", rc)
        except subprocess.TimeoutExpired:
            print("Timeout for device, terminating ...")
            # os.killpg(os.getpgid(handle_1.pid), signal.SIGTERM)
            os.killpg(os.getpgid(handle_1.pid), signal.SIGKILL)

    elif program_type == "tcpdump":
        try:
            # handle_2 = subprocess.Popen(program_command, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            handle_2 = subprocess.Popen(program_command, start_new_session=True, stdout=subprocess.PIPE)
            output = handle_2.stdout.read()
            # rc = handle_1.wait()   # at this point, if process is killed, the thread exits
            rc = handle_2.wait(timeout=wait_time)   # at this point, if process is killed, the thread exits
            print("TCPDUMP PROGRAM {0}", rc)
        except subprocess.TimeoutExpired:
            print("Timeout for tcpdump, terminating ...")
            # os.killpg(os.getpgid(handle_1.pid), signal.SIGTERM)
            os.killpg(os.getpgid(handle_2.pid), signal.SIGKILL)

    
    # handle = subprocess.Popen(program_command, stdout=subprocess.PIPE)
    # output = handle.stdout.read()
    # rc = handle.wait()   # at this point, if process is killed, the thread exits with
    # print(rc)
    
    return

def main():

    # wait_time = 60
    wait_time = 20

    # program_command = ["python", "timer.py", "10"]
    # NOTE: Below is an example of how each individual device should be run inside the simulation
    # program_command = ["sudo", "./goose_CHE_203_generic/goose_CHE_203_generic", "lo", "651R_2"]
    # # TODO: Peform better filterting here (i.e. eth host ....)
    # tcpdump_command = ["sudo", "tcpdump", "-i", "lo", "ether", "host", "01:0c:cd:01:00:02", "-w", "exp_1.pcap"]

    # program_type = "device"
    # p1 = threading.Thread(target=run_process, args=(program_command, program_type, wait_time,))
    
    # program_type = "tcpdump"
    # p2 = threading.Thread(target=run_process, args=(tcpdump_command, program_type, wait_time, ))

    program_command = ["sudo", "ryu", "run" ,"--verbose", "process_bus.py", "--config-file=params.conf"]
    program_type = "device"
    p1 = threading.Thread(target=run_process, args=(program_command, program_type, wait_time,))
    
    program_command = ["sh", "topology_mininet.sh"]
    program_type = "tcpdump"
    p2 = threading.Thread(target=run_process, args=(program_command, program_type, wait_time, ))


    p2.start()
    p1.start()
    p2.join(wait_time)
    p1.join(wait_time)

    if handle_1:
        # print("handle_1 here terminated")
        handle_1.terminate()
        # os.kill(handle_1.pid, signal.SIGTERM)
        print("handle_1 here terminated")
        os.killpg(os.getpgid(handle_1.pid), signal.SIGKILL)

    
    if handle_2:
        handle_2.terminate()
        print("handle_2 here terminated")
        os.killpg(os.getpgid(handle_2.pid), signal.SIGKILL)

    return


if __name__ == '__main__':

    main()