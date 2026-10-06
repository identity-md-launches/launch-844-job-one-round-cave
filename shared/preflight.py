#!/usr/bin/env python3
"""Combine public RPC health, proxy routing, source lookup and unsigned eth_call."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from tools import rpc_health, proxy_route, source_check, call_preview


def preflight(address, data, endpoints, result_type='raw'):
    observations = [rpc_health.probe(url, 12, 120) for url in endpoints]
    good = [o for o in observations if o['status'] == 'fresh']
    if not good:
        return {'status': 'blocked', 'reason': 'No fresh mainnet endpoint',
                'observations': observations, 'sent': False}
    endpoint = min(good, key=lambda o: o['latency_ms'])['endpoint']
    routing = proxy_route.inspect(endpoint, address)
    # Storage indicators are review leads, not proof of the execution target.
    addresses = [address]
    for kind, target in routing['routes'].items():
        if target and kind != 'beacon' and target not in addresses:
            addresses.append(target)
    sources = []
    for target in addresses:
        try:
            source = source_check.fetch(target)
            source.pop('sources', None)  # Keep untrusted source text out of this summary.
            sources.append(source)
        except (ValueError, OSError) as error:
            sources.append({'address': target, 'status': 'lookup_error', 'error': str(error)})
    block = hex(routing['block_number'])
    transaction = {'to': address, 'data': data, 'value': '0x0'}
    response = call_preview.rpc_call(endpoint, transaction, block)
    if 'error' in response:
        error = response['error']
        raw = call_preview.revert_data(error)
        message = error.get('message', '') if isinstance(error, dict) else str(error)
        preview = {'status': 'reverted' if raw or 'revert' in message.lower() else 'rpc_error',
                   'error': error, 'decoded': call_preview.explain_revert(raw)}
    else:
        raw = call_preview.calldata(response.get('result', 'INVALID'))
        preview = {'status': 'succeeded', 'return_data': raw,
                   'decoded': call_preview.decode_result(raw, result_type)}
    end = proxy_route.rpc(endpoint, 'eth_getBlockByNumber', [block, False])
    if int(end['number'], 16) != routing['block_number'] or end['hash'] != routing['block_hash']:
        raise ValueError('Block identity changed after call; discard and retry')
    return {'status': 'observed', 'sent': False, 'endpoint': endpoint,
            'observations': observations, 'routing': routing, 'sources': sources,
            'preview': {'block_number': routing['block_number'], 'transaction': transaction, **preview},
            'limits': 'No safety verdict. Source verification is provider-reported and not block-pinned. '
                      'Routing indicators may not dispatch; beacon implementations are unresolved. '
                      'No sender, value, or state overrides; future transactions can differ.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--address', type=call_preview.address, default=call_preview.ZTO)
    parser.add_argument('--data', type=call_preview.calldata, default='0x18160ddd')
    parser.add_argument('--result-type', choices=['raw', 'uint256', 'bool', 'address'], default='raw')
    parser.add_argument('--endpoint', action='append')
    args = parser.parse_args()
    endpoints = args.endpoint or rpc_health.DEFAULTS
    if any(not url.startswith('https://') for url in endpoints):
        parser.error('endpoints must use HTTPS')
    try:
        report = preflight(args.address, args.data, endpoints, args.result_type)
        print(json.dumps(report, indent=2))
        return 0 if report['status'] == 'observed' and report['preview']['status'] != 'rpc_error' else 1
    except (ValueError, OSError, KeyError, TypeError, argparse.ArgumentTypeError) as error:
        print(json.dumps({'status': 'error', 'sent': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
