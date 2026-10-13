#!/usr/bin/env python3
"""Client and latency benchmark for the four Lab 6 gRPC operations."""

import argparse
import base64
import random
import time
from pathlib import Path

import grpc

import lab6_pb2
import lab6_pb2_grpc

IMAGE_PATH = Path(__file__).with_name('Flatirons_Winter_Sunrise_edit_2.jpg')


def main():
    parser = argparse.ArgumentParser(description='gRPC client for Lab 6')
    parser.add_argument('host', help='Hostname or IP address of the gRPC server')
    parser.add_argument('cmd', choices=['add', 'rawImage', 'dotProduct', 'jsonImage'])
    parser.add_argument('reps', type=int, help='Number of requests to run')
    parser.add_argument('-p', '--port', type=int, default=50051)
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    if args.reps <= 0:
        parser.error('reps must be a positive integer')

    address = f'{args.host}:{args.port}'
    print(f'Running {args.reps} reps against {address}')

    # Read the image once; network/RPC time is measured separately from file I/O.
    img = None
    encoded_img = None
    if args.cmd in ('rawImage', 'jsonImage'):
        img = IMAGE_PATH.read_bytes()
        if args.cmd == 'jsonImage':
            encoded_img = base64.b64encode(img).decode('ascii')

    with grpc.insecure_channel(address, options=[
        ('grpc.max_send_message_length', 16 * 1024 * 1024),
        ('grpc.max_receive_message_length', 16 * 1024 * 1024),
    ]) as channel:
        stub = lab6_pb2_grpc.Lab6ServiceStub(channel)
        # Connect before timing so connect setup does not skew average requests.
        grpc.channel_ready_future(channel).result(timeout=10)
        start = time.perf_counter()
        for _ in range(args.reps):
            if args.cmd == 'add':
                reply = stub.Add(lab6_pb2.addMsg(a=5, b=10))
                result = {'sum': reply.sum}
            elif args.cmd == 'rawImage':
                reply = stub.RawImage(lab6_pb2.rawImageMsg(img=img))
                result = {'width': reply.width, 'height': reply.height}
            elif args.cmd == 'dotProduct':
                a = [random.random() for _ in range(100)]
                b = [random.random() for _ in range(100)]
                reply = stub.DotProduct(lab6_pb2.dotProductMsg(a=a, b=b))
                result = {'dotproduct': reply.dotproduct}
            else:
                reply = stub.JsonImage(lab6_pb2.jsonImageMsg(img=encoded_img))
                result = {'width': reply.width, 'height': reply.height}
            if args.debug:
                print('Response is', result)
        elapsed_ms = (time.perf_counter() - start) * 1000 / args.reps
        print('Took', elapsed_ms, 'ms per operation')


if __name__ == '__main__':
    main()
