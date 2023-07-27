/*
 * goose_publisher_example.c
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>

#include "mms_value.h"
#include "goose_publisher.h"
#include "goose_receiver.h"
#include "hal_thread.h"


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

/* has to be executed as root! */
int
main(int argc, char **argv)
{
    char *interface;
    char *device_name;

    if (argc > 1) {
        interface = argv[1];
        device_name = argv[2];
    }
    else {
        // interface = "eth0";
        interface = "lo";
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

    LinkedList dataSetValues = LinkedList_create();
    CommParameters gooseCommParameters;

    if (strcmp(device_name, "RTAC") == 0) 
    {
        printf("GOOSE RTAC configuration initiated...\n");
        // TODO: 
        // Should have the integer for the True/False or Open/Close
        // and another interger for Trip/NoTrip
        // gooseCommParameters should be here as well.
        // There should be multiple ones based on the comm paths of
        // the devices

        // Breaker status (for device No ?) 0/1 or Open/Close.
        // LinkedList_add(dataSetValues, MmsValue_newIntegerFromInt32(1));
        LinkedList_add(dataSetValues, MmsValue_newBoolean(true));

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
    else if (strcmp(device_name, "651R_2") == 0)
    {
        printf("GOOSE 651R_2 configuration initiated...\n");

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

    printf("Using interface %s\n", interface);

    /*
     * Create a new GOOSE publisher instance. As the second parameter the interface
     * name can be provided (e.g. "eth0" on a Linux system). If the second parameter
     * is NULL the interface name as defined with CONFIG_ETHERNET_INTERFACE_ID in
     * stack_config.h is used.
     */
    GoosePublisher publisher = GoosePublisher_create(&gooseCommParameters, interface);

    if (publisher) {
        // TODO: Change the goCbRef and DataSetRef as well
        // GoosePublisher_setGoCbRef(publisher, "simpleIOGenericIO/LLN0$GO$gcbAnalogValues");
        GoosePublisher_setConfRev(publisher, 1);
        // GoosePublisher_setDataSetRef(publisher, "simpleIOGenericIO/LLN0$AnalogValues");
        GoosePublisher_setTimeAllowedToLive(publisher, 500);

        if (strcmp(device_name, "RTAC") == 0) 
        {
            printf("GOOSE RTAC GOOSE configuration initiated...\n");

        } 
        else if (strcmp(device_name, "651R_2") == 0)
        {
            printf("GOOSE 651R_2 GOOSE configuration initiated...\n");

            // GoosePublisher_setGoCbRef(publisher, "simple_651R_2/LLN0$CO$BCACSWI2$Pos$ctlVal");
            GoosePublisher_setGoCbRef(publisher, "simple_651R_2/PRO$CO$BCACSWI2");
            GoosePublisher_setDataSetRef(publisher, "simple_651R_2/PRO$BCACSWI2_DataSet");
        }
        else if (strcmp(device_name, "787_2") == 0)
        {
            printf("GOOSE 787_2 GOOSE configuration initiated...\n");
        }
        else if (strcmp(device_name, "451_2") == 0)
        {
            printf("GOOSE 451_2 GOOSE configuration initiated...\n");
        }
        else
        {
            printf("No device supported, exiting...\n");
            return 1;
        }


        int i = 0;
        uint32_t prev_stNum = 0; 

        // TODO: The below should be adjusted for each device
        // based on the collected information.

        // Interval in ms
        // int min_interval = 10;
        int min_interval = 4;
        // int min_interval = 500;
        int interval = min_interval;
        // int max_interval = 100;
        int max_interval = 1000;
        // int max_interval = 5000;

        int max_i = 10;

        while (1) {
            
            
            if (GoosePublisher_publish(publisher, dataSetValues) == -1) {
                    printf("Error sending message!\n");
            }
            Thread_sleep(interval);
            
            // First option 
            // if( i <= 3) {
            //     interval = 2 * interval;
            // }
            // else {
            //     interval = max_interval;
            // }

            // Second option
            if( i == 0) {
                interval = min_interval;
            }
            else if( i < 3) {
                interval = 2 * interval;
            }
            else {
                interval = max_interval;
            }
            
            // .. then us a condition to change something to start from the
            // beginning

            if( i == max_i) {
                GoosePublisher_increaseStNum(publisher);
                i = 0;
                interval = min_interval;
            }

            i++;
        }

        GoosePublisher_destroy(publisher);
    }
    else {
        printf("Failed to create GOOSE publisher. Reason can be that the Ethernet interface doesn't exist or root permission are required.\n");
    }

    LinkedList_destroyDeep(dataSetValues, (LinkedListValueDeleteFunction) MmsValue_delete);

    return 0;
}




