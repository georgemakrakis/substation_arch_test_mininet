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
LinkedList dataSetValuesReceivedFrom651R_2;

static
LinkedList dataSetValuesReceivedFromRTAC;

static
LinkedList dataSetValuesReceivedFrom351_2;

static
LinkedList dataSetValuesReceivedFrom487B_2;


static
LinkedList dataSetValuesTo787;

static
LinkedList dataSetValuesTo451_2;

static
LinkedList dataSetValuesTo487B_2;

static
LinkedList dataSetValuesTo651R_2;

int updated_651R_2 = 0;
int updated_487B_2 = 0;
int updated_351_2 = 0;

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
        printf("received MMS ARRAY\n");

        int values_size = MmsValue_getArraySize(values);

        for (int i=0; i<values_size; i++){
            MmsValue* elementValue = MmsValue_getElement(values, i);

            if (elementValue && strcmp(GooseSubscriber_getGoCbRef(subscriber), "SEL_651R_2/LLN0$GO$GooseDSet1") == 0) {
                printf("VALUES FROM 651R_2\n");

                LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom651R_2, i);

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                    updated_651R_2 = 1;
                }

                LinkedList_remove(dataSetValuesReceivedFrom651R_2, value);
                LinkedList_add(dataSetValuesReceivedFrom651R_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
            }
            else if (elementValue && strcmp(GooseSubscriber_getGoCbRef(subscriber), "SEL_487B_2/LLN0$GO$GooseDSet1") == 0) {
                printf("VALUES FROM 487B_2\n");

                LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom487B_2, i);

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                    updated_487B_2 = 1;
                }

                LinkedList_remove(dataSetValuesReceivedFrom487B_2, value);
                LinkedList_add(dataSetValuesReceivedFrom487B_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
            }
              else if (elementValue && strcmp(GooseSubscriber_getGoCbRef(subscriber), "SEL_351_2/LLN0$GO$GooseDSet1") == 0) {
                printf("VALUES FROM 351_2\n");

                LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom351_2, i);

                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                    updated_351_2 = 1;
                }

                LinkedList_remove(dataSetValuesReceivedFrom351_2, value);
                LinkedList_add(dataSetValuesReceivedFrom351_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
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
    int min_interval = 30;
    int publish_interval = min_interval;
    int max_interval = 100;

    int max_i_2 = 50;

    int step_e_done = 0;

    while (1) {

         if (GoosePublisher_publish(publisher, dataSetValuesTo651R_2) == -1 
                || GoosePublisher_publish(publisher_2, dataSetValuesTo787) == -1
                || GoosePublisher_publish(publisher_3, dataSetValuesTo451_2) == -1){
                    // || (publisher_2  != NULL && GoosePublisher_publish(publisher_2, dataSetValuesTo487B_2) == -1)) {
                    printf("Error sending message!\n");
        }
        printf("Publishing...\n");

        if (i == 0 && publish_interval < max_interval) {
                publish_interval = min_interval;
                GoosePublisher_setTimeAllowedToLive(publisher, 3 * max_interval);
                GoosePublisher_setTimeAllowedToLive(publisher_2, 3 * max_interval);
                GoosePublisher_setTimeAllowedToLive(publisher_3, 3 * max_interval);
        }
        else if (i != 0 && publish_interval < max_interval){
            publish_interval = 2 * publish_interval;
            if ( publish_interval >  max_interval){
                publish_interval = max_interval;
                GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                GoosePublisher_setTimeAllowedToLive(publisher_2, 2 * max_interval);
                GoosePublisher_setTimeAllowedToLive(publisher_3, 2 * max_interval);
            }
            else {
                GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                GoosePublisher_setTimeAllowedToLive(publisher_2, 3 * publish_interval);
                GoosePublisher_setTimeAllowedToLive(publisher_3, 3 * publish_interval);
            }
        }
        else if (i != 0 && publish_interval >= max_interval){
            publish_interval = max_interval;
            GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
            GoosePublisher_setTimeAllowedToLive(publisher_2, 2 * max_interval);
            GoosePublisher_setTimeAllowedToLive(publisher_3, 2 * max_interval);
        } 

        i++;

        // TODO: Need to add condition that will initiate step j)

        if(i == max_i_2 && step_e_done == 0) {
            printf("=================== ISSUE FIXED, RESTORING ( STEP J) ) ===================\n");

            // Close HV2

            LinkedList prev_Val = LinkedList_get(dataSetValuesTo651R_2, 0);
            MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo651R_2, value);
            LinkedList_add(dataSetValuesTo651R_2, MmsValue_newIntegerFromInt32(1));
            
            // Close 21
            prev_Val = LinkedList_get(dataSetValuesTo787, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo787, value);
            LinkedList_add(dataSetValuesTo787, MmsValue_newIntegerFromInt32(1));

            // Open 111 and 112
            prev_Val = LinkedList_get(dataSetValuesTo451_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo451_2, value);
            LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(0));

            prev_Val = LinkedList_get(dataSetValuesTo451_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo451_2, value);
            LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(0));

            GoosePublisher_increaseStNum(publisher);
            GoosePublisher_increaseStNum(publisher_2);
            GoosePublisher_increaseStNum(publisher_3);

            publish_interval = min_interval;

            i = 0;
            step_e_done = 1;
        }

        if (updated_651R_2 == 1 && updated_487B_2 == 1 && updated_351_2 == 1){
            
            printf("=================== STEPS C) D) E) ===================\n");

            // Open 21
            LinkedList prev_Val = LinkedList_get(dataSetValuesTo787, 0);
            MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo787, value);
            LinkedList_add(dataSetValuesTo787, MmsValue_newIntegerFromInt32(0));

            // Close 111 and 112
            prev_Val = LinkedList_get(dataSetValuesTo451_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo451_2, value);
            LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(1));

            prev_Val = LinkedList_get(dataSetValuesTo451_2, 0);
            value = (MmsValue*) LinkedList_getData(prev_Val);
            LinkedList_remove(dataSetValuesTo451_2, value);
            LinkedList_add(dataSetValuesTo451_2, MmsValue_newIntegerFromInt32(1));

            GoosePublisher_increaseStNum(publisher_2);
            GoosePublisher_increaseStNum(publisher_3);

            updated_651R_2 = 0;
            updated_487B_2 = 0;
            updated_351_2 = 0;

            publish_interval = min_interval;

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

    printf("GOOSE subscriber RTAC configuration initiated...\n");
        
    // This should be sub for data from 651R_2
    subscriber = GooseSubscriber_create("SEL_651R_2/LLN0$GO$GooseDSet1", NULL);
    uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x02};
    GooseSubscriber_setDstMac(subscriber, dstMac);
    GooseSubscriber_setAppId(subscriber, 1002);

    // sub for data from 487B_2
    subscriber_2 = GooseSubscriber_create("SEL_487B_2/LLN0$GO$GooseDSet1", NULL);
    dstMac[5] = 0x05;
    GooseSubscriber_setDstMac(subscriber_2, dstMac);
    GooseSubscriber_setAppId(subscriber_2, 1005);
    
    // sub for data from 351_2
    subscriber_3 = GooseSubscriber_create("SEL_351_2/LLN0$GO$GooseDSet1", NULL);
    dstMac[5] = 0x06;
    GooseSubscriber_setDstMac(subscriber_3, dstMac);
    GooseSubscriber_setAppId(subscriber_3, 1006);

    GooseSubscriber_setListener(subscriber, gooseListener, NULL);
    GooseReceiver_addSubscriber(receiver, subscriber);

    GooseSubscriber_setListener(subscriber_2, gooseListener, NULL);
    GooseReceiver_addSubscriber(receiver, subscriber_2);

    GooseSubscriber_setListener(subscriber_3, gooseListener, NULL);
    GooseReceiver_addSubscriber(receiver, subscriber_3);

    //.. and now the publisher
    dataSetValues = LinkedList_create();

    dataSetValuesReceivedFrom651R_2 = LinkedList_create();
    dataSetValuesReceivedFrom487B_2 = LinkedList_create();
    dataSetValuesReceivedFrom351_2 = LinkedList_create();

    dataSetValuesTo787 = LinkedList_create();
    dataSetValuesTo451_2 = LinkedList_create();
    dataSetValuesTo651R_2 = LinkedList_create();

    CommParameters gooseCommParameters;
    CommParameters gooseCommParameters_2;
    CommParameters gooseCommParameters_3;

    printf("GOOSE publisher RTAC configuration initiated...\n");

    // Breaker status (for device No ?) 0/1 or Open/Close.
    // Should be CLOSED initially
    LinkedList_add(dataSetValuesTo651R_2, MmsValue_newIntegerFromInt32(1));

    // The initial values of the retained dataSetValuesReceivedFrom651R_2
    // Breaker status (for device No ?) 0/1 or Open/Close.
    LinkedList_add(dataSetValuesReceivedFrom651R_2,  MmsValue_newIntegerFromInt32(0));

    gooseCommParameters.appId = 1001;
    memcpy(gooseCommParameters.dstAddress, (unsigned char[]) {0x01,0x0c,0xcd,0x01,0x00,0x01 }, 
        sizeof gooseCommParameters.dstAddress);

    gooseCommParameters.vlanId = 0;
    gooseCommParameters.vlanPriority = 4;

    // For the RTAC --> 787 comms
    // Should be CLOSED initially
    LinkedList_add(dataSetValuesTo787,  MmsValue_newIntegerFromInt32(1));
    // TODO: Below should be changed if we have 3-phase breaker

    gooseCommParameters_2.appId = 1003;
    memcpy(gooseCommParameters_2.dstAddress, (unsigned char[]) {0x01,0x0c,0xcd,0x01,0x00,0x03 }, 
        sizeof gooseCommParameters_2.dstAddress);
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
   memcpy(gooseCommParameters_3.dstAddress, (unsigned char[]) {0x01,0x0c,0xcd,0x01,0x00,0x04 }, 
        sizeof gooseCommParameters_3.dstAddress);
    gooseCommParameters_3.vlanId = 0;
    gooseCommParameters_3.vlanPriority = 4;
    
    // For device No 487B_2 0/1 or Open/Close for lines 22-24.
    LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));
    LinkedList_add(dataSetValuesReceivedFrom487B_2,  MmsValue_newIntegerFromInt32(0));

    // For device No 351_2 0/1 or Open/Close for line 25.
    LinkedList_add(dataSetValuesReceivedFrom351_2,  MmsValue_newIntegerFromInt32(0));

    publisher = GoosePublisher_create(&gooseCommParameters, interface);
    publisher_2 = GoosePublisher_create(&gooseCommParameters_2, interface);
    publisher_3 = GoosePublisher_create(&gooseCommParameters_3, interface);

    // GoosePublisher_setGoCbRef(publisher, "simple_651R_2/PRO$CO$TEST");
    GoosePublisher_setGoCbRef(publisher, "SEL_RTAC/LLN0$GO$GooseDSet1");
    // GoosePublisher_setDataSetRef(publisher, "simple_651R_2/PRO$TEST_DataSet");
    GoosePublisher_setDataSetRef(publisher, "SEL_RTAC/LLN0$DSet1");

    // GoosePublisher_setGoCbRef(publisher_2, "simple_787_2/PRO$CO$TEST_2");
    GoosePublisher_setGoCbRef(publisher_2, "SEL_RTAC/LLN0$GO$GooseDSet2");
    // GoosePublisher_setDataSetRef(publisher_2, "simple_787_2/PRO$TEST_DataSet_2");
    GoosePublisher_setDataSetRef(publisher_2, "SEL_RTAC/LLN0$DSet2");

    // GoosePublisher_setGoCbRef(publisher_3, "simple_451_2/PRO$CO$TEST_3");
    GoosePublisher_setGoCbRef(publisher_3, "SEL_RTAC/LLN0$GO$GooseDSet3");
    // GoosePublisher_setDataSetRef(publisher_3, "simple_451_2/PRO$TEST_DataSet_3");
    GoosePublisher_setDataSetRef(publisher_3, "SEL_RTAC/LLN0$DSet3");


    pthread_t tid_rec;
    struct args_rec *rec_struct = (struct args_rec *)malloc(sizeof(struct args_rec));
    rec_struct->receiver = receiver;
    rec_struct->myid = tid_rec;

    pthread_create(&tid_rec, NULL, threadedReceiver, (void *)rec_struct);
    GooseReceiver_start(receiver);

    pthread_t tid_pub;
    struct args_pub *pub_struct = (struct args_pub *)malloc(sizeof(struct args_pub));
    pub_struct->device_name = "RTAC";
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
