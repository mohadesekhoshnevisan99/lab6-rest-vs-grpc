# Lab 6 – REST vs. gRPC Performance Measurements

All times are in milliseconds per operation. Each Local REST/gRPC measurement is the average of 100 requests. The Local ping value is the average round-trip time over 10 packets. The measurements were taken on October 13, 2026.

| Method | Local (ms) | Same-Zone (ms) | Different Region (ms) |
|---|---:|---:|---:|
| REST add | 1.8008 | Not measured | Not measured |
| gRPC add | 0.4326 | Not measured | Not measured |
| REST rawimg | 4.7205 | Not measured | Not measured |
| gRPC rawimg | 3.7153 | Not measured | Not measured |
| REST dotproduct | 2.0655 | Not measured | Not measured |
| gRPC dotproduct | 0.5104 | Not measured | Not measured |
| REST jsonimg | 17.5807 | Not measured | Not measured |
| gRPC jsonimg | 12.2616 | Not measured | Not measured |
| PING (average RTT) | 0.0330 | Not measured | Not measured |

## Observations

For my localhost tests, gRPC was faster than REST for all four operations. The difference was especially noticeable for the small add and dotproduct requests. Raw images took longer than these small requests, and sending images as JSON with Base64 took the most time. I think this is partly because Base64 makes the data larger and adds encoding/decoding work. The localhost ping time was only about 0.033 ms, much smaller than the API request times, so most of the measured time here comes from the Python code, serialization, HTTP/RPC processing, and image handling rather than the network trip. REST in this lab uses separate HTTP requests without a persistent client session, while the gRPC client reuses a channel/connection, which can reduce connection overhead. For servers in different regions, I would expect network round-trip time to matter much more, but I cannot conclude that from localhost measurements alone.

## Measurement scope / limitation

I completed and tested the REST and gRPC implementations locally. I could not obtain actual Same-Zone or Different-Region measurements because the Google Cloud educational billing account linked to the project was closed. Those results are marked **Not measured** rather than estimated. If access to cloud instances becomes available, I will run the clients and servers on separate VMs and record the measurements in the table.

Raw timing data: `lab6_test_results.csv`.
