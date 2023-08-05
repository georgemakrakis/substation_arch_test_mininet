#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <signal.h>
#include <sys/time.h>
#include <time.h>
#include <math.h>

#include <pthread.h>
#include <unistd.h>

#include "mms_value.h"
#include "goose_publisher.h"
#include "goose_receiver.h"
#include "hal_thread.h"

#include "goose_subscriber.h"

#include "linked_list.h"

struct args_rec {
    int myid;
    GooseReceiver receiver;
};

struct args_pub {
    int myid;
    char *device_name;
    GoosePublisher publisher;
    GoosePublisher publisher_2;
    GoosePublisher publisher_3;
};


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

static 
LinkedList dataSetValues;

static
LinkedList dataSetValuesReceivedFrom651R_2;

static
LinkedList dataSetValuesReceivedFromRTAC;

static
LinkedList dataSetValuesReceivedFrom487B_2;

static
LinkedList dataSetValuesReceivedFrom351_2;

static
LinkedList dataSetValuesReceivedFrom451_2;

static
LinkedList dataSetValuesTo787;

static
LinkedList dataSetValuesTo451_2;

static
LinkedList dataSetValuesTo487B_2;

static
LinkedList dataSetValuesTo351_2;

static void
sigint_handler(int signalId)
{
    running = 0;
}

