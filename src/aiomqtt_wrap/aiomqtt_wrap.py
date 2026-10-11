#!/usr/bin/env python
"""
AIOMQTT depends on aiomqtt which depends on MQTT5 (rust+python bindings)
the sender expects a options list with the default options

default options  {
    'host': 'localhost',
    'port': 1883,
    'mode': 'tcp',
    'user': 'user',
    'pass': 'password',
    'insecure': False,
    'topic': 'test/test',
    'message': 'test message',
    'dump_options': false,
    'dump_conf': false,
    'action' : ['send'], ['receive'], ['subscribe']
}

"""

import argparse
import asyncio
import logging
import ssl
import sys

import aiomqtt
import yaml

qosmap = [
    aiomqtt.QoS.AT_MOST_ONCE,
    aiomqtt.QoS.AT_LEAST_ONCE,
    aiomqtt.QoS.EXACTLY_ONCE
]

logger = logging.getLogger(__name__)

async def aiomqtt_wrap_send(options: dict, topic: str, message: str) -> None:
    """options dict topic and message
    options for host port user and pass are required
    option['mode'] will default to tcp
    topic and message are required
    """

    logging.basicConfig(filename='aiomqtt.log', level=logging.DEBUG)
    logger.info('Started in async_wrap_send')

    if isinstance(message, str):
        message = message.encode("utf8")

    if "mode" not in options:
        options["mode"] = "tcp"

    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

    if options["insecure"]:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    if options["mode"] == "tcp":
        context = None

    async with aiomqtt.Client(
        hostname=options["host"],
        port=options["port"],
        username=options["user"],
        password=options["password"].encode('utf8'),
        ssl_context=context,
        #qos=aiomqtt.QoS.AT_MOST_ONCE,
        #session_expiry_interval=600,
        #reconnect=True,
        #clean_start=False,
        #logger = logger
    ) as client:
        await client.publish(topic, message, qos=aiomqtt.QoS.AT_MOST_ONCE)
        #await client.publish(topic, message)


async def consume(client: aiomqtt.Client) -> None:
    #async for message in client.messages():
    while True:
        try:
            async for message in client.messages():
                print(message.payload)
        except aiomqtt.ConnectError:
            await client.connected()
        print(message.payload)

async def aiomqtt_wrap_recv(options: dict, topic: str) -> None:
    """options dict topic and message
    options for host port user and pass are required
    option['mode'] will default to tcp
    topic and messages queue are required
    """
    logging.basicConfig(filename='aiomqtt.log', level=logging.DEBUG)
    logger.info('Started in async_wrap_recv')

    if "mode" not in options:
        options["mode"] = "tcp"

    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

    if options["insecure"]:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    if options["mode"] == "tcp":
        context = None

    async with aiomqtt.Client(
        hostname=options["host"],
        port=options["port"],
        username=options["user"],
        password=options["password"].encode('utf8'),
        ssl_context=context,
        session_expiry_interval=600,
        reconnect=True,
        clean_start=True,
        logger = logger
    ) as client:
        #await client.subscribe(topic, max_qos=aiomqtt.QoS.AT_MOST_ONCE)
        await client.subscribe(topic, max_qos=aiomqtt.QoS.AT_MOST_ONCE)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(consume(client))
#            tg.create_task(asyncio.sleep(5))  # Some other task

       
    #while True:
    #    try:
    #        async for message in client.messages():
    #            print(message.payload)
    #    except aiomqtt.ConnectError:
    #        await client.connected()




def _parse_args(argv: list, cfg:dict | None) -> dict:
    """parse default command line optins"""

    def_opt = {
        "host": "localhost",
        "port": 1883,
        "mode": "tcp",
        "user": "user",
        "password": "password",
        "insecure": False,
        "topic": "test/test",
        "message": "test message",
        "dump_options": False,
        "dump_yaml": False,
        "action": "send",
        "qos": 0
    }
    try:
        for k, value in cfg.items():
            def_opt[k]=value
    except TypeError:
        pass
        

    parser = argparse.ArgumentParser(
        description="Wrap asyncio-mqtt parameters",
        add_help=False,
        usage="%(prog)s [options]",
        epilog="",
    )
    parser.add_argument(
        "-h",
        "--host",
        default=def_opt["host"],
        help="hostname to connect to defaults to %{default}",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=def_opt["port"],
        help="tcp port to connect to"
    )
    parser.add_argument(
        "-m",
        "--mode",
        "--proto",
        default=def_opt["mode"],
        choices=["tcp", "tls", "ws", "wss"],
        help="protocol type %{choices}",
    )
    parser.add_argument(
        "-u",
        "--user",
        "--username",
        default=def_opt["user"],
        help="username to connect with",
    )
    parser.add_argument(
        "--password", default=def_opt["password"],
        help="password to connect with"
    )
    parser.add_argument(
        "-i",
        "--insecure",
        action="store_true",
        default=def_opt["insecure"],
        help="Do not validiate host certificate"
    )
    parser.add_argument("-t", "--topic", default=def_opt["topic"],
                        help="MQTT Topic")
    parser.add_argument("--message", default=def_opt["message"],
                        help="MQTT Message")
    parser.add_argument(
        "-a",
        "--action",
        choices=["send", "receive", "subscribe", "none"],
        required=True,
        default=def_opt["action"],
        help="Select action %{choices} to act on Topic and Message",
    )
    parser.add_argument(
        "--qos",
        type=int,
        choices=[0, 1, 2],
        default=def_opt["qos"],
        help="Select qos %{choices} for mqtt messages",
    )
    parser.add_argument(
        "--dump_options",
        "--options",
        "--dump",
        action="store_true",
        default=def_opt["dump_options"],
        help="dump command line default options",
    )
    parser.add_argument(
        "--dump_yaml",
        "--dump_config",
        action="store_true",
        default=def_opt["dump_yaml"],
        help="Dump config options in yaml format",
    )

    args = parser.parse_args(argv[1::])
    return vars(args)


# main
if __name__ == "__main__":
    try:
        with open("wrap.conf") as f:
            cfg_options = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        cfg_options: dict=None

    cmd_options = _parse_args(sys.argv, cfg_options)
  
    cfg_options["qos"] = qosmap[cfg_options["qos"]]
    
   

    if cmd_options["dump_options"]:
        print(cmd_options)
    elif cmd_options["dump_yaml"]:
        if cfg_options:
            yaml_dump = yaml.dump(cfg_options, default_flow_style=False)
            print(yaml_dump)
        else:
            print(
                "no config file exists\n dumping default options in yaml",
                file=sys.stderr,
            )
            print(yaml.dump(cmd_options, default_flow_style=False))
    else:
        # merge config and command line
        asyncio.run(
            aiomqtt_wrap_send(
                cmd_options, topic=cmd_options["topic"],
                message=cmd_options["message"]
            )
        )
    
