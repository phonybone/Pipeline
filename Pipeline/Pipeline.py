import os, tempfile, logging
from .exceptions import *
import networkx as nx

config_file=os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'logging.conf'))
import logging.config
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
        self.pipelines=[]
        self.commands=[]

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

    def add_cmd(self, cmd):
        self.commands.append(cmd)
        setattr(self, cmd.name, cmd)
        return self

    def add_cmds(self, *cmds):
        self.commands.extend(cmds)
        return self

    def find_command(self, cmd_name):
        for c in self.commands:
            if c.name==cmd_name: return c
        for p in self.pipelines:
            c=p.find_command(cmd_name)
            if c: return c
        return None

    def add_pipeline(self, other_pipeline):
        self.pipelines.append(other_pipeline)
        setattr(self, other_pipeline.name, other_pipeline)

    def _run_cmds(self, *cmds):
        if len(cmds)==0:
            cmds=self.commands

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


    def _run_cmd(self, cmd):
            retcode=cmd.run()
            if retcode != 0:
                self.log.info('%s failed (retcode=%s), throwing exception' % (cmd.name, retcode))
                raise CmdFailed(cmd)
        

    def _create_output_dir(self):
        try:
            with tempfile.TemporaryFile(dir=self.output_dir) as tmp:
                tmp.write('testing')
        except OSError, e:
            os.mkdir(self.output_dir) # fixme: could still fail...
            self.log.info('output_dir: %s created' % self.output_dir)

    def graph(self):
        '''
        construct a graph representation of the pipeline
        each file is a node
        each command is a node
        
        '''
        import networkx as nx
        g=nx.DiGraph()

        for p in self.pipelines:
#            g.add_edges_from(p.graph().edges())
            pg=p.graph()
            for e in pg.edges():
                d=pg.get_edge_data(e[0],e[1])
                g.add_edge(e[0],e[1], **d)

        for cmd in self.commands:
            for in_fn in cmd.inputs():
#                print 'adding %-30s consumes %s' % (cmd.name, in_fn)
                g.add_edge(cmd.name, in_fn, type='consumes')
            for out_fn in cmd.outputs():
#                print 'adding %-30s creates  %s' % (cmd.name, out_fn)
                g.add_edge(cmd.name, out_fn, type='creates')
        return g

    def check_continuity(self):
        if not nx.is_connected(self.graph().to_undirected()):
            raise ContinuityError(self)
        return True
