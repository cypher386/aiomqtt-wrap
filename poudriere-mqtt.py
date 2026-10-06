#!/usr/bin/env python
"""
    python mqtt to wayland notify of poundriere buils


    Poudriere os enviroment variables.
    BUILD_URL 	URL for the build.
	BUILDNAME 	The configured (${BUILDNAME_FORMAT}) build name.
	LOG_URL 	URL for the logs.
	LOG 	Path to log directory for the build.
	POUDRIERE_BUILD_TYPE 	Currently always bulk
	POUDRIERE_DATA 	Path to configured /usr/local/poudriere/data.
	POUDRIERED 	Path to configured /usr/local/etc/poudriere.d.
	JAILNAME 	The configured jail name.
	PTNAME 	The configured ports tree name.
	SETNAME 	The configured set name (from -z)
	MASTERNAME 	Master Jail name, i.e. JAILNAME-PTNAME-SETNAME
	MASTERMNT 	Path to the master reference jail. This is cloned for each builder.
	PACKAGES 	Path to the packages directory for this build. If ATOMIC_PACKAGE_REPOSITORY 
                is enabled then this will be a symlinked subdir of PACKAGES_ROOT.
	PACKAGES_ROOT 	Path to the packages top-level directory.
	MY_JOBID 	The job id of the current builder. In 3.5+ this is deprecated in favor of MY_BUILDER_ID.
 	MY_BUILDER_ID 	The builder id of the current builder.
 	VERBOSE 	0 or greater to note how many -v were used.

"""

import os
import sys
import argparse
import ssl
import json
import asyncio
import aiomqtt
#import aiomqtt_wrap
from aiomqtt_wrap import aiomqtt_wrap_main

mqtt_opts = {
    'host': 'mqtt.tail69a033.ts.net',
	'port': 8883,
	'mode': 'tls',
	'user': 'poudriere',
	'pass': 'FreeBSD',
	'insecure': False,
	'topic': 'skynet/freebsd/poudriere',
	'message': 'test message'
}

poudriere_var = [
    "BUILD_URL",
	"BUILDNAME",
	"LOG_URL",
	"LOG",
	"POUDRIERE_BUILD_TYPE",
	"POUDRIERE_DATA",
	"POUDRIERED",
	"JAILNAME",
	"PTNAME",
	"SETNAME",
	"MASTERNAME",
	"MASTERMNT",
	"PACKAGES",
	"PACKAGES_ROOT",
	"MY_JOBID",
 	"MY_BUILDER_ID",
 	"VERBOSE"
]


class EnvInfo():
    """ read env """
    def __init__(self, args=[], kwargs={}):
        for k in args:
            for k in args:
                self.__setattr__(k, os.environ.get(k, ""))
            for key, func in kwargs.items():
                self.__setattr__(key, func(os.environ.get(key, "")))
    def __repr__(self):
        """ return repr """
        return f"{self.__dict__}"
    def __str__(self):
        """ return string repr """
        return f"{self.__dict__}"
    def get_dict(self):
        """ return dict from attributes """
        return self.__dict__



async def main(env_obj) -> None:
    """ post messages """
    async with aiomqtt.Client(hostname="localhost", port=1884, username="poudriere",
                              password=b"FreeBSD") as client:
        await client.publish("skynet/freebsd/poudriere", json.dumps(env_obj.get_dict(),
                                                                    sort_keys=True).encode('utf-8'))

# main
if __name__ == '__main__':
    p_env = EnvInfo(poudriere_var)
    #print(p_env)
    print(json.dumps(p_env.get_dict(), sort_keys=True))
    message = json.dumps(p_env.get_dict(), sort_keys=True).encode('utf-8')
    asyncio.run(aiomqtt_wrap_main(mqtt_opts, topic=mqtt_opts['topic'], message=message))

    
