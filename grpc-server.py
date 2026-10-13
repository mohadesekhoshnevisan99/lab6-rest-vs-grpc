#!/usr/bin/env python3
"""gRPC server for Lab 6: REST vs gRPC."""

import argparse
import base64
import io
from concurrent import futures

import grpc
from PIL import Image

import lab6_pb2
import lab6_pb2_grpc


class Lab6Server(lab6_pb2_grpc.Lab6ServiceServicer):
    def Add(self, request, context):
        return lab6_pb2.addReply(sum=request.a + request.b)

    def RawImage(self, request, context):
        try:
            with Image.open(io.BytesIO(request.img)) as image:
                width, height = image.size
        except Exception:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid image data")
        return lab6_pb2.imageReply(width=width, height=height)

    def DotProduct(self, request, context):
        if len(request.a) != len(request.b):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Vectors must have the same length")
        value = sum(a * b for a, b in zip(request.a, request.b))
        return lab6_pb2.dotProductReply(dotproduct=value)

    def JsonImage(self, request, context):
        try:
            image_bytes = base64.b64decode(request.img, validate=True)
            with Image.open(io.BytesIO(image_bytes)) as image:
                width, height = image.size
        except Exception:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid base64 image data")
        return lab6_pb2.imageReply(width=width, height=height)


def main():
    parser = argparse.ArgumentParser(description="Lab 6 gRPC server")
    parser.add_argument("-p", "--port", type=int, default=50051)
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[("grpc.max_receive_message_length", 16 * 1024 * 1024)])
    lab6_pb2_grpc.add_Lab6ServiceServicer_to_server(Lab6Server(), server)
    server.add_insecure_port(f"[::]:{args.port}")
    server.start()
    print(f"gRPC server running on port {args.port}", flush=True)
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=0)


if __name__ == "__main__":
    main()
