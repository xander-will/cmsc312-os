from threading import Lock
from time import time

import src.exceptions as ex

from src.globals import DebugPrint

class Page:
    def __init__(self):
        self.counter = 0
        self.location = None

class Memory:
    PHYSICAL_MEM = 4096
    VIRTUAL_MEM = 8192
    CACHE_MEM = 40
    TOTAL_MEM = PHYSICAL_MEM + VIRTUAL_MEM + CACHE_MEM

    def __init__(self):
        self.page_table = [Page()] * self.TOTAL_MEM
        self.cache = [None] * self.CACHE_MEM
        self.phys = [None] * self.PHYSICAL_MEM
        self.virt = [None] * self.VIRTUAL_MEM
        self.lock = Lock()

    def remaining(self):
        return self.phys.count(None) + self.virt.count(None)
    
    def full(self):
        return False if None in self.phys and None in self.virt else True

    def allocate(self, size):
        with self.lock:
            DebugPrint("[Memory] Entering memory alloc")
            if size > self.remaining():
                raise ex.MemoryAllocationError

            page_list = list()
            for page in self.page_table:
                if page.location is None:
                    if None not in self.phys:
                        if None not in self.virt:
                            table = self.cache
                        else:
                            table = self.virt
                    else:
                        table = self.phys
                    index = table.index(None)
                    table[index] = page
                    page.location = table
                    page_list.append(page)
                if len(page_list) == size:
                    break

        return page_list

    def deallocate(self, page_list):
        with self.lock:
            for page in page_list:
                index = page.location.index(page)
                page.location[index] = None
                page.location = None

    def findLeastUsed(self, table):
        min = table[0]
        for page in table:
            if page.counter < min.counter:
                min = page

        return page

    def access(self, page_list):
        with self.lock:
            start_page = page_list[0]
            start_loc = start_page.location
            if start_loc is not self.cache:
                swap_p = self.findLeastUsed(self.cache)
                self.cache[self.cache.index(swap_p)] = start_page
                start_loc[start_loc.index(start_page)] = swap_p
                swap_p.location = start_loc
                start_page.location = self.cache

            for page in page_list:
                page.counter = time()
                if page.location is self.virt:
                    swap_p = self.findLeastUsed(self.phys)
                    self.phys[self.phys.index(swap_p)] = page
                    self.virt[self.virt.index(page)] = swap_p
                    swap_p.location = self.virt
                    page.location = self.phys

memory = Memory()


