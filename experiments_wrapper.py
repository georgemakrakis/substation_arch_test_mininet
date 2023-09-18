import os
import signal
import subprocess
import threading
import time
import psutil

handle_1 = None
handle_2 = None


def run_process(program_command, program_type, wait_time):
 
    
    global handle_1
    global handle_2
    output = None
    if program_type == "controller":
        try:
            handle_1 = subprocess.Popen(program_command, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            output = handle_1.stdout.read()
            rc = handle_1.wait(timeout=wait_time)   # at this point, if process is killed, the thread exits
            print("DEVICE PROGRAM {0}", rc)
        except subprocess.TimeoutExpired:
            print("Timeout for device, terminating ...")
            os.killpg(os.getpgid(handle_1.pid), signal.SIGKILL)

    elif program_type == "mininet":
        try:
            handle_2 = subprocess.Popen(program_command, start_new_session=True, stdout=subprocess.PIPE)
            output = handle_2.stdout.read()
            rc = handle_2.wait(timeout=wait_time)   # at this point, if process is killed, the thread exits
            print("MININET PROGRAM {0}", rc)
        except subprocess.TimeoutExpired:
            print("Timeout for tcpdump, terminating ...")
            os.killpg(os.getpgid(handle_2.pid), signal.SIGKILL)

    return

def main(security=False, scenario=1):

    wait_time = 30
   
    # for i in range(0, 1):
    # for i in range(0, 200):
    for i in range(0, 1000):

        clear_mn = subprocess.run(["sudo", "mn", "-c"])

        print(clear_mn.stdout)

        if security:

            program_command = ["sudo", "ryu", "run" ,"--verbose", "process_bus.py", "--config-file=params.conf"]
        else:
            program_command = ["sudo", "ryu", "run" ,"--verbose", "learning_controller.py", "--config-file=params.conf"]
        
        program_type = "controller"
        p1 = threading.Thread(target=run_process, args=(program_command, program_type, wait_time,))

        
        if security:
            program_command = ["sudo", "python", "process_bus_mininet.py", str(scenario), str(i), "True"]
        else:
            program_command = ["sudo", "python", "process_bus_mininet.py", str(scenario), str(i), "False"]

        program_type = "mininet"
        
        p2 = threading.Thread(target=run_process, args=(program_command, program_type, wait_time, ))
        p1.start()
        time.sleep(1)
        p2.start()
        p1.join(wait_time)
        p2.join(wait_time)

        if handle_1:
            # print("handle_1 here terminated")
            handle_1.terminate()
            # os.kill(handle_1.pid, signal.SIGTERM)
            print("handle_1 here terminated")
            os.killpg(os.getpgid(handle_1.pid), signal.SIGKILL)

        
        if handle_2:
            handle_2.terminate()
            print("handle_2 here terminated")
            # os.killpg(os.getpgid(handle_2.pid), signal.SIGKILL)

    return


if __name__ == '__main__':
    
    security=False
    # security=True

    scenario = 1
    # scenario = 2

    main(security=security, scenario=scenario)