from cbutil import Path,URL
from string import Template

import sys
import subprocess as subproc
from functools import partial
from fxpkg import Package

open_console = partial(subproc.Popen,args = ['cmd'], stdin = subproc.PIPE, stdout = sys.stdout, shell =True, text = True)

self_path = Path(sys.path[0])

def get_url(version):
    ver_nums = version.split('.')
    if len(ver_nums) == 2:
        ver_nums.append(0)
    ver_nums_s = list(map(str,ver_nums))
    version = '.'.join(ver_nums_s)
    name_suffix = '_' + '_'.join(ver_nums_s)
    url = f'https://dl.bintray.com/boostorg/release/{version}/source/boost{name_suffix}.zip'
    return url

class MainPkg(Package):
    def begin(self, config):
        self.config = config
        self.download_path = Path(self.config.download_path)
        self.src_path = Path(self.config.src_path)
        self.install_path = Path(self.config.install_path)
        self.lib_path = self.install_path/'lib'
        self.inc_path = self.install_path/'inc'
        self.cmake_path = self.install_path/'cmake'
        self.download_url = url = URL(get_url('1.73'))
        self.download_file_path = self.download_path/url.name

    def download(self):
        self.download_url.download(self.download_file_path, continuous=True)

    def extract_src(self):
        self.download_file_path.unzip(self.src_path)
        self.src_path.sons[0].move_all_out()

    def build(self):
        build_temp_path = self_path/'boost_build_cmd.template.txt'
        build_temp = Template(build_temp_path.read_text())
        build_bat = build_temp.substitute(
            src_path=self.src_path.to_str(),
            install_path = self.install_path.to_str(),
            lib_path = self.lib_path.to_str(),
            inc_path = self.inc_path.to_str(),
            cmake_path = self.cmake_path.to_str()
            )
        build_bat_path = self_path/'boost_build_cmd.bat'
        build_bat_path.write_text(build_bat)
        with subproc.Popen(build_bat_path.to_str(), stdout = subproc.PIPE) as proc:
            proc.wait()
        

    def install(self):
        pass

    def end(self):
        '''return information'''
        pass