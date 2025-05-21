# libswapRAN.so

We use LD_PRELOAD to load `libswapRAN.so` to intercept calls that start/initialize real-time/high-priority threads.
Given how OAI creates and sets up their real-time/high-priority threads, we have adapted this implementation accordingly, as compared to the version that we have discussed in the SwapRAN paper.

In short, the SwapRAN paper only intercepts the `pthread_setschedparam` call.
In contrast, for OAI, here, we intercept addtional calls, including `pthread_attr_setschedparam` and `pthread_setaffinity_np`.

Despite the differences, the logic remains similar to what has been discussed in the paper -- we intercept the initialization/start-up of the first real-time/high-priority thread, block it, and wait until the old DU is terminated before allowing it to continue.

## Using libswapRAN.so

To use this shared library, one simply appends `LD_PRELOAD=/path/to/libswapRAN.so` to the OAI's `nr-softmodem` command.

For example:
```
sudo LD_PRELOAD=/path/to/libswapRAN.so ./nr-softmodem -O ~/gnb.conf --sa --thread-pool 16,17,18,19,20,21,22,23
```