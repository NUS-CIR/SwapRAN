#define _GNU_SOURCE
#include <dlfcn.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

static int rt_thread_count = 0;
static int blocking = 0;

// Function pointer to hold the original pthread_setschedparam function
int (*original_pthread_setschedparam)(pthread_t, int, const struct sched_param *);

// Interceptor function
int pthread_setschedparam(pthread_t thread, int policy, const struct sched_param *param) {
    // Load the original function if not already loaded
    if (!original_pthread_setschedparam) {
        original_pthread_setschedparam = dlsym(RTLD_NEXT, "pthread_setschedparam");
        if (!original_pthread_setschedparam) {
            fprintf(stderr, "Error loading original pthread_setschedparam: %s\n", dlerror());
            return -1;
        }
    }

    // Print the thread name
    char thread_name[16];
    pthread_getname_np(thread, thread_name, sizeof(thread_name));
    printf("[LIBSWAPRAN] Thread name: %s\n", thread_name);

    // Log the call
    printf("[LIBSWAPRAN] Intercepted pthread_setschedparam call: thread=%lu, policy=%d, priority=%d\n",
           thread, policy, param->sched_priority);

    if(!rt_thread_count && param->sched_priority > 50) {
        // Increment the thread count
        rt_thread_count++;
        blocking = 1;

        printf("[LIBSWAPRAN] This is the first intercepted thread.\n");

        // Write the value "999" to a shared file that will be read by the old DUs preStop hook
        // Then, wait for the file to reset with the value "0" before proceeding
        FILE *file = fopen("/tmp/rt_status.txt", "w");
        // write the value "999" to the file
        if (file) {
            fprintf(file, "999");
            fclose(file);
        } else {
            perror("Error opening file");
        }
        // wait for the file to be updated by preStop hook
        // at most wait for 10 seconds
        int sleep_count = 0;
        while (1) {
            file = fopen("/tmp/rt_status.txt", "r");
            if (file) {
                int count;
                fscanf(file, "%d", &count);
                fclose(file);
                if (count == 0 || sleep_count > 1000) {
                    // If the file contains "0" or if we have waited for 10 seconds, exit the loop
                    blocking = 0;
                    
                    if(count != 0) {
                        FILE *file = fopen("/tmp/rt_status.txt", "w");
                        fprintf(file, "0");
                        fclose(file);
                    }
                    break; // Exit the loop if the file contains "0"
                }
            } else {
                perror("Error opening file");
            }
            // sleep for 10 ms
            usleep(10000);
            sleep_count++;
        }
        printf("[LIBSWAPRAN] PreStop hook at old DU is executed, proceeding with normal execution.\n");
    } 

    // Wait until the blocking condition is resolved
    while(blocking) {}
    
    printf("[LIBSWAPRAN] Calling original pthread_setschedparam function for thread %s\n", thread_name);

    // Call the original function
    return original_pthread_setschedparam(thread, policy, param);
}


// Function pointer to hold the original pthread_attr_setschedparam function
int (*original_pthread_attr_setschedparam)(pthread_attr_t *, const struct sched_param *);

// Interceptor function
int pthread_attr_setschedparam(pthread_attr_t *attr, const struct sched_param *param) {
    // Load the original function if not already loaded
    if (!original_pthread_attr_setschedparam) {
        original_pthread_attr_setschedparam = dlsym(RTLD_NEXT, "pthread_attr_setschedparam");
        if (!original_pthread_attr_setschedparam) {
            fprintf(stderr, "Error loading original pthread_attr_setschedparam: %s\n", dlerror());
            return -1;
        }
    }

    // Print the thread name
    char thread_name[16];
    pthread_t thread = pthread_self();
    pthread_getname_np(thread, thread_name, sizeof(thread_name));
    printf("[LIBSWAPRAN] Thread name: %s\n", thread_name);

    // Log the call
    printf("[LIBSWAPRAN] Intercepted pthread_attr_setschedparam call: priority=%d\n", param->sched_priority);

    // Get the scheduling policy
    int policy;
    pthread_attr_getschedpolicy(attr, &policy);
    printf("[LIBSWAPRAN] Scheduling policy: %d\n", policy);

    // if(!rt_thread_count && param->sched_priority > 50) {
    //     // Increment the thread count
    //     rt_thread_count++;
    //     blocking = 1;

    //     printf("[LIBSWAPRAN] This is the first intercepted thread.\n");

    //     // Write the value "999" to a shared file that will be read by the old DUs preStop hook
    //     // Then, wait for the file to reset with the value "0" before proceeding
    //     FILE *file = fopen("/tmp/rt_status.txt", "w");
    //     // write the value "999" to the file
    //     if (file) {
    //         fprintf(file, "999");
    //         fclose(file);
    //     } else {
    //         perror("Error opening file");
    //     }
    //     // wait for the file to be updated by preStop hook
    //     // at most wait for 10 seconds
    //     int sleep_count = 0;
    //     while (1) {
    //         file = fopen("/tmp/rt_status.txt", "r");
    //         if (file) {
    //             int count;
    //             fscanf(file, "%d", &count);
    //             fclose(file);
    //             if (count == 0 || sleep_count > 1000) {
    //                 // If the file contains "0" or if we have waited for 10 seconds, exit the loop
    //                 blocking = 0;
                    
    //                 if(count != 0) {
    //                     FILE *file = fopen("/tmp/rt_status.txt", "w");
    //                     fprintf(file, "0");
    //                     fclose(file);
    //                 }
    //                 break; // Exit the loop if the file contains "0"
    //             }
    //         } else {
    //             perror("Error opening file");
    //         }
    //         // sleep for 10 ms
    //         usleep(10000);
    //         sleep_count++;
    //     }
    //     printf("[LIBSWAPRAN] PreStop hook at old DU is executed, proceeding with normal execution.\n");
    // } 

    // // Wait until the blocking condition is resolved
    // while(blocking && param->sched_priority > 50) {}

    // Call the original function
    return original_pthread_attr_setschedparam(attr, param);
}

