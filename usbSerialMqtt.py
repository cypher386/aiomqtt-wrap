#!/usr/bin/env python

import os
import ssl
import json
import asyncio
import aiomqtt
import serial
import serial_asyncio

"""
    python serial json to mqtt


"""

featherrfm69_var = [
    "X",
    "Y",
    "Z",
    "TVOC",
    "eCO2",
    "Temp",
    "RH",
    "TAP",
    "HF"
]


class EnvInfo():
    """ load Environment into dict """
    def __init__(self, args=[], kwargs={}):
        for k in args:
            for k in args:
                self.__setattr__(k, os.environ.get(k, ""))
            for key, func in kwargs.items():
                self.__setattr__(key, func(os.environ.get(key, "")))
    def __repr__(self):
        return f"{self.__dict__}"
    def __str__(self):
        return f"{self.__dict__}"
    def get_dict(self):
        return self.__dict__



class ReadLines(asyncio.Protocol):
    """ read serial in chunks send mqtt on newline """
    def connection_made(self, transport):
        """Store the serial transport and prepare to receive data.
        """
        self.transport = transport
        self.transport.serial.rts = False  # You can manipulate Serial object via transport
        self.buf = bytes()

        print('Reader connection created')

    def data_received(self, data):
        """Store characters until a newline is received.
        """
        self.buf += data
        if b'\n' in self.buf:
            lines = self.buf.split(b'\n')
            self.buf = lines[-1]  # whatever was left over
            for line in lines[:-1]:
                json_data = json.loads(line)
                print(f'received: {json_data}')
#                async with aiomqtt.Client(hostname="localhost", port=1884, username="skynet",
#                              password=b"loveiggies") as client:
#                    await client.publish("skynet/home/door", json.dumps(json_data,
#                                         sort_keys=True).encode('utf-8'))


    def connection_lost(self, exc):
        print('Reader closed')


#async def Reader():
#    """  Reader asyncio function """
#    transport, protocol = await serial_asyncio.create_serial_connection(loop,
#                            InputChunkProtocol, '/dev/cuaU0', baudrate=115200)
#
#    while True:
#        await asyncio.sleep(0.3)
#        protocol.resume_reading()


# main
if __name__ == '__main__':
    print(featherrfm69_var)
    loop = asyncio.get_event_loop()
    serial_data = serial_asyncio.create_serial_connection(loop, ReadLines(),
                                                            '/dev/cuaU0', baudrate=115200)
    transport, protocol = loop.run(serial_data)
    #loop.run(ReadLines())
    #loop.close()
    #asyncio.run(mqtt_writer())
