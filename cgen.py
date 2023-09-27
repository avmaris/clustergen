#! dynamically executable python3.7
# -*- coding: utf-8 -*-

""" Python templating engine with Jinja2 for generating
    slurm cluster installation scripts generation.
"""
import os
import shutil
import argparse
import json
import time
import datetime
import random
import string

from stat import *
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.utils import generate_lorem_ipsum
generationtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

script_path = os.path.realpath(__file__)
destinationroot = os.path.dirname(script_path)

class TemplateUtils:
    @staticmethod
    def true_example_condition(arg):
        return True
      
class TemplateProcessing:
    def __init__(self, rootpath, content):
        self.content = content
        self.root = rootpath
        # Target Jinja2 template
        # Output file name generated automatically,
        #  by removing extension of target template if output_file not defined
        self.templates = {
            'install.sh': {
                'template_file': 'install.sh.j2',
                'destination_path': '{root}/',
                'permissions': (S_IWUSR | S_IWGRP | S_IXUSR | S_IXGRP
                                | S_IXOTH | S_IRUSR | S_IRGRP | S_IROTH)
            },
            'hosts': {
                'template_file': 'hosts.j2',
                'output_file': 'example_hosts',
                'destination_path': '{root}/',
            },
            'README.txt.j2': {'template_file': 'README.txt.j2'},
            'mungekey': {
                'template_file': 'munge.key.j2',
                'destination_path': '{root}/../clustercfg/'
            },
            'slurmconf': {
              'destination_path': '{root}/../clustercfg/',
              'template_file': 'slurm.conf.j2'
            },
            'cgroupconf': {
              'destination_path': '{root}/../clustercfg/',
              'template_file': 'cgroup.conf.j2'
            },
            'SLURM_installation': {
                'template_file': 'SLURM_installation.sh.j2',
                'destination_path': '{root}/',
                'permissions': (S_IWUSR | S_IWGRP | S_IXUSR | S_IXGRP
                                | S_IXOTH | S_IRUSR | S_IRGRP | S_IROTH),
                'condition': TemplateUtils.true_example_condition(content)
            },
            'buildslurm_sh': {
                'template_file': 'buildslurm.sh.j2',
                'destination_path': '{root}/',
                'permissions': (S_IWUSR | S_IWGRP | S_IXUSR | S_IXGRP
                                | S_IXOTH | S_IRUSR | S_IRGRP | S_IROTH)
            }
        }

    def get_destination_path(self):
        return self.root

    def get_template_file(self, template):
        # Get permission of output file
        template_record = self.templates.get(template)
        template_file = template_record.get('template_file', None)
        if not template_file:
            raise Exception("template_file is mandatory in :", template)
        return template_file

    def get_permissions(self, template):
        # Get output file permissions
        return self.templates.get(template, {}).get('permissions', None)

    def get_codition(self, template):
        # If no condition at the template then all return True
        return self.templates.get(template, {}).get('condition', True)
            
    def get_absolute_path(self, path):
        # Get absolute path
        return os.path.abspath(path)
    
    def get_filename(self, template):
        # Get output file name
        # Build output file name if not specify in a record
        template_file = self.get_template_file(template)
        no_extention = os.path.splitext(template_file)[0]

        template_record = self.templates.get(template)
        output_file_name = template_record.get('output_file', no_extention)

        return output_file_name

    def destinationpath(self, template):
        """Build a path for curent product file, based on input arguments."""
        template_record = self.templates.get(template)
        destination = template_record.get('destination_path', '{root}/')
        input_arguments = locals()
        destination_path = destination.format(root=self.root,
                                              **input_arguments)
        path = destination_path + self.get_filename(template)
        return path

    def template_processing(self, outputfile, template):
        """Render template into a file."""

        # Use directory of current script for loads templates
        processing_script_dir=os.path.realpath(os.path.dirname(__file__))

        loader = FileSystemLoader(processing_script_dir)
        # Set processing enviroments
        # trim_blocks - first newline after a block is removed
        # lstrip_blocks - remove empty space from the start of a line to a block
        jinja_env = Environment(loader=loader,
                                trim_blocks=True,
                                lstrip_blocks=True)
        jinja_template = jinja_env.get_template(template)
        generationtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Render a template using a dictionary to pass in arguments

        
        jinja_process_context = dict(time=time,
                                    datetime=datetime,
                                    generationtime=generationtime,
                                    content=self.content,
                                    os=os,
                                    random=random,
                                    string=string)
        try:
            jinja_template.stream(jinja_process_context).dump(outputfile)
        except Exception as e:
            errstr = "Template '{}' processing fail:\n  | {}".format(template, e)
            raise Exception(errstr)

    def processing(self):
        """Main processing method."""

        for template in self.templates:

            if (not self.get_codition(template)):
                continue
            
            outputfile = self.destinationpath(template)

            # Create folder for a output file
            makedirfolder(outputfile)
            # Template processing
            templatedir = "./templates/"
            templatepath = templatedir + self.get_template_file(template)
            
            self.template_processing(outputfile,
                                     templatepath)
            # Set permissions of generated file
            if self.get_permissions(template):
                os.chmod(
                    outputfile, self.get_permissions(template))

def get_vec_path(root, node_name):
    return root + "/" + node_name

# Get package version
def version():
  return "0.1.1"
  
def arguments_parse():
    """Returns parsed arguments as dictionary
    """

    parser = argparse.ArgumentParser(
        description='Generation scripts for cluster initialization.')
    
    parser.add_argument('--version', '-v', action='version',
                    version=version())
    parser.add_argument('--cluster', '-i',
                        required=True,
                        help='Path to cluster in json format')
    parser.add_argument('--destination', '-d',
                        default='./build/',
                        help='Output directory path for application.')
    parser.add_argument('--force', '-f',
                        action='store_true',
                        help='Overwrite existing application.')
    args = parser.parse_args()

    returndict = dict()

    return args


def jsonfile2dict(path):
    """Convert input json file to dictionary.
    """
    with open(path, 'r') as json_file:
        data = json.load(json_file)
        return data

def clrdestination(destination, forcerm):

    if os.path.isdir(destination) and os.listdir(destination):
        if forcerm:
            shutil.rmtree(destination)
        else:
            raise Exception("Destination not empty.")

# Validation of cluster structure
def validate(json_data):
  return True

def makedirfolder(target_path):
    """Make folder for target file."""

    destloc = os.path.dirname(target_path)
    if not os.path.isdir(destloc):
        os.makedirs(destloc)


def main():
    # Processing
    parsdict = arguments_parse()

    json_data = jsonfile2dict(parsdict.cluster)
    validate(json_data)
    parsdict.destination = parsdict.destination + "/scripts"
    clrdestination(parsdict.destination, parsdict.force)

    templateprocessing = TemplateProcessing(rootpath=parsdict.destination,
                                            content=json_data)
    templateprocessing.processing()
    try:
        pass
    except Exception as e:
        print(e)
        exit(-1)

if __name__ == "__main__":
    main()
