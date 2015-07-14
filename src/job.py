"""defines Job classes:
    Job: atomic class
    JobList: Job set
    JobGroup: container which can contains JobGroups and JobLists"""

from bisect import bisect_left
from collections import Counter
from functools import total_ordering

import constants


@total_ordering
class Job:
    """Job class with hash and comparison based on job id"""

    def __init__(self, job_xml, args):
        """create a job with the xml 'joblist' tree"""

        from misc import time_handler

        self.dct = {}
        for itm, itmtp in constants.itms.items():
            self.dct[itm] = ''
            for tag in itmtp.xml_tag:
                elts = job_xml.iter(tag)
                self.dct[itm] = ', '.join(sorted(elt.text for elt in elts
                                                 if elt.text))
                if self.dct[itm]:
                    break

        self.dct['i'] = int(self.dct['i'])
        self.idt = dct['i']

        if self.dct['k']:
            self.dct['q'], self.dct['d'] = self.dct['k'].rsplit('@')

        self.dct['t'], self.dct['e'] = time_handler(self.dct['t'],
                                                    args.start_format,
                                                    args.elapsed_format)

    def __hash__(self):
        """hash based on job id"""
        return hash(self.idt)

    def __eq__(self, other):
        """comparison based on job id"""
        return isinstance(other, self.__class__) and self.idt == other.idt

    def __lt__(self, other):
        """comparison based on job id"""
        return isinstance(other, self.__class__) and self.idt < other.idt

    def get(self, itm):
        """get job propriety"""
        return self.dct[itm]

    def rep(self, fmt):
        """representation of job based on format fmt"""
        return fmt.format(**self.dct)


class JobList:
    """JobList class which handle the width of the different
    fields and the job counting for total"""

    def __init__(self, job_list):
        """constructor expects a list of Job"""
        self.jobset = sorted(set(job_list))
        self.njobs = len(self.jobset)
        self.width = {}
        self.total = {}
        for itm in constants.itms:
            self.width[itm] = sorted(len(str(job.get(itm)))
                                     for job in self.jobset)
            self.total[itm] = Counter(str(job.get(itm))
                                      for job in self.jobset)

    def add(self, new_job):
        """add a job, update width and total, and erase the previous
        existing one with the same id if needed"""

        # will need to recompute completely the elapsed time due to its
        # volatile nature...

        idx = bisect_left(self.jobset, new_job)
        old_job = self.jobset[idx]

        if new_job == old_job:
            for itm in constants.itms:
                jitm = str(old_job.get(itm))
                lgt = len(jitm)
                wlist = self.width[itm]
                del wlist[bisect_left(wlist, lgt)]

                self.total[itm] -= Counter([jitm])
            del self.jobset[idx]

        for itm in constants.itms:
            jitm = str(new_job.get(itm))
            lgt = len(jitm)
            wlist = self.width[itm]
            wlist.insert(bisect_left(wlist, lgt), lgt)

            self.total[itm] += Counter([jitm])

        self.jobset.insert(idx, new_job)

    def rep(self, fmt):
        """handles the representation of the entire list"""
        # will have to work a bit on the format to put the width of the fields
        # will have to sort jobset
        # replace output.out
        for job in self.jobset:
            print(job.rep(fmt))

    def rep_tot(self, tot_list, fmt):
        """handles the representation of the totals"""
        # will need args.total -> tot_list
        pass


class JobGroup:
    pass
