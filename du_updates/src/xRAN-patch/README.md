# xRAN Fast Startup Patch

During initialization, xRAN always waits until the frame ID to rotate back to 0 before starting it.
This slows down the DU start up process, as xRAN would block the whole DU, resulting in a waiting time of up to 10 seconds or so.

Here, we provide a patch that get rids of this waiting, and forces xRAN to start xRAN as quickly as possible without waiting from the frame ID to rotate back.
This results in a near-immediate DU start up in practice.

## Applying this Patch

This patch has been tested with the OAI DU, using the F-release of xRAN.
First, you should apply OAI's F-release patch, before applying `swapran.patch`.