# xRAN Fast Startup Patch

During initialization, xRAN always waits until the frame ID to rotate back to 0 before starting it.
This slows down the DU start up process, as xRAN would block the whole DU, resulting in a waiting time of up to 10 seconds or so.

Here, we provide a patch that get rids of this waiting, and forces xRAN to start xRAN as quickly as possible without waiting from the frame ID to rotate back.
This results in a near-immediate DU start up in practice.

## Applying this Patch

This patch has been tested with the OAI DU, using the F-release of xRAN.

First, you should apply OAI's F-release patch, before applying `swapran.patch`.

Note that the current patch file has been tested to work with the OAI F-release as of `2025.w31`.
You may need to do the patching manually if there are any conflicts in future versions, but it should be straightforward to do so.

#### Upstreaming this Patch

We are working with the OAI maintainers to upstream this patch into the OAI codebase.

You can track the progress of this upstreaming effort through the following MR: https://gitlab.eurecom.fr/oai/openairinterface5g/-/merge_requests/3585.
Apart from the xRAN fast startup patch, this MR also includes minor changes to ensure that the L1 is ready before allowing xRAN to start sending packets to the DU.