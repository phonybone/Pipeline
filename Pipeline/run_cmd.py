import os, sys, subprocess, tempfile, logging, time
from datetime import datetime
from lazy import lazy

class RunCmd(object):
    '''
    Abstract class to launch a shell command, then wait for it to finish (a lot like 
    os.system()).  
    Subclasses must define:
    get_cmd()
    get_args()

    And may override:
    get_envion()
    '''

    @lazy
    def _ts(self):
        return datetime.now()

    _ts_format='%Y%b%d.%H.%m.%S'

    def __init__(self, name, pipeline, skip_if_current=False):
        self.name=name
        self.pipeline=pipeline
        self.skip_if_current=skip_if_current

    log=logging.getLogger('Pipeline')

    def run(self):
        self.log.info('****** running %s *********' % self.name)
        os.chdir(self.pipeline.working_dir) 
        self.log.debug("chdir\'d to %s" % self.pipeline.working_dir)

        is_current=self.is_current()
        self.log.debug('skip_flag: %s; %s.is_current: %s' % (self.skip_if_current, self.name, is_current))
        if self.skip_if_current and is_current:
            msg='# %s: is up-to-date, skipping' % self.name
            self.log.info(msg)
            if self.pipeline.echo:
                print msg
            return 0            # success!
        
        if self.pipeline.dry_run or self.pipeline.echo:
            print '# %s' % self.name
            print self.cmd_string()
            print
            if self.pipeline.dry_run:
                (self.pid, self.status)=(-1,-1)
                self.log.info('dry_run is True: bye!')
                return 0            # success!
        
        self.log.info(self.cmd_string())


        # put in something about checking for readability of all input files...

        new_stdout=open(self.get_stdout(), 'w')
        new_stderr=open(self.get_stderr(), 'w')

        cmd=[self.get_cmd()]
        cmd.extend(self.get_args())
        retcode=subprocess.call(cmd, env=self._build_environ(),
                                stdout=new_stdout, stderr=new_stderr,
                                )
        self.log.info('%s: retcode=%d' % (self.name, retcode))
        new_stdout.close()      # don't know if these are necessary or not...
        new_stderr.close()      # ...but they don't seem to hurt

        self.retcode=retcode
        return retcode



        # could put something here about provenance

    def cmd_string(self):
        stuff=[self.get_cmd()]
        stuff.extend(self.get_args())
        return ' '.join(stuff)

    def _build_environ(self):
        try: env=self.get_envrion()
        except AttributeError: env={}
        env.update({'HOME':os.environ['HOME'],
                    'USER':os.environ['USER'],
                    })

        env.update(self.pipeline.host.environ())
        return env

#    def outputs(self):
#        return []

    def is_current(self):
        if len(self.outputs())==0: return False
        self.log.debug('check1')
        if len(self.inputs())==0: return False
        self.log.debug('check2')
        
        try:
            last_updated=max([int(os.path.getmtime(fn)) for fn in self.inputs()])
            self.log.debug('check3: last_updated=%s (%s)' % (last_updated, time.ctime(last_updated)))
        except OSError, e:
            self.log.debug('check4 returning False: %s' % e)
            return False        # one of the inputs probably doesn't exist


        # check that all of our outputs exist, and
        #       that each is newer than the most recent input
        for out in self.outputs():
            if not os.path.exists(out):
                self.log.debug('check5 returning False: %s does not exist' % out)
                return False
            out_updated=int(os.path.getmtime(out))
            self.log.debug('out_updated: %s' % out_updated)
            if out_updated < last_updated:
                self.log.debug('check6 returning False: %s out of date' % out)
                return False

        self.log.debug('check7: %s.is_current()=True' % self.name)
        return True
        
    def __get_output_fn(self, fn_type):
        return os.path.join(self.pipeline.output_dir,
                            '%s.%s.%s' % (self.name, self._ts.strftime(self._ts_format), fn_type))

    def get_stdout(self):
        ''' return the name of the file to which to redirect stdout '''
        return self.__get_output_fn('stdout')
                            
    def get_stderr(self):
        ''' return the name of the file to which to redirect stderr '''
        return self.__get_output_fn('stderr')

    def inputs(self): return []
    def outputs(self): return []
