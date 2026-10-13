#!/usr/bin/env python3
"""Run Lab 6 REST/gRPC measurements against running servers.

Run from the repository directory:
  uv run python run_lab6_tests.py --rest-host localhost --grpc-host localhost --label Local
For cloud tests, run client on a US VM, use the remote server's internal IPs,
  and choose a different label. Never substitute local timings for remote tests.
"""
import argparse
import csv
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OPS = ('add', 'rawImage', 'dotProduct', 'jsonImage')


def command_result(command, timeout):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description='Lab 6 REST / gRPC latency tests')
    parser.add_argument('--rest-host', default='localhost')
    parser.add_argument('--grpc-host', default=None, help='Default: same as REST host')
    parser.add_argument('--rest-port', type=int, default=5000)
    parser.add_argument('--grpc-port', type=int, default=50051)
    parser.add_argument('--reps', type=int, default=100)
    parser.add_argument('--label', default='Local')
    parser.add_argument('--output', default='lab6_test_results.csv')
    args = parser.parse_args()
    if args.reps <= 0:
        parser.error('--reps must be greater than zero')
    grpc_host = args.grpc_host or args.rest_host
    outputs = []
    for protocol, host, port, client in (
        ('REST', args.rest_host, args.rest_port, 'rest-client.py'),
        ('gRPC', grpc_host, args.grpc_port, 'grpc-client.py'),
    ):
        for op in OPS:
            cmd = [sys.executable, client, host, op, str(args.reps), '-p', str(port)]
            print(f'Running {protocol} {op}: {host}:{port} ...', flush=True)
            try:
                result = command_result(cmd, max(45, args.reps * 10))
                match = re.search(r'Took\s+([0-9.eE+-]+)\s+ms per operation', result.stdout)
                if result.returncode or not match:
                    print('FAILED:', result.stderr.strip() or result.stdout.strip())
                    continue
                ms = float(match.group(1))
                outputs.append((args.label, protocol, op, args.reps, f'{ms:.6f}', datetime.now(timezone.utc).isoformat()))
                print(f'  {ms:.4f} ms per operation')
            except subprocess.TimeoutExpired:
                print('FAILED: timed out')
    print(f'Running ping to {args.rest_host} ...', flush=True)
    try:
        ping = command_result(['ping', '-c', '10', args.rest_host], 30)
        match = re.search(r'(?:rtt|round-trip) min/avg/max/(?:mdev|stddev)\s*=\s*([\d.]+)/([\d.]+)/', ping.stdout)
        if match and ping.returncode == 0:
            ms = float(match.group(2))
            outputs.append((args.label, 'PING', 'round-trip', 10, f'{ms:.6f}', datetime.now(timezone.utc).isoformat()))
            print(f'  {ms:.4f} ms average RTT')
        else:
            print('Ping could not be measured:', ping.stderr.strip() or ping.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print('Ping command unavailable or timed out')
    output_file = Path(args.output)
    exists = output_file.exists() and output_file.stat().st_size > 0
    with output_file.open('a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(('location', 'protocol', 'operation', 'repetitions', 'average_ms', 'recorded_utc'))
        writer.writerows(outputs)
    print(f'Wrote {len(outputs)} measurements to {output_file}')
    if len(outputs) != 9:
        print('Some tests did not finish; check that both servers are running and reachable.')
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