int updated_RTAC_451_2 = 0;
int updated_651R_2 = 0;
int updated_487B_2 = 0;
int updated_351_2 = 0;
int updated_451_2 = 0;

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
   

    if (MmsValue_getType(values) == MMS_ARRAY) {
        // printf("received binary control command: ");
        printf("received MMS ARRAY\n");

        int values_size = MmsValue_getArraySize(values);

        for (int i=0; i<values_size; i++){
            MmsValue* elementValue = MmsValue_getElement(values, i);

            if (elementValue) {

                if (MmsValue_equals(elementValue, MmsValue_newIntegerFromInt32(1))){
                    // printf("Breaker Closed\n");
                    printf("Value %d\n", MmsValue_toInt32(elementValue));
                }
                else{
                    // printf("Breaker Open\n");
                    printf("Value %d\n", MmsValue_toInt32(elementValue));
                }


                // Update the values of dataSetValuesReceivedFrom651R_2
                // TODO: Can that be done outside the loop with direct assignment somehow?
                // TODO: Shall we also move the if statement somewhere outside the loop?
                if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_651R_2/PRO$CO$BCACSWI2") == 0){
                        
                    LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom651R_2, i);

                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                        updated_651R_2 = 1;
                    }

                    LinkedList_remove(dataSetValuesReceivedFrom651R_2, value);
                    LinkedList_add(dataSetValuesReceivedFrom651R_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
                }
                else if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_451_2/PRO$CO$TEST_3") == 0){
                    printf("VALUES FROM RTAC to 451_2\n");
                    
                    LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFromRTAC, i);

                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                        updated_RTAC_451_2 = 1;
                    }

                    LinkedList_remove(dataSetValuesReceivedFromRTAC, value);
                    LinkedList_add(dataSetValuesReceivedFromRTAC, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));

                    // if( MmsValue_toInt32(elementValue) == 1){
                    //     updated_RTAC_451_2 = 1;
                    // }

                }
                else if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_487B_2/PRO$CO$BCACSWI2") == 0){
                    printf("VALUES FROM 487B\n");

                    LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom487B_2, i);

                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                        updated_487B_2 = 1;
                    }

                    LinkedList_remove(dataSetValuesReceivedFrom487B_2, value);
                    LinkedList_add(dataSetValuesReceivedFrom487B_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
                }
                else if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_351_2/PRO$CO$BCACSWI2") == 0){
                    printf("VALUES FROM 351\n");
                    
                    LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom351_2, i);

                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                        updated_351_2 = 1;
                    }

                    LinkedList_remove(dataSetValuesReceivedFrom351_2, value);
                    LinkedList_add(dataSetValuesReceivedFrom351_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
                }
                else if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_451_2/PRO$CO$BCACSWI2") == 0){

                    printf("VALUES FROM 451\n");

                    LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom451_2, i);

                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                        updated_451_2 = 1;
                    }

                    LinkedList_remove(dataSetValuesReceivedFrom451_2, value);
                    LinkedList_add(dataSetValuesReceivedFrom451_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
                }
            }
        }
    }

    
    // Messages from steps a) and b) to perform c), d) and e) 
    if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_651R_2/PRO$CO$BCACSWI2") == 0
        || strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_487B_2/PRO$CO$BCACSWI2") == 0
        || strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_351_2/PRO$CO$BCACSWI2") == 0){

        if(updated_651R_2 == 1 && updated_487B_2 == 1 && updated_351_2 == 1){
            // Open 21
            LinkedList prev_Val = LinkedList_get(dataSetValuesTo787, 0);
            MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo787, value);
            LinkedList_add(dataSetValuesTo787, MmsValue_newIntegerFromInt32(0));

            // printf("dataSetValuesTo451_2 BEFORE values are: \n");
            // printLinkedList(dataSetValuesTo451_2); 

            // Close 111 and 112
            prev_Val = LinkedList_get(dataSetValuesTo451_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo451_2, value);
            LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(1));

            prev_Val = LinkedList_get(dataSetValuesTo451_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo451_2, value);
            LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(1));
        }
    }

    // Messages from step e) to perform i)
    if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_451_2/PRO$CO$TEST_3") == 0){

        if(updated_RTAC_451_2 == 1){

            printf("dataSetValuesTo487B_2 BEFORE values are: \n");
            printLinkedList(dataSetValuesTo487B_2); 

            // Close 22, 23, 24
            LinkedList prev_Val = LinkedList_get(dataSetValuesTo487B_2, 0);
            MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo487B_2, value);
            LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(1));

            prev_Val = LinkedList_get(dataSetValuesTo487B_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo487B_2, value);
            LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(1));

            prev_Val = LinkedList_get(dataSetValuesTo487B_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo487B_2, value);
            LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(1));

            printf("dataSetValuesTo487B_2 AFTER values are: \n");
            printLinkedList(dataSetValuesTo487B_2); 
        }
    }

    if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_451_2/PRO$CO$BCACSWI2") == 0){

        if(updated_487B_2 == 1){

            printf("dataSetValuesTo351_2 BEFORE values are: \n");
            printLinkedList(dataSetValuesTo351_2);

            // Close 25
            LinkedList prev_Val = LinkedList_get(dataSetValuesTo351_2, 0);
            MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo351_2, value);
            LinkedList_add(dataSetValuesTo351_2, MmsValue_newIntegerFromInt32(1));

            printf("dataSetValuesTo351_2 AFTER values are: \n");
            printLinkedList(dataSetValuesTo351_2);
        }
    }

    // Adds time logging for the "packet"
    char buffer_time[26];
    int millisec;
    struct tm* tm_info;
    struct timeval tv;

    gettimeofday(&tv, NULL);

    // Round to nearest millisec
    millisec = lrint(tv.tv_usec/1000.0);
    // Allow for rounding up to nearest second
    if (millisec>=1000) {
        millisec -=1000;
        tv.tv_sec++;
    }

    tm_info = localtime(&tv.tv_sec);

    strftime(buffer_time, 26, "%Y:%m:%d %H:%M:%S", tm_info);
    printf("At %s.%03d\n", buffer_time, millisec);
}


void *threadedReceiver(void *input)
{
    // Store the value argument passed to this thread
    int myid  = ((struct args_rec*)input)->myid;
    GooseReceiver receiver = ((struct args_rec*)input)->receiver;
  
    if (GooseReceiver_isRunning(receiver)) {
        // ready to receive messages.
        signal(SIGINT, sigint_handler);

        while (running) {
            Thread_sleep(100);
        }
    }
    else {
        printf("Failed to start GOOSE subscriber. Reason can be that the Ethernet interface doesn't exist or root permission are required.\n");
    }
}

