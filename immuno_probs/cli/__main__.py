# Create IGoR models and calculate the generation probability of V(D)J and
# CDR3 sequences. Copyright (C) 2019 Wout van Helvoirt

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Executable for running functions located in immuno_probs.cli directory."""


import argparse
import os
import sys
import tempfile
from shutil import rmtree

from immuno_probs.cli.build_igor_model import BuildIgorModel
from immuno_probs.cli.generate_sequences import GenerateSequences
from immuno_probs.cli.extract_file_sequences import ExtractFileSequences
from immuno_probs.cli.evaluate_sequences import EvaluateSequences
from immuno_probs.cli.locate_cdr3_anchors import LocateCdr3Anchors
from immuno_probs.util.cli import dynamic_cli_options, make_colored
from immuno_probs.util.constant import set_num_threads, set_separator, \
set_working_dir, set_out_name, set_config_data, get_config_data
from immuno_probs.util.io import create_directory_path


def main():
    """Function to create the ArgumentParser containing the sub-options."""
    # Create the parser with general commands and set the subparser.
    description = 'Create IGoR models and calculate the generation ' \
        'probability of V(D)J and CDR3 sequences.'
    parser_general_options = {
        '-separator': {
            'type': 'str',
            'nargs': '?',
            'help': 'The separator character used for input files and for ' \
                    'writing new files (default: tab character).'
        },
        '-threads': {
            'type': 'int',
            'nargs': '?',
            'help': 'The number of threads the program is allowed to use ' \
                    '(default: max available threads in system).'
        },
        '-set-wd': {
            'type': 'str',
            'nargs': '?',
            'help': 'An optional location for writing files (default: ' \
                    'the current working directory).'
        },
        '-out-name': {
            'type': 'str',
            'nargs': '?',
            'help': 'An optional output file name. If multiple files are ' \
                    'created, the value is used as a prefix for the file ' \
                    '(default: none).'
        },
        '-config-file': {
            'type': 'str',
            'nargs': '?',
            'help': 'An optional configuration file path for ImmunoProbs. ' \
                    'This file is always combined with the default ' \
                    'configuration to make up missing values (default: none).'
        },
    }
    parser = argparse.ArgumentParser(prog='immuno-probs',
                                     description=description)
    parser = dynamic_cli_options(parser=parser, options=parser_general_options)
    subparsers = parser.add_subparsers(help='Supported immuno-probs options, ' \
        'command plus help displays more information for the option.',
                                       dest='subparser_name')

    # Add main- and suboptions to the subparser.
    efs = ExtractFileSequences(subparsers=subparsers)
    lca = LocateCdr3Anchors(subparsers=subparsers)
    bim = BuildIgorModel(subparsers=subparsers)
    ges = GenerateSequences(subparsers=subparsers)
    evs = EvaluateSequences(subparsers=subparsers)

    # Parse the commandline arguments and set variables.
    parsed_arguments = parser.parse_args()
    try:
        if parsed_arguments.config_file is not None:
            set_config_data(parsed_arguments.config_file)
        if parsed_arguments.separator is not None:
            set_separator(parsed_arguments.separator)
        if parsed_arguments.threads is not None:
            set_num_threads(parsed_arguments.threads)
        if parsed_arguments.set_wd is not None:
            set_working_dir(parsed_arguments.set_wd)
        if parsed_arguments.out_name is not None:
            set_out_name(parsed_arguments.out_name)
    except (TypeError, ValueError, IOError) as err:
        sys.stdout.write(make_colored('error\n', 'red'))
        sys.stderr.write(make_colored(str(err), 'bg-red'))
        return

    # Create the directory paths for temporary files.
    try:
        output_dir = get_config_data('WORKING_DIR')
        if get_config_data('USE_SYSTEM_TEMP', option_type='bool'):
            temp_dir = create_directory_path(
                os.path.join(tempfile.gettempdir(), get_config_data('TEMP_DIR')))
        else:
            temp_dir = create_directory_path(
                os.path.join(output_dir, get_config_data('TEMP_DIR')))
        set_working_dir(temp_dir)
    except IOError as err:
        sys.stdout.write(make_colored('error\n', 'red'))
        sys.stderr.write(make_colored(
            'Cannot create ImmunoProbs working directory ({})\n'.format(err),
            'bg-red'))
        return

    # Execute the correct tool based on given subparser name.
    if parsed_arguments.subparser_name == 'locate':
        lca.run(args=parsed_arguments, output_dir=output_dir)
    elif parsed_arguments.subparser_name == 'extract':
        efs.run(args=parsed_arguments, output_dir=output_dir)
    elif parsed_arguments.subparser_name == 'build':
        bim.run(args=parsed_arguments, output_dir=output_dir)
    elif parsed_arguments.subparser_name == 'generate':
        ges.run(args=parsed_arguments, output_dir=output_dir)
    elif parsed_arguments.subparser_name == 'evaluate':
        evs.run(args=parsed_arguments, output_dir=output_dir)
    else:
        sys.stdout.write("No option selected, run 'immuno-probs -h' to show all options.\n")

    # Finally, delete the temporary directory.
    rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
