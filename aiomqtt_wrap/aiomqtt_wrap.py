#!/usr/bin/env python
"""
    AIOMQTT depends on aiomqtt which depends on MQTT5 (rust+python bindings)
    the sender expects a options list with the default options

    default options
    options = { 
        'host': 'localhost', 
        'port': 1883,
        'mode': 'tcp',
        'user': 'user',
        'pass': 'password',
        'insecure': False,
        'topic': 'skynet/test',
        'message': 'test message',
        'dump_options': True
    }

"""

import sys
import argparse
import ssl
import asyncio
import aiomqtt

async def aiomqtt_wrap_main(options: dict, topic: str, message: str) -> None:
    """ options dict topic and message 
    options for host port user and pass are required
    option['mode'] will default to tcp
    topic and message are required
    """

    if type(message) == str:
        message=message.encode('utf8')

    if "mode" not in options:
        options['mode'] = 'tcp'

    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    #context = load_verify_locations('/etc/ssl/cert.pem')
    if options['insecure']:
        context.check_hostname = False
        context.verify_mode=ssl.CERT_NONE
        
    if options['mode'] == 'tcp':
        async with aiomqtt.Client(hostname=options['host'], port=options['port'], 
                                 username=options['user'], 
                                 password=options['pass'].encode('utf8') ) as client:
            await client.publish(topic, message)
    
    if options['mode'] == 'tls':
        async with aiomqtt.Client(hostname=options['host'], port=options['port'], 
                                  username=options['user'], 
                                  password=options['pass'].encode('utf8'),
                                  ssl_context = context ) as client:
            await client.publish(topic, message)
    #print("Completed")

def _parse_args(argv: list) -> dict:
    """ parse default command line optins """
    parser = argparse.ArgumentParser(description='test mqtt publish',
                                    add_help=False, 
                                    usage='%(prog)s [options]',
                                    epilog='')
    parser.add_argument('-h', '--host', default='localhost',
                       help='hostname to connect to defaults to localhost')
    parser.add_argument('-p', '--port', type=int, default='1883',
                       help='tcp port to connect to')
    parser.add_argument('-m', '--mode', '--proto', default='tcp', 
                        help='protocol type tcp, tls')
    parser.add_argument('-u', '--user', '--username', default="poudriere",
                        help='username to login with')
    parser.add_argument('--pass', '--password', default="FreeBSD",
                        help='username to login with')
    parser.add_argument('-i', '--insecure', action='store_true', default=False,
                        help='Ignore TLS validation')
    parser.add_argument('-t', '--topic', default='skynet/test',
                        help='MQTT Topic')
    parser.add_argument('--message', default='test message',
                        help='MQTT Message')
    parser.add_argument('--dump_options', '--options', '--dump', action='store_true', 
                        default=False, help="Default Options")
    
    args=parser.parse_args(argv[1::])
    return vars(args)

# main
if (__name__ == '__main__'):
    options = _parse_args(sys.argv)
    if options['dump_options']:
        print(options)
    else:
        asyncio.run(aiomqtt_wrap_main(options, topic=options['topic'], 
                                      message = options['message']))
    print("Done\n")