void *threadedPublisher(void *input)
{
    // Store the value argument passed to this thread
    int myid  = ((struct args_pub*)input)->myid;
    char *device_name = ((struct args_pub*)input)->device_name;
    GoosePublisher publisher = ((struct args_pub*)input)->publisher;
    GoosePublisher publisher_2 = ((struct args_pub*)input)->publisher_2;
    GoosePublisher publisher_3 = ((struct args_pub*)input)->publisher_3;

    // TODO: The below should be adjusted for each device
    // based on the collected information.

    int i = 0;
    // Intervals in ms
    // int min_interval = 10;
    int min_interval = 4;
    // int min_interval = 500;
    int publish_interval = min_interval;
    // int max_interval = 100;
    int max_interval = 1000;
    // int max_interval = 5000;
    
    // NOTE: Used as a simple condition to increase the StNum
    int max_i = 10;
    int max_i_2 = 30;

    int step_e_done = 0;
    int step_a_done = 0;
    int step_b_done = 0;

    while (1) {
             // Now we also publish based on the defined interval
            if (GoosePublisher_publish(publisher, dataSetValues) == -1 
                // || GoosePublisher_publish(publisher_2, dataSetValuesTo487B_2) == -1 
                || GoosePublisher_publish(publisher_2, dataSetValuesTo787) == -1
                || GoosePublisher_publish(publisher_3, dataSetValuesTo451_2) == -1) {
                    printf("Error sending message!\n");
            }
            printf("Publishing...\n");
            // Thread_sleep(publish_interval);

            // First option 
            // if( i <= 3) {
            //     interval = 2 * interval;
            // }
            // else {
            //     interval = max_interval;
            // }

            // Second option
            // if( i == 0) {
            //     publish_interval = min_interval;
            // }
            // else if( i < 3) {
            //     publish_interval = 2 * publish_interval;
            // }
            // else {
            //     publish_interval = max_interval;
            // }

            // The different Transmit Interval algorithms for each device.
            if (strcmp(device_name, "651R_2") == 0) {

                if( i == 0 || i == 1) {
                    publish_interval = min_interval;
                }
                else if( i == 2) {
                    publish_interval = 2 * publish_interval;
                }
                else {
                    publish_interval = max_interval;
                }
            }
            else if (strcmp(device_name, "RTAC") == 0) {

                if( i == 0) {
                    publish_interval = min_interval;
                }
                else if( i < 3) {
                    publish_interval = 2 * publish_interval;
                }
                else {
                    publish_interval = max_interval;
                }
            }
            else if (strcmp(device_name, "487B_2") == 0) {
                
                if( i == 0 || i == 1) {
                    publish_interval = min_interval;
                }
                else if( i == 2) {
                    publish_interval = 2 * publish_interval;
                }
                else {
                    publish_interval = max_interval;
                }
            }
            else if (strcmp(device_name, "351_2") == 0) {
                
                if( i == 0 || i == 1) {
                    publish_interval = min_interval;
                }
                else if( i == 2) {
                    publish_interval = 2 * publish_interval;
                }
                else {
                    publish_interval = max_interval;
                }
            }
            else if (strcmp(device_name, "451_2") == 0) {

                dataSetValues = dataSetValuesTo487B_2;
                
                if( i == 0 || i == 1) {
                    publish_interval = min_interval;
                }
                else if( i == 2) {
                    publish_interval = 2 * publish_interval;
                }
                else {
                    publish_interval = max_interval;
                }
            }
            
            // .. then us a condition to change something to start from the
            // beginning

            // This could be step a) 
            if (strcmp(device_name, "651R_2") == 0 && i == max_i && step_a_done == 0) {
                printf("=================== STEP A)  ===================");
                LinkedList prev_Val = LinkedList_get(dataSetValues, 0);

                // LinkedList_remove(dataSetValues, prev_Val);
                // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));
               

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                LinkedList_remove(dataSetValues, value);
                LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                GoosePublisher_increaseStNum(publisher);
                publish_interval = min_interval;

                step_a_done = 1;

                // i = 0;
            }

            // This could be step b) 
            if (i == max_i && step_b_done == 0) {

                if ( strcmp(device_name, "487B_2") == 0) {
                    printf("=================== STEP B)  ===================");

                    // Trip 22
                    LinkedList prev_Val = LinkedList_get(dataSetValues, 0);
                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    LinkedList_remove(dataSetValues, value);
                    LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                    // Trip 23
                    LinkedList prev_Val_2 = LinkedList_get(dataSetValues, 1);
                    value = (MmsValue*) LinkedList_getData(prev_Val_2);

                    LinkedList_remove(dataSetValues, value);
                    LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                    // Trip 24
                    LinkedList prev_Val_3 = LinkedList_get(dataSetValues, 0);
                    value = (MmsValue*) LinkedList_getData(prev_Val_3);

                    LinkedList_remove(dataSetValues, value);
                    LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                    GoosePublisher_increaseStNum(publisher);
                    publish_interval = min_interval;

                    step_b_done = 1;

                    // i = 0;
                }
                else if ( strcmp(device_name, "351_2") == 0) {
                    printf("=================== STEP B)  ===================");

                    // Trip 25
                    LinkedList prev_Val = LinkedList_get(dataSetValues, 0);
                    MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                    LinkedList_remove(dataSetValues, value);
                    LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                    GoosePublisher_increaseStNum(publisher);
                    publish_interval = min_interval;

                    step_b_done = 1;

                    // i = 0;
                }
            }

            // This could be step e)
            // TODO: That will be if step e) happens from RTAC --> 651-2?
            // Combined all the events in the single "if block".
            if (strcmp(device_name, "RTAC") == 0 && i == max_i_2 && step_e_done == 0) {

                printf("=================== ISSUE FIXED, RESTORING ( STEP E) ) ===================");
                
                // For RTAC --> 651-2
                // Trip
                LinkedList prev_Val_0 = LinkedList_get(dataSetValues, 0);
                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val_0);

                LinkedList_remove(dataSetValues, value);
                LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));

                // Close
                LinkedList prev_Val_1 = LinkedList_get(dataSetValues, 1);
                value = (MmsValue*) LinkedList_getData(prev_Val_1);

                LinkedList_remove(dataSetValues, value);
                LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                // For RTAC --> 787_2
                prev_Val_0 = LinkedList_get(dataSetValuesTo787, 0);
                
                value = (MmsValue*) LinkedList_getData(prev_Val_0);

                LinkedList_remove(dataSetValuesTo787, value);
                // Close 21
                LinkedList_add(dataSetValuesTo787, MmsValue_newIntegerFromInt32(1));

                // For RTAC --> 451_2
                prev_Val_0 = LinkedList_get(dataSetValuesTo451_2, 0);
                prev_Val_1 = LinkedList_get(dataSetValuesTo451_2, 1);
                
                value = (MmsValue*) LinkedList_getData(prev_Val_0);
                LinkedList_remove(dataSetValuesTo451_2, value);
                // Open 111
                LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(0));

                value = (MmsValue*) LinkedList_getData(prev_Val_1);
                LinkedList_remove(dataSetValuesTo451_2, value);
                // Open 112
                LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(0));

                GoosePublisher_increaseStNum(publisher);
                publish_interval = 0;

                step_e_done = 1;
                // i = 0;
                // return 0;
            }

            i++;

            // NOTE: Not sure if that is really needed.
            if (step_e_done == 1){
                i = 0;
                step_e_done = 0;
            }

            // if (step_b_done == 1){
            //     i = 0;
            //     // step_b_done = 0;
            // }

            // if (step_a_done == 1){
            //     i = 0;
                // step_a_done = 0;
            // }

            Thread_sleep(publish_interval);
    }
}

