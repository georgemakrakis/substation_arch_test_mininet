/*
 * goose_subscriber_example.c
 *
 * This is an example for a standalone GOOSE subscriber
 *
 * Has to be started as root in Linux.
 */

#include "goose_receiver.h"
#include "goose_subscriber.h"
#include "hal_thread.h"
#include "linked_list.h"

#include <stdlib.h>
#include <stdio.h>
#include <signal.h>

#include <sys/time.h>
#include <time.h>
#include <math.h>


static int running = 1;

static void
sigint_handler(int signalId)
{
    running = 0;
}

static void
gooseListener(GooseSubscriber subscriber, void* parameter)
{
    printf("GOOSE event:\n");
    printf("  stNum: %u sqNum: %u\n", GooseSubscriber_getStNum(subscriber),
            GooseSubscriber_getSqNum(subscriber));
    printf("  timeToLive: %u\n", GooseSubscriber_getTimeAllowedToLive(subscriber));

    uint64_t timestamp = GooseSubscriber_getTimestamp(subscriber);

    printf("  timestamp: %u.%u\n", (uint32_t) (timestamp / 1000), (uint32_t) (timestamp % 1000));
    printf("  message is %s\n", GooseSubscriber_isValid(subscriber) ? "valid" : "INVALID");

    MmsValue* values = GooseSubscriber_getDataSetValues(subscriber);

    char buffer[1024];

    MmsValue_printToBuffer(values, buffer, 1024);

    printf("  allData: %s\n", buffer);

    char buffer_time[26];
    int millisec;
    struct tm* tm_info;
    struct timeval tv;

    gettimeofday(&tv, NULL);

    millisec = lrint(tv.tv_usec/1000.0); // Round to nearest millisec
    if (millisec>=1000) { // Allow for rounding up to nearest second
        millisec -=1000;
        tv.tv_sec++;
    }

    tm_info = localtime(&tv.tv_sec);

    strftime(buffer_time, 26, "%Y:%m:%d %H:%M:%S", tm_info);
    printf("At %s.%03d\n", buffer_time, millisec);

    
}

int
main(int argc, char** argv)
{
    GooseReceiver receiver = GooseReceiver_create();
    char *device_name;

    if (argc > 1) {
        printf("Set interface id: %s\n", argv[1]);
        GooseReceiver_setInterfaceId(receiver, argv[1]);
        device_name = argv[2];
    }
    else {
        // printf("Using interface eth0\n");
        printf("Using interface lo\n");
        // printf("Using interface 487E-eth0\n");
        // GooseReceiver_setInterfaceId(receiver, "eth0");

        // the interface of SEL 487E device in mininet 
        // GooseReceiver_setInterfaceId(receiver, "487E-eth0");
        GooseReceiver_setInterfaceId(receiver, "lo");
    }

    char * devices [] = { "RTAC", "651R_2", "787_2", "451_2" };
    int len = sizeof(devices)/sizeof(devices[0]);
    int found = 0;

    for(int i = 0; i < len; ++i) {
        if(!strcmp(devices[i], device_name)) {
            printf("Device in list\n");
            found = 1;
        }
        if(found == 0 && i+1 == len) {
             printf("Device not in list, exiting..\n");
             return 1;
        }
    }

    GooseSubscriber subscriber;

    if (strcmp(device_name, "RTAC") == 0) 
    {
        printf("GOOSE RTAC configuration initiated...\n");
        
        // This should be sub for data from 651R_2
        // TODO: We need for the rest of them as well.
        subscriber = GooseSubscriber_create("simple_651R_2/PRO$CO$BCACSWI2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x02};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1002);
    } 
    else if (strcmp(device_name, "651R_2") == 0)
    {
        printf("GOOSE 651R_2 configuration initiated...\n");

        // This should be sub for data from RTAC
        // TODO: We need for the rest of them as well.
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x01};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1001);
    }
    else if (strcmp(device_name, "787_2") == 0)
    {
        printf("GOOSE 787_2 configuration initiated...\n");
    }
    else if (strcmp(device_name, "451_2") == 0)
    {
        printf("GOOSE 451_2 configuration initiated...\n");
    }
    else
    {
        printf("No device supported, exiting...\n");
        return 1;
    }

    // GooseSubscriber subscriber = GooseSubscriber_create("simpleIOGenericIO/LLN0$GO$gcbAnalogValues", NULL);

    // uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x01};
    // GooseSubscriber_setDstMac(subscriber, dstMac);
    // GooseSubscriber_setAppId(subscriber, 1000);

    GooseSubscriber_setListener(subscriber, gooseListener, NULL);

    GooseReceiver_addSubscriber(receiver, subscriber);

    GooseReceiver_start(receiver);

    if (GooseReceiver_isRunning(receiver)) {
        signal(SIGINT, sigint_handler);

        while (running) {
            // NOTE: this was for μs
            // Thread_sleep(100);
            
            Thread_sleep(100);
        }
    }
    else {
        printf("Failed to start GOOSE subscriber. Reason can be that the Ethernet interface doesn't exist or root permission are required.\n");
    }

    GooseReceiver_stop(receiver);

    GooseReceiver_destroy(receiver);

    return 0;
}
