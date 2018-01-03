#!/usr/bin/env python
#Use python CacheSim.py -help for help.
#Simple Cache Simulator that takes in block size, cache size, cachetype, associativity and filename as an command line argument.
#Each object has an object for storing dirty and tag bit in case of write.


#TO-DO: improve the main function and make it more general for unified and split.

import sys
import argparse
# import math

class Status():                                         #Class to store dirty bit of a specific tag and rewrite it.

    def __init__(self):
        self.tag = 0
        self.dirty = False
        self.lrucount = 0

    def write(self, tag):
        self.dirty = True
        self.lrucount = 0
        self.tag = tag

class CacheB():                                          #Class to read, write, replace block.
    def __init__(self, assoc):
        self.status = [Status() for _ in range(assoc)]   #Create status objects as per associativity.

    def readwrite(self, tag, operation):
        status = self.getstatus(tag)
        if status is None or not status.dirty:
            self.replace(tag)
            return False
        else:
            if (operation == 'r'):
                status.lrucount = 0
            if (operation == 'w'):
                status.write(tag)
            for status in self.status:
                status.lrucount += 1            
            return True

    def replace(self, tag):
        maxlrublock = self.status[0]
        for status in self.status:
            if status.lrucount > maxlrublock.lrucount:
                maxlrublock = status
        maxlrublock.write(tag)
        for status in self.status:
            status.lrucount += 1

    def getstatus(self, tag):
        for status in self.status:
            if status.tag == tag:
                return status
        return None


def main():

    #get the arguments from command line
    parser = argparse.ArgumentParser(description='Simple Cache Simulator.')

    parser.add_argument("-filename", dest = "filename", required=True, help="Trace File")
    parser.add_argument("-l1-cachetype", dest = "CacheType", required = True, help="'u' for Unified, 's' for Seperate")
    parser.add_argument("-l1-isize", dest = "iCacheSize", type= int, help="Size of L1 Instruction Cache")
    parser.add_argument("-l1-dsize", dest = "dCacheSize", type= int, help="Size of L1 Data Cache")
    parser.add_argument("-l1-iassoc", dest = "iAssoc", type= int, help="Associativity of L1 Instruction Cache")
    parser.add_argument("-l1-dassoc", dest = "dAssoc", type= int, help="Associativity of L1 Data Cache")
    parser.add_argument("-l1-ibsize", dest = "iBlockSize", type= int, help="Size of Instruction Cache Block")
    parser.add_argument("-l1-dbsize", dest = "dBlockSize", type= int, help="Size of Data Cache Block")
    parser.add_argument("-l1-usize", dest = "uCacheSize", type= int, help="Size of Unified Cache")
    parser.add_argument("-l1-ubsize", dest = "uBlockSize", type= int, help="Size of Unified Cache Block")
    parser.add_argument("-l1-uassoc", dest = "uAssoc", type= int, help="Associativity of Unified Cache")

    #checking for unified or split cache.
    #create a CacheB object for every cacheblock as per cache type.
    args = parser.parse_args()
    if (args.CacheType == 'u'):                                                     
        way = int(args.uAssoc)  
        clines = [CacheB(way) for i in range(int(args.uCacheSize)/int(args.uBlockSize))]
    elif (args.CacheType == 's'):
        way = int(args.dAssoc)  
        clinesd = [CacheB(way) for i in range(int(args.dCacheSize)/int(args.dBlockSize))]
        way = int(args.iAssoc)
        clinesi = [CacheB(way) for i in range(int(args.iCacheSize)/int(args.iBlockSize))]

    #variable initialization
    readaccesses = writeaccesses = cachemiss = lrucounter  = tag = totalaccesses = datacachemiss = intcachemiss = 0 

    #reading the trace file.
    with open(args.filename, 'rb') as tracefile:
        num_accesses = num_misses = 0
        for line in tracefile:
            if line.strip() == '':                                                  #handling empty lines. skip if found.
                continue
            label = int(line[0] )                                                   #Get Operation Label.
            address = int(line[2:].strip(),16)                                      #Get memory address in decimals.
            if args.CacheType is "u":                                               #Operation for Unified Cache.
                way = int(args.uAssoc)                                              #Get the number of associativity.
                noofblocks = int(args.uCacheSize)/int(args.uBlockSize)              #Get no of cache lines.
                noofsets = noofblocks/way                                           #Get no of sets.
                if None in (args.uAssoc, args.uBlockSize, args.uCacheSize):         #Check if all arguments needed are passed.
                    sys.exit("Error, pass all the arguments for Unified Cache")
                else:
                    totalaccesses += 1
                    mainmemoryblock = address//int(args.uBlockSize)                 #find the memory block corresponding to the address.
                    cacheline = mainmemoryblock%noofsets                            #find the cacheline where the memory block will go
                    tag = mainmemoryblock//noofsets                                 #get the tag of the memory block.
                    block = clines[cacheline]                                       #get the object file of the cacheline.
                    if label == 0 or label == 2:                                    #for reading data or fetching instruction
                        if not block.readwrite(tag, 'r'):                           
                            cachemiss += 1
                    if label == 1:
                        if not block.readwrite(tag, 'w'):
                            cachemiss += 1

            if args.CacheType is "s":
                if None in (args.iAssoc, args.dAssoc, args.iBlockSize, args.dBlockSize, args.iCacheSize, args.dCacheSize):
                    sys.exit("Error, pass all arguments for Seperate Cache")
                else:
                    totalaccesses += 1
                    if label == 0 or label == 1:                                       #data cache
                        way = int(args.dAssoc)  
                        noofblocks = int(args.dCacheSize)/int(args.dBlockSize)
                        noofsets = noofblocks/way
                        mainmemoryblock = address//int(args.dBlockSize)
                        cacheline = mainmemoryblock%noofsets
                        tag = mainmemoryblock//noofsets                               
                        block = clinesd[cacheline]
                        if not block.readwrite(tag, 'r'):
                            datacachemiss += 1

                    if label == 2:                                                      #instruction cache
                        way = int(args.iAssoc) 
                        noofblocks = int(args.iCacheSize)/int(args.iBlockSize)
                        noofsets = noofblocks/way
                        mainmemoryblock = address//int(args.iBlockSize)
                        cacheline = mainmemoryblock%noofsets
                        tag = mainmemoryblock//noofsets
                        block = clinesi[cacheline]
                        if not block.readwrite(tag, 'r'):
                            intcachemiss += 1

        if args.CacheType is "s":
            print "Total accesses - %d Inst cachemiss - %d Data cachemiss - %d" %(totalaccesses, intcachemiss, datacachemiss)
        if args.CacheType is "u":
            print "Total accesses - %d cachemiss - %d" %(totalaccesses, cachemiss)

if __name__ == "__main__":
    main()