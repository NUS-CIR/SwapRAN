# libswapRAN.so

We use LD_PRELOAD to load `libswapRAN.so` to intercept calls that start/initialize real-time/high-priority threads.
Given how OAI creates and sets up their real-time/high-priority threads, we have adapted this implementation accordingly, as compared to the version that we have discussed in the SwapRAN paper.

In short, the SwapRAN paper only intercepts the `pthread_setschedparam` call.
In contrast, for OAI, here, we intercept addtional calls, including `pthread_attr_setschedparam` and `pthread_setaffinity_np`.

Despite the differences, the logic remains similar to what has been discussed in the paper -- we intercept the initialization/start-up of the first real-time/high-priority thread, block it, and wait until the old DU is terminated (we wait for the old DU's preStop hook to be triggered) before allowing it to continue.

## Implementation Details 

This implementation is a simplified version of what is presented in the SwapRAN paper.

To allow the new DU and the old DU to communicate their status, we use a simple file-based approach which involves reading/writing to the file `/tmp/rt_status.txt`.

Key steps:
1. When the new DU starts, it writes the value `999` to the file when the first real-time/high-priority thread is being initialized/started, and it blocks/waits at this point.
1. Then, it waits for the old DU's  preStop hook to be triggered which expects the value `999` indicating that the new DU is ready.
1. The old DU then starts demoting its real-time/high-priority threads, and once they are demoted, it writes the value `0` to the file and returns from the preStop hook allowing itself to terminate.
1. The new DU, which has been blocked/waiting, detects the value `0` in the file, and it continues initializing/starting its real-time/high-priority threads.

## Using libswapRAN.so

To use this shared library, one simply prepends `LD_PRELOAD=/path/to/libswapRAN.so` to the OAI's `nr-softmodem` command.

For example:
```
sudo LD_PRELOAD=/path/to/libswapRAN.so ./nr-softmodem -O ~/gnb.conf --sa --thread-pool 16,17,18,19,20,21,22,23
```

## Demo Setup

Copy `/path/to/libswapRAN.so` and put it under `/tmp`.