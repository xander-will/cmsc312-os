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
    TOTAL_MEM = PHYSICAL_MEM + VIRTUAL_MEM

    def __init__(self):
        self.page_table = [Page()] * self.TOTAL_MEM
        self.phys = [None] * self.PHYSICAL_MEM
        self.virt = [None] * self.VIRTUAL_MEM
        self.lock = Lock()

    def remaining(self):
        return self.phys.count(None) + self.virt.count(None)
    
    def full(self):
        return False if None in self.phys and None in self.virt else False

    def allocate(self, size):
        with self.lock:
            DebugPrint("[Memory] Entering memory alloc")
            if self.full():
                raise ex.MemoryAllocationError

            page_list = list()
            for page in self.page_table:
                if page.location is None:
                    table = self.phys if self.phys.count(None) else self.virt
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

    def findLeastUsed(self):
        min = self.phys[0]
        for page in self.phys:
            if page.counter < min.counter:
                min = page

        return page

    def access(self, page_list):
        with self.lock:
            for page in page_list:
                page.counter = time()
                if page.location is self.virt:
                    swap_p = self.findLeastUsed()
                    self.phys[self.phys.index(swap_p)] = page
                    self.virt[self.virt.index(page)] = swap_p

                    swap_p.location = self.virt
                    page.location = self.phys

memory = Memory()


