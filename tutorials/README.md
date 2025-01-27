# The Refinery Files

### [Volume 1 — NetWalker Dropper][0x01]

Extract a NetWalker sample and its configuration from a PowerShell loader. The tutorial touches on all fundamental binary refinery concepts.

### [Volume 2 — Amadey Loader Strings][0x02]

A short tutorial extracting the strings (including C2 configuration) of an Amadey Loader sample. Revisits most of the concepts that were introduced in the tutorial.

### [Volume 3 — SedUpLoader C2s][0x03]

In this tutorial, we extract the C2 configuration from a SedUpLoader sample. The tutorial introduces the push/pop mechanic, which is used to first extract a decryption key, store it as a variable, continue to extract the C2 data, and then decrypt the C2 domains using the stored key.

### [Volume 4 — Run Length Encoding][0x04]

A short tutorial about a loader using a custom run-length encoding. The tutorial showcases how to define custom refinery units when it would be too difficult to implement a decoding step using existing units.

### [Volume 5 — FlareOn 9][0x05]

This is a refinery-focused write-up of how to solve FlareOn9.


[0x01]: tbr-files.v0x01.netwalker.dropper.ipynb
[0x02]: tbr-files.v0x02.amadey.loader.ipynb
[0x03]: tbr-files.v0x03.seduploader.ipynb
[0x04]: tbr-files.v0x04.run.length.encoding.ipynb
[0x05]: tbr-files.v0x05.flare.on.9.ipynb