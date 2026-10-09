# main
if __name__ == "__main__":
    import asyncio
    import sys

    import yaml

    from .aiomqtt_wrap import _parse_args, aiomqtt_wrap_recv, aiomqtt_wrap_send


    try:
        with open("wrap.conf") as f:
            cfg_options = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        cfg_options: dict=None

    cmd_options = _parse_args(sys.argv, cfg_options)

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
    elif cmd_options["action"] == "send":
        asyncio.run(
            aiomqtt_wrap_send(
                cmd_options, topic=cmd_options["topic"],
                message=cmd_options["message"]
            )
        )
    
    elif (cmd_options["action"] == "receive") | (cmd_options["action"] == "subscribe"):
        asyncio.run(
            aiomqtt_wrap_recv(
                cmd_options, topic=cmd_options["topic"]
            )
        )
  
