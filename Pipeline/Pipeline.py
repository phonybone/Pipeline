import os, tempfile, logging
from .exceptions import *

config_file=os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'logging.conf'))
print 'config_file is %s' % config_file
logging.config.fileConfig(config_file,
                          disable_existing_loggers=False,
                          )

class Pipeline(object):
    log=logging.getLogger(__name__)

    def __init__(self, name, host, working_dir, 
                 dry_run=False, output_dir=None, echo=False, skip_if_current=False):
        self.name=name
        self.host=host
        self.working_dir=working_dir
        self.output_dir=output_dir or working_dir
        self.dry_run=dry_run
        self.echo=echo
        self.skip_if_current=skip_if_current

    def __repr__(self):
        return 'Pipeline %s: host=%s working_dir=%s output_dir=%s dry_run=%s echo=%s skip=%s' % (
            self.name, 
            self.host,
            self.working_dir,
            self.output_dir,
            self.dry_run,
            self.echo,
            self.skip_if_current,
            )

    def run(self):
        raise AbstractMethodNotImplementedException('Pipeline.Pipeline.run')

    def _run_cmd(self, cmd):
            retcode=cmd.run()
            if retcode != 0:
                self.log.info('%s failed (retcode=%s), throwing exception' % (cmd.name, retcode))
                raise CmdFailed(cmd)
        
    def _run_cmds(self, *cmds):
        try:
            for cmd in cmds:
                self._run_cmd(cmd)
        except CmdFailed, e:
            try: retcode=e.run_cmd.retcode
            except: retcode=None
            self.log.error("this failed (retcode=%s):\n%s" % (retcode, e.run_cmd.cmd_string()))
            self.log.error("Envrionment:")
            for k,v in e.run_cmd._build_environ().items():
                self.log.error("env: %s: %s" % (k,v))
            self.log.error("see %s for details" % e.run_cmd.get_stderr())
            raise PipelineFailed(self, cmd, e)


    def _create_output_dir(self):
        try:
            with tempfile.TemporaryFile(dir=self.output_dir) as tmp:
                tmp.write('testing')
        except OSError, e:
            os.mkdir(self.output_dir) # fixme: could still fail...
            self.log.info('output_dir: %s created' % self.output_dir)
