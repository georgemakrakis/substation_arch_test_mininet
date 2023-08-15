#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <signal.h>
#include <sys/time.h>
#include <time.h>
#include <math.h>
#include <inttypes.h>

#include <pthread.h>
#include <unistd.h>
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>

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


char *device_name;

static int running = 1;

static 
LinkedList dataSetValues;

static
LinkedList dataSetValuesReceivedFrom651R_2;

static
LinkedList dataSetValuesTo787;

static
LinkedList dataSetValuesTo451_2;

char buffer_time[26];


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

int fileLog(char *message){

    char *dir_path = (char*)malloc(100 * sizeof(char));
    sprintf(dir_path, "%s-%s", 
        "/home/mininet/substation_arch_test/goose_CHE_203_generic/logs_dir", device_name);

    FILE *log_file;
    DIR* dir = opendir(dir_path);

    // printf("At %s.%03d\n", buffer_time, millisec);
    char *log_name = (char*)malloc(26 * sizeof(char));
    sprintf(log_name, "%s-%s.log", device_name, buffer_time);

    if (dir) {
        closedir(dir);
    } else if (ENOENT == errno) {
        printf("Directory does not exist, creating ...\n");
        int result = mkdir(dir_path, 0777);
        closedir(dir);
    } else {
        printf("Other directory error ...\n");
        return 1;
    }

    char *log_path = (char*)malloc(100 * sizeof(char));
    sprintf(log_path, "%s/%s", dir_path, log_name);

    log_file = fopen(log_path, "a+"); // a+ (create + append) option will allow appending which is useful in a log file
    
    if (log_file == NULL) { 
        // Something is wrong
        return 1;
    }
    fprintf(log_file, "%s\n", message);
    fclose(log_file);

    return 0;
}

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

    char *timestamp_msg = (char*)malloc(70 * sizeof(char));
    sprintf(timestamp_msg, "packet timestamp: %u.%u\n", (uint32_t) (timestamp / 1000), (uint32_t) (timestamp % 1000));
    // fileLog(timestamp_msg);

    // Creating loggging for the device
    // long            ms; // Milliseconds
    // time_t          s;  // Seconds
    // struct timespec spec;
    // clock_gettime(CLOCK_REALTIME, &spec);
    // s  = spec.tv_sec;
    // ms = round(spec.tv_nsec / 1.0e6); // Convert nanoseconds to milliseconds
    // if (ms > 999) {
    //     s++;
    //     ms = 0;
    // }
    // sprintf(timestamp_msg, "device timestamp: %"PRIdMAX".%03ld\n", (intmax_t)s, ms);
    // fileLog(timestamp_msg);

    // printf("  timestamp: %u.%u\n", (uint32_t) (timestamp / 1000), (uint32_t) (timestamp % 1000));
    printf("  %s", timestamp_msg);
    printf("  message is %s\n", GooseSubscriber_isValid(subscriber) ? "valid" : "INVALID");

    MmsValue* values = GooseSubscriber_getDataSetValues(subscriber);

    char buffer[1024];

    MmsValue_printToBuffer(values, buffer, 1024);

    printf("  allData: %s\n", buffer);

    int updated = 0;

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
                if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "SEL_651R_2/LLN0$GO$GooseDSet1") == 0){
                        
                        LinkedList prev_Val = LinkedList_get(dataSetValuesReceivedFrom651R_2, i);

                        MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val);

                        if (MmsValue_toInt32(value) != MmsValue_toInt32(elementValue)){
                            updated = 1;
                        }

                        LinkedList_remove(dataSetValuesReceivedFrom651R_2, value);
                        LinkedList_add(dataSetValuesReceivedFrom651R_2, MmsValue_newIntegerFromInt32(MmsValue_toInt32(elementValue)));
                }
            }
        }
    }

    

    if (strcmp(GooseSubscriber_getGoCbRef(subscriber), "SEL_651R_2/LLN0$GO$GooseDSet1") == 0){

        if(updated == 1){
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

    // Adds time logging for the "packet"
    char buffered_time[26];
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

    strftime(buffered_time, 26, "%Y:%m:%d %H:%M:%S", tm_info);
    printf("At %s.%03d\n", buffered_time, millisec);
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
    int publish_interval = 0;
    // int max_interval = 100;
    int max_interval = 1000;
    if (strcmp(device_name, "651R_2") == 0) {
        max_interval = 100;
    }
    else  if (strcmp(device_name, "787_2") == 0) {
        min_interval = 10;
        max_interval = 100;
    }
    else  if (strcmp(device_name, "451_1") == 0) {
        max_interval = 1000;
    }
    // There is no example for RTAC, the values are arbitrary.
    else  if (strcmp(device_name, "RTAC") == 0) {
        min_interval = 10;
        max_interval = 100;
    }

    // int max_interval = 5000;
    
    // NOTE: Used as a simple condition to increase the StNum
    int max_i = 10;
    int max_i_2 = 30;

    int step_e_done = 0;
    int step_a_done = 0;

    // That seems to be the case so far for the initial message.
    GoosePublisher_setTimeAllowedToLive(publisher, 3 * min_interval);

    while (1) {
            // Now we also publish based on the defined interval
            if (GoosePublisher_publish(publisher, dataSetValues) == -1 
                || (publisher_2  != NULL && GoosePublisher_publish(publisher_2, dataSetValuesTo787) == -1)
                || (publisher_3  != NULL && GoosePublisher_publish(publisher_3, dataSetValuesTo451_2) == -1)) {
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
                    GoosePublisher_setTimeAllowedToLive(publisher, 3 * min_interval);
                    publish_interval = min_interval;
                }
                else if( i == 2) {
                    GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                    publish_interval = 2 * publish_interval;
                }
                else {
                    GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                    publish_interval = max_interval;
                }
            }
            // NOTE: There is no specific mention of intervals in the manual for RTAC
            else if (strcmp(device_name, "RTAC") == 0) {

                if (i == 0 && publish_interval < max_interval) {
                    publish_interval = min_interval;
                    GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                }
                else if (i != 0 && publish_interval < max_interval){
                    publish_interval = 2 * publish_interval;
                    if ( publish_interval >  max_interval){
                        publish_interval = max_interval;
                        GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                    }
                    else {
                        GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                    }
                    // GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                }
                else if (i != 0 && publish_interval >= max_interval){
                    publish_interval = max_interval;
                    GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                }
            }
            else if (strcmp(device_name, "787_2") == 0) {
                
                if (i == 0 && publish_interval < max_interval) {
                    publish_interval = min_interval;
                    GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                }
                else if (i != 0 && publish_interval < max_interval){
                    publish_interval = 2 * publish_interval;
                    if ( publish_interval >  max_interval){
                        publish_interval = max_interval;
                        GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                    }
                    else {
                        GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                    }
                    // GoosePublisher_setTimeAllowedToLive(publisher, 3 * publish_interval);
                }
                else if (i != 0 && publish_interval >= max_interval){
                    publish_interval = max_interval;
                    GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                }

            }
            else if (strcmp(device_name, "451_2") == 0) {
                
                if( i == 0 || i == 1) {
                    GoosePublisher_setTimeAllowedToLive(publisher, 3 * min_interval);
                    publish_interval = min_interval;
                }
                else if( i == 2) {
                    GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
                    publish_interval = 2 * publish_interval;
                }
                else {
                    GoosePublisher_setTimeAllowedToLive(publisher, 2 * max_interval);
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

            // This could be step e)
            // TODO: That will be if step e) happens from RTAC --> 651-2?
            // Combined all the events in the single "if block".
            if (strcmp(device_name, "RTAC") == 0 && i == max_i_2 && step_e_done == 0) {

                printf("=================== ISSUE FIXED, RESTORING ( STEP E) ) ===================");
                
                // For RTAC --> 651-2

                // Close
                LinkedList prev_Val_1 = LinkedList_get(dataSetValues, 0);
                MmsValue* value = (MmsValue*) LinkedList_getData(prev_Val_1);

                LinkedList_remove(dataSetValues, value);
                LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));

                // For RTAC --> 787_2
                LinkedList prev_Val_0 = LinkedList_get(dataSetValuesTo787, 0);
                
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
                GoosePublisher_increaseStNum(publisher_2);
                GoosePublisher_increaseStNum(publisher_3);
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

    // Setup logging
    // char buffer_time[26];
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

    strftime(buffer_time, 26, "%Y-%m-%d_%H-%M-%S", tm_info);

    // fileLog("Try", buffer_time);
    // fileLog("Try 2", buffer_time);

    GooseReceiver receiver = GooseReceiver_create();
    GoosePublisher publisher;
    GoosePublisher publisher_2;
    GoosePublisher publisher_3;

    char *interface;
    // char *device_name;

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
    GooseSubscriber subscriber_2;

    if (strcmp(device_name, "RTAC") == 0) 
    {
        printf("GOOSE subscriber RTAC configuration initiated...\n");
        
        // This should be sub for data from 651R_2
        // TODO: We need for the rest of them as well.
        subscriber = GooseSubscriber_create("SEL_651R_2/LLN0$GO$GooseDSet1", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x02};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1002);
    } 
    else if (strcmp(device_name, "651R_2") == 0)
    {
        printf("GOOSE subscriber 651R_2 configuration initiated...\n");

        // This should be sub for data from RTAC
        // TODO: We need for the rest of them as well.

        // TODO: Chahnge the below from TEST to something else.
        subscriber = GooseSubscriber_create("SEL_RTAC/LLN0$GO$GooseDSet1", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x01};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1001);
    }
    else if (strcmp(device_name, "787_2") == 0)
    {
        printf("GOOSE subscriber 787_2 configuration initiated...\n");

        // TODO: After testing rename this to just "subscriber"
        subscriber = GooseSubscriber_create("SEL_RTAC/LLN0$GO$GooseDSet2", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x03};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1003);
    }
    else if (strcmp(device_name, "451_2") == 0)
    {
        printf("GOOSE 451_2 configuration initiated...\n");

        // TODO: After testing rename this to just "subscriber"
        subscriber = GooseSubscriber_create("SEL_RTAC/LLN0$GO$GooseDSet3", NULL);
        uint8_t dstMac[6] = {0x01,0x0c,0xcd,0x01,0x00,0x04};
        GooseSubscriber_setDstMac(subscriber, dstMac);
        GooseSubscriber_setAppId(subscriber, 1004);
    }
    else
    {
        printf("No device supported, exiting...\n");
        return 1;
    }

    //.. and now the publisher
    dataSetValues = LinkedList_create();
    dataSetValuesReceivedFrom651R_2 = LinkedList_create();
    dataSetValuesTo787 = LinkedList_create();
    dataSetValuesTo451_2 = LinkedList_create();

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
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));
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

        // 21
        LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(0));

        gooseCommParameters.appId = 1008;
        gooseCommParameters.dstAddress[0] = 0x01;
        gooseCommParameters.dstAddress[1] = 0x0c;
        gooseCommParameters.dstAddress[2] = 0xcd;
        gooseCommParameters.dstAddress[3] = 0x01;
        gooseCommParameters.dstAddress[4] = 0x00;
        gooseCommParameters.dstAddress[5] = 0x08;
        gooseCommParameters.vlanId = 0;
        gooseCommParameters.vlanPriority = 4;
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

    // TODO: The below should be adjusted for each device
    // based on the collected information.

    if (publisher) {
        GoosePublisher_setConfRev(publisher, 1);
        // GoosePublisher_setTimeAllowedToLive(publisher, 500);

        if (strcmp(device_name, "RTAC") == 0) 
        {
            printf("RTAC GOOSE configuration initiated...\n");

            GoosePublisher_setGoCbRef(publisher, "SEL_RTAC/LLN0$GO$GooseDSet1");
            GoosePublisher_setDataSetRef(publisher, "SEL_RTAC/LLN0$DSet1");

            GoosePublisher_setGoCbRef(publisher_2, "SEL_RTAC/LLN0$GO$GooseDSet2");
            GoosePublisher_setDataSetRef(publisher_2, "SEL_RTAC/LLN0$DSet2");

            GoosePublisher_setGoCbRef(publisher_3, "SEL_RTAC/LLN0$GO$GooseDSet3");
            GoosePublisher_setDataSetRef(publisher_3, "SEL_RTAC/LLN0$DSet3");
        } 
        // NOTE: JUST FOR TESTING
        else if (strcmp(device_name, "651R_2") == 0)
        // if (strcmp(device_name, "RTAC") == 0)
        {
            printf("651R_2 GOOSE configuration initiated...\n");

            // GoosePublisher_setGoCbRef(publisher, "simple_651R_2/LLN0$CO$BCACSWI2$Pos$ctlVal");
            GoosePublisher_setGoCbRef(publisher, "SEL_651R_2/LLN0$GO$GooseDSet1");
            GoosePublisher_setDataSetRef(publisher, "SEL_651R_2/LLN0$GooseDSet1");
        }
        else if (strcmp(device_name, "787_2") == 0)
        {
            printf("787_2 GOOSE configuration initiated...\n");
            
            GoosePublisher_setGoCbRef(publisher, "SEL_787_2/LLN0$GO$GooseDSet1");
            GoosePublisher_setDataSetRef(publisher, "SEL_787_2/LLN0$GooseDSet1");
        }
        else if (strcmp(device_name, "451_2") == 0)
        {
            printf("451_2 GOOSE configuration initiated...\n");

            GoosePublisher_setGoCbRef(publisher, "SEL_451_2/LLN0$GO$GooseDSet1");
            GoosePublisher_setDataSetRef(publisher, "SEL_451_2/LLN0$GooseDSet1");
        }
        else
        {
            printf("No device supported, exiting...\n");
            return 1;
        }
    }

    if (strcmp(device_name, "651R_2") == 0 ||
        strcmp(device_name, "787_2") == 0 ||
        strcmp(device_name, "451_2") == 0) {
            
        publisher_2 = NULL;
        publisher_3 = NULL;
    }


    GooseSubscriber_setListener(subscriber, gooseListener, NULL);

    GooseReceiver_addSubscriber(receiver, subscriber);

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