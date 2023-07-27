#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <signal.h>
#include <sys/time.h>
#include <time.h>
#include <math.h>


#include "mms_value.h"
#include "goose_publisher.h"
#include "goose_receiver.h"
#include "hal_thread.h"

#include "goose_subscriber.h"

#include "linked_list.h"


void printLinkedList(LinkedList list){

    LinkedList valueElement = LinkedList_getNext(list);
    // LinkedList valueElement = LinkedList_get(list, 2);
    char buf[1024];
    while (valueElement) {

        MmsValue* value = (MmsValue*) LinkedList_getData(valueElement);
        if (value) {
            MmsValue_printToBuffer(value, buf, 1024);
            printf("%s\n", buf);
        }

        valueElement = LinkedList_getNext(valueElement);
    }
}

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

/* has to be executed as root! */
int
main(int argc, char **argv)
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

}