// pthread_setaffinity_np 
// This function points to the original pthread_setaffinity_np function
int (*original_pthread_setaffinity_np)(pthread_t, size_t, const cpu_set_t *);

// Interceptor function
int pthread_setaffinity_np(pthread_t thread, size_t cpusetsize, const cpu_set_t *cpuset) {
    // Load the original function if not already loaded
    if (!original_pthread_setaffinity_np) {
        original_pthread_setaffinity_np = dlsym(RTLD_NEXT, "pthread_setaffinity_np");
        if (!original_pthread_setaffinity_np) {
            fprintf(stderr, "Error loading original pthread_setaffinity_np: %s\n", dlerror());
            return -1;
        }
    }

    // Print the thread name
    char thread_name[16];
    pthread_getname_np(thread, thread_name, sizeof(thread_name));
    printf("[LIBSWAPRAN] Thread name: %s\n", thread_name);

    // Log the call
    printf("[LIBSWAPRAN] Intercepted pthread_setaffinity_np call: thread=%lu, cpusetsize=%zu\n",
           thread, cpusetsize);
    
    int has_rt_threads = 0;
    // check if the cpu_set covers 0-15
    for (int i = 0; i < CPU_SETSIZE; i++) {
        if (CPU_ISSET(i, cpuset)) {
            // check if the cpu_set covers 0-15
            if (i >= 0 && i <= 15) {
                has_rt_threads = 1;
                break;
            }
        }
    }

    // get this threads scheduling policy
    int policy;
    struct sched_param param;
    pthread_getschedparam(thread, &policy, &param);
    printf("[LIBSWAPRAN] Thread scheduling policy: %d\n", policy);
    printf("[LIBSWAPRAN] Thread scheduling priority: %d\n", param.sched_priority);

    if(!rt_thread_count && has_rt_threads && param.sched_priority > 50) {
        // Increment the thread count
        rt_thread_count++;
        blocking = 1;

        printf("[LIBSWAPRAN] This is the first intercepted thread.\n");

        // Write the value "999" to a shared file that will be read by the old DUs preStop hook
        // Then, wait for the file to reset with the value "0" before proceeding
        FILE *file = fopen("/tmp/rt_status.txt", "w");
        // write the value "999" to the file
        if (file) {
            fprintf(file, "999");
            fclose(file);
        } else {
            perror("Error opening file");
        }
        // wait for the file to be updated by preStop hook
        // at most wait for 10 seconds
        int sleep_count = 0;
        while (1) {
            file = fopen("/tmp/rt_status.txt", "r");
            if (file) {
                int count;
                fscanf(file, "%d", &count);
                fclose(file);
                if (count == 0 || sleep_count > 1000) {
                    // If the file contains "0" or if we have waited for 10 seconds, exit the loop
                    blocking = 0;
                    
                    if(count != 0) {
                        FILE *file = fopen("/tmp/rt_status.txt", "w");
                        fprintf(file, "0");
                        fclose(file);
                    }
                    break; // Exit the loop if the file contains "0"
                }
            } else {
                perror("Error opening file");
            }
            // sleep for 10 ms
            usleep(10000);
            sleep_count++;
        }
        printf("[LIBSWAPRAN] PreStop hook at old DU is executed, proceeding with normal execution.\n");
    }

    while(blocking && has_rt_threads && param.sched_priority > 50) {}

    // Call the original function
    return original_pthread_setaffinity_np(thread, cpusetsize, cpuset);
}

// SCHED_FIFO 1
// SCHED_RR 2
// SCHED_OTHERS 3








