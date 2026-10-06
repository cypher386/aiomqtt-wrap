# main
if (__name__ == '__main__'):
    import sys
    import argparse
    import ssl
    import asyncio
    import aiomqtt
    from .aiomqtt_wrap import _parse_args, aiomqtt_wrap_main
    options = _parse_args(sys.argv)
    if options['dump_options']:
        print(options)
    else:
        asyncio.run(aiomqtt_wrap_main(options, topic=options['topic'], 
                                      message = options['message']))
    print("Done\n")
