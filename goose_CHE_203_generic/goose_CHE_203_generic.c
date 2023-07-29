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
    GoosePublisher publisher;
    char *interface;
    char *device_name;

    if (argc > 1) {
        interface = argv[1];
        device_name = argv[2];
        printf("Set interface id: %s\n",  interface);
        
        GooseReceiver_setInterfaceId(receiver, interface);
    }
    else {
        // printf("Using interface eth0\n");
        printf("Not enough parameters, exiting...\n");
        return 1;
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

    // First let's setup the subscriber
    GooseSubscriber subscriber;

    if (strcmp(device_name, "RTAC") == 0) 
    {
        printf("GOOSE subscriber RTAC configuration initiated...\n");
        
        // This should be sub for data from 651R_2
        // TODO: We need for the rest of them as well.
        subscriber = GooseSubscriber_create("simple_651R_2/PRO$CO$BCACSWI2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x02};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1002);
    } 
    else if (strcmp(device_name, "651R_2") == 0)
    {
        printf("GOOSE subscriber 651R_2 configuration initiated...\n");

        // This should be sub for data from RTAC
        // TODO: We need for the rest of them as well.
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x01};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1001);
    }
    else if (strcmp(device_name, "787_2") == 0)
    {
        printf("GOOSE subscriber 787_2 configuration initiated...\n");
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

    //.. and now the publisher
    LinkedList dataSetValues = LinkedList_create();
    CommParameters gooseCommParameters;
    
    if (strcmp(device_name, "RTAC") == 0) 
    {
        printf("GOOSE publisher RTAC configuration initiated...\n");
        // TODO: 
        // Should have the integer for the True/False or Open/Close
        // and another interger for Trip/NoTrip
        // gooseCommParameters should be here as well.
        // There should be multiple ones based on the comm paths of
        // the devices

        // Breaker status (for device No ?) 0/1 or Open/Close.
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(true));

        // Trip command (for device No ?) Trip/NoTrip.
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // NOTE: Disable for now might be enabled later.
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(false));

        gooseCommParameters.appId = 1001;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x01;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;

    } 
    // NOTE: JUST FOR TESTING
    // else if (strcmp(device_name, "651R_2") == 0)
    if (strcmp(device_name, "RTAC") == 0)
    {
        printf("GOOSE publisher 651R_2 configuration initiated...\n");

        // Breaker status (for device No ?) 0/1 or Open/Close.
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(true));

        // Trip command (for device No ?) Trip/NoTrip.
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
         // NOTE: Disable for now might be enabled later.
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(false));

        gooseCommParameters.appId = 1002;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x02;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;

    }
    else if (strcmp(device_name, "787_2") == 0)
    {
        printf("GOOSE publisher 787_2 configuration initiated...\n");
    }
    else if (strcmp(device_name, "451_2") == 0)
    {
        printf("GOOSE publisher 451_2 configuration initiated...\n");
    }
    else
    {
        printf("No device supported, exiting...\n");
        return 1;
    }

    publisher = GoosePublisher_create(&gooseCommParameters, interface);
    // publisher = GoosePublisher_create(&gooseCommParameters, "eth0");

    int i = 0;
    uint32_t prev_stNum = 0; 

    // TODO: The below should be adjusted for each device
    // based on the collected information.

    // Interval in ms
    // int min_interval = 10;
    int min_interval = 4;
    // int min_interval = 500;
    int publish_interval = min_interval;
    // int max_interval = 100;
    int max_interval = 1000;
    // int max_interval = 5000;
    
    // NOTE: Used as a simple condition to increase the StNum
    int max_i = 10;
    if (publisher) {
        // TODO: Change the goCbRef and DataSetRef as well
        // GoosePublisher_setGoCbRef(publisher, "simpleIOGenericIO/LLN0$GO$gcbAnalogValues");
        GoosePublisher_setConfRev(publisher, 1);
        // GoosePublisher_setDataSetRef(publisher, "simpleIOGenericIO/LLN0$AnalogValues");
        GoosePublisher_setTimeAllowedToLive(publisher, 500);

        if (strcmp(device_name, "RTAC") == 0) 
        {
            printf("RTAC GOOSE configuration initiated...\n");
        } 
        // NOTE: JUST FOR TESTING
        // else if (strcmp(device_name, "651R_2") == 0)
        if (strcmp(device_name, "RTAC") == 0)
        {
            printf("651R_2 GOOSE configuration initiated...\n");

            // GoosePublisher_setGoCbRef(publisher, "simple_651R_2/LLN0$CO$BCACSWI2$Pos$ctlVal");
            GoosePublisher_setGoCbRef(publisher, "simple_651R_2/PRO$CO$BCACSWI2");
            GoosePublisher_setDataSetRef(publisher, "simple_651R_2/PRO$BCACSWI2_DataSet");
        }
        else if (strcmp(device_name, "787_2") == 0)
        {
            printf("787_2 GOOSE configuration initiated...\n");
        }
        else if (strcmp(device_name, "451_2") == 0)
        {
            printf("451_2 GOOSE configuration initiated...\n");
        }
        else
        {
            printf("No device supported, exiting...\n");
            return 1;
        }
    }



    GooseSubscriber_setListener(subscriber, gooseListener, NULL);

    GooseReceiver_addSubscriber(receiver, subscriber);

    GooseReceiver_start(receiver);

    if (GooseReceiver_isRunning(receiver)) {
        // ready to receive messages.
        signal(SIGINT, sigint_handler);

        while (running) {
            // NOTE: this was for μs
            // Thread_sleep(100);
            
            Thread_sleep(100);

            // Now we also publish based  on the defined interval
            if (GoosePublisher_publish(publisher, dataSetValues) == -1) {
                    printf("Error sending message!\n");
            }
            Thread_sleep(publish_interval);
            printf("Publishing...\n");

            // First option 
            // if( i <= 3) {
            //     interval = 2 * interval;
            // }
            // else {
            //     interval = max_interval;
            // }

            // Second option
            if( i == 0) {
                publish_interval = min_interval;
            }
            else if( i < 3) {
                publish_interval = 2 * publish_interval;
            }
            else {
                publish_interval = max_interval;
            }
            
            // .. then us a condition to change something to start from the
            // beginning

            if( i == max_i) {
                GoosePublisher_increaseStNum(publisher);
                i = 0;
                publish_interval = min_interval;
            }

            i++;

        }
    }
    else {
        printf("Failed to start GOOSE subscriber. Reason can be that the Ethernet interface doesn't exist or root permission are required.\n");
    }

    GoosePublisher_destroy(publisher);

    GooseReceiver_stop(receiver);

    GooseReceiver_destroy(receiver);

}