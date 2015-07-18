#!PYTHON_CMD
"""qjobs is a qstat wrapper designed to get a better output."""

import sys


def main():
    """execute qstat and produces output according to chosen options."""

    from datetime import datetime
    from subprocess import Popen, PIPE
    import xml.etree.ElementTree as ET

    import cmdargs
    import constants
    from job import Job, JobList, JobGroup

    args = cmdargs.parse()
    if args.items:
        print(*('{}: {}'.format(k, v.dscr) for k, v in constants.itms.items()),
              sep='\n')
        sys.exit()

    if args.file:
        qstat_out = args.file
    else:
        qstat_out = Popen(args.qstat_cmd +
                          ' -u "' + args.users + '" -xml -r',
                          shell=True, stdout=PIPE).stdout

    qstat_out = ET.parse(qstat_out).getroot().iter('job_list')

    alljobs = []
    today = datetime.today()
    for j in qstat_out:
        alljobs.append(Job(j, args, today))

    if not alljobs:
        if not args.mute:
            print('No pending or running job.')
    else:
        alljobs = JobList(alljobs, args)

        out_gen = (alljobs.rep(), alljobs.rep_tot())
        for line in out_gen[args.reverse]:
            print(line)

        if args.out and args.total:
            print()

        for line in out_gen[not args.reverse]:
            print(line)


if __name__ == '__main__':

    try:
        main()
    except Exception as excpt:

        from configparser import NoSectionError, MissingSectionHeaderError

        if excpt not in (SystemExit, NoSectionError,
                         MissingSectionHeaderError):
            import logging
            from tempfile import NamedTemporaryFile

            tmpf = NamedTemporaryFile(prefix='qjobs', suffix='.log',
                                      delete=False)
            tmpf.close()
            logging.basicConfig(filename=tmpf.name, level=logging.DEBUG)
            logging.exception('qjobs exception log:')
            print('ERROR! Please check', tmpf.name, 'for more information.')
            sys.exit()
        raise
