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
LinkedList dataSetValuesReceivedFrom451_2;

static
LinkedList dataSetValuesTo351_2;

static
LinkedList dataSetValuesToRTAC;

int updated_451_2 = 0;

int code_runs = 0;

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
    // printf("GOOSE event:\n");
    // printf("  stNum: %u sqNum: %u\n", GooseSubscriber_getStNum(subscriber),
    //         GooseSubscriber_getSqNum(subscriber));
    // printf("  timeToLive: %u\n", GooseSubscriber_getTimeAllowedToLive(subscriber));

    uint64_t timestamp = GooseSubscriber_getTimestamp(subscriber);

    // printf("  timestamp: %u.%u\n", (uint32_t) (timestamp / 1000), (uint32_t) (timestamp % 1000));
    // printf("  message is %s\n", GooseSubscriber_isValid(subscriber) ? "valid" : "INVALID");

    MmsValue* values = GooseSubscriber_getDataSetValues(subscriber);

    char buffer[1024];

    MmsValue_printToBuffer(values, buffer, 1024);

    // printf("  allData: %s\n", buffer);

    if (MmsValue_getType(values) == MMS_ARRAY) {


        int values_size = MmsValue_getArraySize(values);

        for (int i=0; i<values_size; i++){
            MmsValue* elementValue = MmsValue_getElement(values, i);

            if (elementValue && strcmp(GooseSubscriber_getGoCbRef(subscriber), "SEL_451_2/LLN0$GO$GooseDSet1") == 0) {
                // printf("VALUES FROM 451_2\n");

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

void *threadedReceiver(void *input)
{
    // Store the value argument passed to this thread
    int myid  = ((struct args_rec*)input)->myid;
    GooseReceiver receiver = ((struct args_rec*)input)->receiver;
  
    if (GooseReceiver_isRunning(receiver)) {
        // ready to receive messages.
        signal(SIGINT, sigint_handler);

        while (running) {
            // Thread_sleep(100);
            Thread_sleep(50);
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
    int min_interval = 30;
    int publish_interval = min_interval;
    int max_interval = 100;

    int max_i = 30;

    int step_b_done = 0;

    while (1) {

        if (GoosePublisher_publish(publisher, dataSetValuesToRTAC) == -1 ||
            GoosePublisher_publish(publisher_2, dataSetValuesTo351_2) == -1) {
            printf("Error sending message!\n");
        }
        printf("Publishing...\n");

       if( i == 0 || i == 1) {
            GoosePublisher_setTimeAllowedToLive(publisher, 3 * min_interval);
            GoosePublisher_setTimeAllowedToLive(publisher_2, 3 * min_interval);
            publish_interval = min_interval;
        }
        else if( i == 2) {
            GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
            GoosePublisher_setTimeAllowedToLive(publisher_2, 2 * max_interval);
            publish_interval = 2 * publish_interval;
        }
        else {
            GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
            GoosePublisher_setTimeAllowedToLive(publisher_2, 2 * max_interval);
            publish_interval = max_interval;
        }

        i++;

        if (i == max_i && step_b_done == 0){
            
            printf("=================== STEP B)  ===================");
            
            int values_size = LinkedList_size(dataSetValuesToRTAC);

            for (int i=0; i<values_size; i++){

                // LinkedList prev_Val = LinkedList_get(dataSetValuesToRTAC, i);
                LinkedList prev_Val = LinkedList_get(dataSetValuesToRTAC, 0);

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                LinkedList_remove(dataSetValuesToRTAC, value);
                LinkedList_add(dataSetValuesToRTAC, MmsValue_newIntegerFromInt32(0));
            }

            GoosePublisher_increaseStNum(publisher);
            publish_interval = min_interval;

            step_b_done = 1;

            i = 0;
        }

        if (updated_451_2 == 1) {
            
            LinkedList prev_Val = LinkedList_get(dataSetValuesTo351_2, 0);

            MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

            LinkedList_remove(dataSetValuesTo351_2, value);
            LinkedList_add(dataSetValuesTo351_2, MmsValue_newIntegerFromInt32(1));

        
            GoosePublisher_increaseStNum(publisher_2);
            publish_interval = min_interval;
            
            updated_451_2 = 0;
            
            i = 0;
        }

        Thread_sleep(publish_interval);

        code_runs++;
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
        printf("Not enough parameters, exiting...\n");
        return 1;
    }

    // First let's setup the subscriber
    GooseSubscriber subscriber;
    GooseSubscriber subscriber_2;
    GooseSubscriber subscriber_3;

    printf("GOOSE subscriber 487B_2 configuration initiated...\n");
        
    // This should be sub for data from 451_2
    subscriber = GooseSubscriber_create("SEL_451_2/LLN0$GO$GooseDSet1", NULL);
    uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x09};
    GooseSubscriber_setDstMac(subscriber, dstMac);
    GooseSubscriber_setAppId(subscriber, 1009);
    
    GooseSubscriber_setListener(subscriber, gooseListener, NULL);
    GooseReceiver_addSubscriber(receiver, subscriber);

    //.. and now the publisher
    dataSetValues = LinkedList_create();

    dataSetValuesReceivedFrom451_2 = LinkedList_create();

    dataSetValuesTo351_2 = LinkedList_create();
    dataSetValuesToRTAC = LinkedList_create();

    CommParameters gooseCommParameters;
    CommParameters gooseCommParameters_2;
    CommParameters gooseCommParameters_3;

    printf("GOOSE publisher 487B_2 configuration initiated...\n");

    // Breaker status (for device No ?) 0/1 or Open/Close.
    // Should be CLOSED initially
    LinkedList_add(dataSetValuesTo351_2, MmsValue_newIntegerFromInt32(1));

    // For 22, 23, 24 
    LinkedList_add(dataSetValuesToRTAC, MmsValue_newIntegerFromInt32(1));
    LinkedList_add(dataSetValuesToRTAC, MmsValue_newIntegerFromInt32(1));
    LinkedList_add(dataSetValuesToRTAC, MmsValue_newIntegerFromInt32(1));

    // Breaker status (for device No ?) 0/1 or Open/Close.
    LinkedList_add(dataSetValuesReceivedFrom451_2,  MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesReceivedFrom451_2,  MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesReceivedFrom451_2,  MmsValue_newIntegerFromInt32(0));
    
    // For RTAC
    gooseCommParameters.appId = 1005;
    memcpy(gooseCommParameters.dstAddress, (unsigned char[]) {0x01,0x0c,0xcd,0x01,0x00,0x05 }, 
        sizeof gooseCommParameters.dstAddress);

    gooseCommParameters.vlanId = 0;
    gooseCommParameters.vlanPriority = 4;

    // For 351_2
    gooseCommParameters_2.appId = 1010;
    memcpy(gooseCommParameters_2.dstAddress, (unsigned char[]) {0x01,0x0c,0xcd,0x01,0x00,0x10 }, 
        sizeof gooseCommParameters_2.dstAddress);

    gooseCommParameters_2.vlanId = 0;
    gooseCommParameters_2.vlanPriority = 4;


    publisher = GoosePublisher_create(&gooseCommParameters, interface);
    publisher_2 = GoosePublisher_create(&gooseCommParameters_2, interface);

    // GoosePublisher_setGoCbRef(publisher, "simple_487B_2/PRO$CO$BCACSWI2");
    GoosePublisher_setGoCbRef(publisher, "SEL_487B_2/LLN0$GO$GooseDSet1");
    // GoosePublisher_setDataSetRef(publisher, "simple_487B_2/PRO$BCACSWI2_DataSet");
    GoosePublisher_setDataSetRef(publisher, "SEL_487B_2/LLN0$GooseDSet1");

    // GoosePublisher_setGoCbRef(publisher_2, "simple_487B_2/PRO$CO$BCACSWI2_2");
    GoosePublisher_setGoCbRef(publisher_2, "SEL_487B_2/LLN0$GO$GooseDSet2");
    // GoosePublisher_setDataSetRef(publisher_2, "simple_487B_2/PRO$BCACSWI2_2_DataSet");
    GoosePublisher_setDataSetRef(publisher_2, "SEL_487B_2/LLN0$GooseDSet2");


    pthread_t tid_rec;
    struct args_rec *rec_struct = (struct args_rec *)malloc(sizeof(struct args_rec));
    rec_struct->receiver = receiver;
    rec_struct->myid = tid_rec;

    pthread_create(&tid_rec, NULL, threadedReceiver, (void *)rec_struct);
    GooseReceiver_start(receiver);

    pthread_t tid_pub;
    struct args_pub *pub_struct = (struct args_pub *)malloc(sizeof(struct args_pub));
    pub_struct->device_name = "487B_2";
    pub_struct->publisher = publisher;
    pub_struct->publisher_2 = publisher_2;
    pub_struct->publisher_3 = publisher_3;
    pub_struct->myid = tid_pub;

    sleep(3);
    
    
    pthread_create(&tid_pub, NULL, threadedPublisher, (void *)pub_struct);


    while(code_runs < 200){
        sleep(1);
    }

    GoosePublisher_destroy(publisher);
    GoosePublisher_destroy(publisher_2);
    GoosePublisher_destroy(publisher_3);

    GooseReceiver_stop(receiver);

    GooseReceiver_destroy(receiver);
}