/* has to be executed as root! */
int
main(int argc, char **argv)
{
    GooseReceiver receiver = GooseReceiver_create();
    GoosePublisher publisher;
    GoosePublisher publisher_2;
    GoosePublisher publisher_3;

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

    char * devices [] = { "RTAC", "651R_2", "787_2", "451_2", "487B_2",  "351_2"};
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
    GooseSubscriber subscriber_2;
    GooseSubscriber subscriber_3;

    if (strcmp(device_name, "RTAC") == 0) 
    {
        printf("GOOSE subscriber RTAC configuration initiated...\n");
        
        // This should be sub for data from 651R_2
        // TODO: We need for the rest of them as well.
        subscriber = GooseSubscriber_create("simple_651R_2/PRO$CO$BCACSWI2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x02};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1002);

        // sub for data from 487B_2
        subscriber_2 = GooseSubscriber_create("simple_487B_2/PRO$CO$BCACSWI2", NULL);
        dstMac[5] = 0x05;
        GooseSubscriber_setDstMac(subscriber_2, dstMac);
        GooseSubscriber_setAppId(subscriber_2, 1005);
        
        subscriber_3 = GooseSubscriber_create("simple_351_2/PRO$CO$BCACSWI2", NULL);
        dstMac[5] = 0x06;
        GooseSubscriber_setDstMac(subscriber_3, dstMac);
        GooseSubscriber_setAppId(subscriber_3, 1006);
        
    } 
    else if (strcmp(device_name, "651R_2") == 0)
    {
        printf("GOOSE subscriber 651R_2 configuration initiated...\n");

        // This should be sub for data from RTAC
        // TODO: We need for the rest of them as well.

        // TODO: Chahnge the below from TEST to something else.
        subscriber = GooseSubscriber_create("simple_651R_2/PRO$CO$TEST", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x01};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1001);
    }
    else if (strcmp(device_name, "787_2") == 0)
    {
        printf("GOOSE subscriber 787_2 configuration initiated...\n");

        // TODO: After testing rename this to just "subscriber"
        subscriber = GooseSubscriber_create("simple_787_2/PRO$CO$TEST_2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x03};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1003);
    }
    else if (strcmp(device_name, "451_2") == 0)
    {
        printf("GOOSE 451_2 configuration initiated...\n");

        // TODO: After testing rename this to just "subscriber"
        subscriber = GooseSubscriber_create("simple_451_2/PRO$CO$TEST_3", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x04};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1004);
    }
    else if (strcmp(device_name, "487B_2") == 0)
    {
        printf("GOOSE 487B_2 configuration initiated...\n");

        // TODO: After testing rename this to just "subscriber"
        subscriber = GooseSubscriber_create("simple_451_2/PRO$CO$BCACSWI2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x07};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1007);
    }
    else if (strcmp(device_name, "351_2") == 0)
    {
        printf("GOOSE 351_2 configuration initiated...\n");

        // TODO: After testing rename this to just "subscriber"
        subscriber = GooseSubscriber_create("simple_487B_2/PRO$CO$BCACSWI2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x05};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1005);
    }
    else
    {
        printf("No device supported, exiting...\n");
        return 1;
    }

    //.. and now the publisher
    dataSetValues = LinkedList_create();

    dataSetValuesReceivedFrom651R_2 = LinkedList_create();
    dataSetValuesReceivedFromRTAC = LinkedList_create();
    dataSetValuesReceivedFrom487B_2 = LinkedList_create();
    dataSetValuesReceivedFrom451_2 = LinkedList_create();
    dataSetValuesReceivedFrom351_2 = LinkedList_create();

    dataSetValuesTo787 = LinkedList_create();
    dataSetValuesTo451_2 = LinkedList_create();
    dataSetValuesTo487B_2 = LinkedList_create();
    dataSetValuesTo351_2 = LinkedList_create();

    CommParameters gooseCommParameters;
    CommParameters gooseCommParameters_2;
    CommParameters gooseCommParameters_3;
    
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
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(true));

        // Trip command (for device No ?) 0/1 NoTrip/Trip.
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // NOTE: Disable for now might be enabled later.
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(false));

        // The initial values of the retained dataSetValuesReceivedFrom651R_2
        // Breaker status (for device No ?) 0/1 or Open/Close.
        LinkedList_add(dataSetValuesReceivedFrom651R_2,  MmsValue_newIntegerFromInt32(0));

        gooseCommParameters.appId = 1001;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x01;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;

        // For the RTAC --> 787 comms
        // Should be CLOSED initially
        LinkedList_add(dataSetValuesTo787,  MmsValue_newIntegerFromInt32(1));

        // TODO: Can we write those asisgnment to that dstAddress array in a better way?
        gooseCommParameters_2.appId = 1003;
        gooseCommParameters_2.dstAddress[0] = 0x01;
        gooseCommParameters_2.dstAddress[1] = 0x0c;
        gooseCommParameters_2.dstAddress[2] = 0xcd;
        gooseCommParameters_2.dstAddress[3] = 0x01;
        gooseCommParameters_2.dstAddress[4] = 0x00;
        gooseCommParameters_2.dstAddress[5] = 0x03;
        gooseCommParameters_2.vlanId = 0;
        gooseCommParameters_2.vlanPriority = 4;


        // For the RTAC -->  451_2 comms
        // This is for the 111
        // Should be OPEN initially
        LinkedList_add(dataSetValuesTo451_2,  MmsValue_newIntegerFromInt32(0));
        // This is for the 112
        // Should be OPEN initially
        LinkedList_add(dataSetValuesTo451_2,  MmsValue_newIntegerFromInt32(0));

        // TODO: Can we write those asisgnment to that dstAddress array in a better way?
        gooseCommParameters_3.appId = 1004;
        gooseCommParameters_3.dstAddress[0] = 0x01;
        gooseCommParameters_3.dstAddress[1] = 0x0c;
        gooseCommParameters_3.dstAddress[2] = 0xcd;
        gooseCommParameters_3.dstAddress[3] = 0x01;
        gooseCommParameters_3.dstAddress[4] = 0x00;
        gooseCommParameters_3.dstAddress[5] = 0x04;
        gooseCommParameters_3.vlanId = 0;
        gooseCommParameters_3.vlanPriority = 4;

        
        // Trip command (for device No 487B_2) 0/1 NoTrip/Trip.
        LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));

        // Trip command (for device No 351_2) 0/1 NoTrip/Trip.
        LinkedList_add(dataSetValuesReceivedFrom351_2,  MmsValue_newIntegerFromInt32(0));

        LinkedList_add(dataSetValuesTo351_2,  MmsValue_newIntegerFromInt32(0));
    } 
    // NOTE: JUST FOR TESTING
    else if (strcmp(device_name, "651R_2") == 0)
    // if (strcmp(device_name, "RTAC") == 0)
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

        // 112
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // 111
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));

        gooseCommParameters.appId = 1007;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x07;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;

        LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(0));

        // RTAC to 451-2
        LinkedList_add(dataSetValuesReceivedFromRTAC, MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesReceivedFromRTAC, MmsValue_newIntegerFromInt32(0));
        
    }
    else if (strcmp(device_name, "487B_2") == 0)
    {
        printf("GOOSE publisher 487B_2 configuration initiated...\n");
        
        // Trip status (for device No ?) 0/1 or NoTrip/Trip.
        // 22
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // 23
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // 24
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(true));

        // Trip command (for device No ?) Trip/NoTrip.
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
         // NOTE: Disable for now might be enabled later.
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(false));
        
        LinkedList_add(dataSetValuesReceivedFrom451_2, MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesReceivedFrom451_2, MmsValue_newIntegerFromInt32(0));

        gooseCommParameters.appId = 1005;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x05;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;

        // NOTE: No need for 487B to receive message from 351 (for now?)
        // LinkedList_add(dataSetValuesReceivedFrom351_2, MmsValue_newIntegerFromInt32(0));

        LinkedList_add(dataSetValuesTo351_2, MmsValue_newIntegerFromInt32(0));
    }
    else if (strcmp(device_name, "351_2") == 0)
    {
        printf("GOOSE publisher 351_2 configuration initiated...\n");

        // Trip status (for device No ?) 0/1 or NoTrip/Trip.
        // 25
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(true));

        // Trip command (for device No ?) Trip/NoTrip.
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
        // NOTE: Disable for now might be enabled later.
        // LinkedList_add(dataSetValues, MmsValue_newBoolean(false));

        // Trip command (for device No 351_2) 0/1 NoTrip/Trip.
        LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));
        LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));

        gooseCommParameters.appId = 1006;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x06;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;
    }
    else
    {
        printf("No device supported, exiting...\n");
        return 1;
    }

    publisher = GoosePublisher_create(&gooseCommParameters, interface);
    publisher_2 = GoosePublisher_create(&gooseCommParameters_2, interface);
    publisher_3 = GoosePublisher_create(&gooseCommParameters_3, interface);
    // publisher = GoosePublisher_create(&gooseCommParameters, "eth0");

    int i = 0;
    uint32_t prev_stNum = 0; 

    if (publisher) {
        GoosePublisher_setConfRev(publisher, 1);
        GoosePublisher_setTimeAllowedToLive(publisher, 500);

        if (strcmp(device_name, "RTAC") == 0) 
        {
            printf("RTAC GOOSE configuration initiated...\n");

            GoosePublisher_setGoCbRef(publisher, "simple_651R_2/PRO$CO$TEST");
            GoosePublisher_setDataSetRef(publisher, "simple_651R_2/PRO$TEST_DataSet");

            GoosePublisher_setGoCbRef(publisher_2, "simple_787_2/PRO$CO$TEST_2");
            GoosePublisher_setDataSetRef(publisher_2, "simple_787_2/PRO$TEST_DataSet_2");

            GoosePublisher_setGoCbRef(publisher_3, "simple_451_2/PRO$CO$TEST_3");
            GoosePublisher_setDataSetRef(publisher_3, "simple_451_2/PRO$TEST_DataSet_3");
        } 
        // NOTE: JUST FOR TESTING
        else if (strcmp(device_name, "651R_2") == 0)
        // if (strcmp(device_name, "RTAC") == 0)
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

            GoosePublisher_setGoCbRef(publisher, "simple_451_2/PRO$CO$BCACSWI2");
            GoosePublisher_setDataSetRef(publisher, "simple_451_2/PRO$BCACSWI2_DataSet");
        }
        else if (strcmp(device_name, "487B_2") == 0)
        {
            printf("487B_2 GOOSE configuration initiated...\n");

            GoosePublisher_setGoCbRef(publisher, "simple_487B_2/PRO$CO$BCACSWI2");
            GoosePublisher_setDataSetRef(publisher, "simple_487B_2/PRO$BCACSWI2_DataSet");
        }
        else if (strcmp(device_name, "351_2") == 0)
        {
            printf("351_2 GOOSE configuration initiated...\n");

            GoosePublisher_setGoCbRef(publisher, "simple_351_2/PRO$CO$BCACSWI2");
            GoosePublisher_setDataSetRef(publisher, "simple_351_2/PRO$BCACSWI2_DataSet");
        }
        else
        {
            printf("No device supported, exiting...\n");
            return 1;
        }
    }



    GooseSubscriber_setListener(subscriber, gooseListener, NULL);
    GooseReceiver_addSubscriber(receiver, subscriber);

    if (strcmp(device_name, "RTAC") == 0) {
        GooseSubscriber_setListener(subscriber_2, gooseListener, NULL);
        GooseSubscriber_setListener(subscriber_3, gooseListener, NULL);

        GooseReceiver_addSubscriber(receiver, subscriber_2);
        GooseReceiver_addSubscriber(receiver, subscriber_3);
    }
    // else  if (strcmp(device_name, "487B_2") == 0) {
    //     printf("487B_2 second subscriber\n");
    //     GooseSubscriber_setListener(subscriber_2, gooseListener, NULL);
    //     // GooseSubscriber_setListener(subscriber_3, gooseListener, NULL);

    //     GooseReceiver_addSubscriber(receiver, subscriber_2);
    //     // GooseReceiver_addSubscriber(receiver, subscriber_3);
    // }
    
    
   

    GooseReceiver_start(receiver);

    pthread_t tid_rec;
    struct args_rec *rec_struct = (struct args_rec *)malloc(sizeof(struct args_rec));
    rec_struct->receiver = receiver;
    rec_struct->myid = tid_rec;

    pthread_t tid_pub;
    struct args_pub *pub_struct = (struct args_pub *)malloc(sizeof(struct args_pub));
    pub_struct->device_name = device_name;
    pub_struct->publisher = publisher;
    pub_struct->publisher_2 = publisher_2;
    pub_struct->publisher_3 = publisher_3;
    pub_struct->myid = tid_pub;

    pthread_create(&tid_rec, NULL, threadedReceiver, (void *)rec_struct);
    pthread_create(&tid_pub, NULL, threadedPublisher, (void *)pub_struct);

    sleep(1000000);

    GoosePublisher_destroy(publisher);

    GooseReceiver_stop(receiver);

    GooseReceiver_destroy(receiver);

}