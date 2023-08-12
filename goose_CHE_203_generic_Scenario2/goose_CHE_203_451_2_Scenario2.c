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

static int running = 1;

static 
LinkedList dataSetValues;

static
LinkedList dataSetValuesReceivedFromRTAC;

static
LinkedList dataSetValuesTo351_2;

static
LinkedList dataSetValuesTo487B_2;

int updated_451_2 = 0;

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

static void
sigint_handler(int signalId)
{
    running = 0;
}

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

            if (elementValue && strcmp(GooseSubscriber_getGoCbRef(subscriber), "simple_451_2/PRO$CO$TEST_3") == 0) {
                printf("VALUES FROM RTAC\n");

                LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFromRTAC, i);

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                    updated_451_2 = 1;
                }

                LinkedList_remove(dataSetValuesReceivedFromRTAC, value);
                LinkedList_add(dataSetValuesReceivedFromRTAC, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
            }
        }
    }
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
        printf("Failed to start GOOSE subscriber. Reason can be that the Ethernet interface doesn't exist or root permission is required.\n");
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

    int i = 0;
    // Intervals in ms
    int min_interval = 4;
    int publish_interval = min_interval;
    int max_interval = 1000;
    
    // NOTE: Used as a simple condition to increase the StNum
    int max_i = 30;

    while (1) {

        if (GoosePublisher_publish(publisher, dataSetValuesTo487B_2) == -1){
            printf("Error sending message!\n");
        }
        printf("Publishing...\n");

       if( i == 0 || i == 1) {
            GoosePublisher_setTimeAllowedToLive(publisher, 2 * min_interval);
            publish_interval = min_interval;
        }
        else if( i == 2) {
            GoosePublisher_setTimeAllowedToLive(publisher, 2 * min_interval);
            publish_interval = 2 * publish_interval;
        }
        else {
            GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
            publish_interval = max_interval;
        }

        i++;

        if (updated_451_2 == 1){
            
            printf("=================== STEP F)  ===================");
            
            int values_size = LinkedList_size(dataSetValuesTo487B_2);

            for (int i=0; i<values_size; i++){

                // LinkedList prev_Val = LinkedList_get(dataSetValuesToRTAC, i);
                LinkedList prev_Val = LinkedList_get(dataSetValuesTo487B_2, 0);

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                LinkedList_remove(dataSetValuesTo487B_2, value);
                LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(1));
            }

            GoosePublisher_increaseStNum(publisher);
            publish_interval = min_interval;

            updated_451_2 = 0;

            i = 0;
        }

        // TODO: Need to check for the received values from 451_2 
        // and then change those for 351_2

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

    if (argc > 1) {
        interface = argv[1];
        printf("Set interface id: %s\n",  interface);
        
        GooseReceiver_setInterfaceId(receiver, interface);
    }
    else {
        // printf("Using interface eth0\n");
        printf("Not enough parameters, exiting...\n");
        return 1;
    }

    // First let's setup the subscriber
    GooseSubscriber subscriber;
    GooseSubscriber subscriber_2;
    GooseSubscriber subscriber_3;

    printf("GOOSE subscriber 451_2 configuration initiated...\n");
        
    // This should be sub for data from 451_2
    subscriber = GooseSubscriber_create("simple_451_2/PRO$CO$TEST_3", NULL);
    uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x04};
    GooseSubscriber_setDstMac(subscriber, dstMac);
    GooseSubscriber_setAppId(subscriber, 1004);
    
    GooseSubscriber_setListener(subscriber, gooseListener, NULL);
    GooseReceiver_addSubscriber(receiver, subscriber);

    //.. and now the publisher
    dataSetValues = LinkedList_create();

    dataSetValuesReceivedFromRTAC = LinkedList_create();

    dataSetValuesTo487B_2 = LinkedList_create();

    CommParameters gooseCommParameters;
    CommParameters gooseCommParameters_2;
    CommParameters gooseCommParameters_3;

    printf("GOOSE publisher 451_2 configuration initiated...\n");

    // Breaker status (for device No ?) 0/1 or Open/Close.
    // Should be CLOSED initially
    // For 22, 23, 24
    LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesTo487B_2, MmsValue_newIntegerFromInt32(0));

    // Breaker status (for device No ?) 0/1 or Open/Close.
    LinkedList_add(dataSetValuesReceivedFromRTAC,  MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesReceivedFromRTAC,  MmsValue_newIntegerFromInt32(0));
    
    // For 487B_2
    gooseCommParameters.appId = 1009;
    memcpy(gooseCommParameters.dstAddress, (unsigned char[]) {0x01,0x0c,0xcd,0x01,0x00,0x09 }, 
        sizeof gooseCommParameters.dstAddress);

    gooseCommParameters.vlanId = 0;
    gooseCommParameters.vlanPriority = 4;

    publisher = GoosePublisher_create(&gooseCommParameters, interface);

    GoosePublisher_setGoCbRef(publisher, "simple_451_2/PRO$CO$BCACSWI2");
    GoosePublisher_setDataSetRef(publisher, "simple_451_2/PRO$BCACSWI2_DataSet");


    pthread_t tid_rec;
    struct args_rec *rec_struct = (struct args_rec *)malloc(sizeof(struct args_rec));
    rec_struct->receiver = receiver;
    rec_struct->myid = tid_rec;

    pthread_create(&tid_rec, NULL, threadedReceiver, (void *)rec_struct);
    GooseReceiver_start(receiver);

    pthread_t tid_pub;
    struct args_pub *pub_struct = (struct args_pub *)malloc(sizeof(struct args_pub));
    pub_struct->device_name = "451_2";
    pub_struct->publisher = publisher;
    pub_struct->publisher_2 = publisher_2;
    pub_struct->publisher_3 = publisher_3;
    pub_struct->myid = tid_pub;
    
    // TODO: Can we launch those 3 publishers as separate threads
    // if there are no problems with shared data?
    pthread_create(&tid_pub, NULL, threadedPublisher, (void *)pub_struct);

    sleep(1000000);

    GoosePublisher_destroy(publisher);
    GoosePublisher_destroy(publisher_2);
    GoosePublisher_destroy(publisher_3);

    GooseReceiver_stop(receiver);

    GooseReceiver_destroy(receiver);
}
