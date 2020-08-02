import sys
import subprocess as subproc
from string import Template
from functools import partial
from cbutil import Path,URL

from fxpkg import *

open_console = partial(subproc.Popen,args = ['cmd'], stdin = subproc.PIPE, stdout = sys.stdout, shell =True, text = True)

self_path = Path(__file__)

def get_url(version) -> URL:
    ver_nums = version.split('.')
    if len(ver_nums) == 2:
        ver_nums.append(0)
    ver_nums_s = list(map(str,ver_nums))
    version = '.'.join(ver_nums_s)
    name_suffix = '_' + '_'.join(ver_nums_s)
    url = f'https://dl.bintray.com/boostorg/release/{version}/source/boost{name_suffix}.zip'
    return URL(url)

class MainPort(FxPort):
    info = PortInfo(
        name = 'boost'
    )

    default_config = dict(
        version='1.73',
    )

    def make_default_libconfig(self, config: LibConfig = None) ->LibConfig:
        default_config = self.default_config
        for k,v in default_config.items():
            if not hasattr(config, k) or getattr(config, k) == None:
                setattr(config, k, v)
        return config

    def complete_libconfig(self, config: LibConfig) ->LibConfig:
        self.host.complete_libconfig(config,self)
        return config

    def install(self, config: LibConfig) -> LibConfig:
        self.lib_config = config
        self.download()
        self.extract_src()
        self.build()
        return config

    def download(self):
        config = self.lib_config
        url = get_url(config.version)
        self.download_file_path = dst_path = config.download_path/url.name
        if dst_path.exists():
            return
        save_path = Path(str(dst_path)+'.downloading')
        url.download(save_path=save_path, continuous=True)
        save_path.rename(dst_path)
        self.download_file_path = dst_path
            
    def extract_src(self):
        config = self.lib_config
        src_path = config.src_path
        complte_stamp_path = src_path/'extract_complete.stamp'
        if complte_stamp_path.exists():
            return
        src_path.remove_sons()
        self.download_file_path.unzip(src_path)
        config.src_path.sons[0].move_all_out()
        with complte_stamp_path.open('w'): pass

    def build(self):
        config = self.lib_config
        build_temp_path = self_path.prnt/'boost_build_cmd.template.txt'
        build_temp = Template(build_temp_path.read_text())
        install_path = self.port_config.install_path
        build_bat = build_temp.substitute(
            src_path=config.src_path.str,
            install_path = install_path.str,
            log_path = config.log_path.str
            )
        build_bat_path = self_path.prnt/'boost_build_cmd.bat'
        build_bat_path.write_text(build_bat)

        install_path.mkdir()
        config.log_path.mkdir()
        with subproc.Popen(build_bat_path.str, stdout = subproc.PIPE) as proc:
            proc.wait()