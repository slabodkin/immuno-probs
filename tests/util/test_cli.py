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


"""Test file for testing immuno_probs.util.cli file."""

import argparse

import pytest

from immuno_probs.util.cli import dynamic_cli_options


@pytest.mark.parametrize(
    'options, commandline_input, expected',
    [
        (
            {
                'input':
                {
                    'metavar': 'I',
                    'type': 'str',
                    'help': 'Test input file'
                },
                'output':
                {
                    'metavar': 'O',
                    'type': 'str',
                    'help': 'Test output file'
                },
                'choice':
                {
                    'metavar': 'C',
                    'type': 'str',
                    'choices': ['A', 'B', 'C'],
                    'help': 'Test of some choices'
                },
                '--option-1':
                {
                    'type': 'int',
                    'nargs': '?',
                    'default': 1,
                    'help': "Test option 1 (default: 1)"
                },
                '--option-2':
                {
                    'type': 'int',
                    'nargs': '*',
                    'help': "Test option 2"
                }
            },
            [
                'test/input/location',
                'B',
                'test/output/location',
                '--option-1',
                '2',
                '--option-2',
                '5',
                '10'
            ],
            [
                'test/input/location',
                'test/output/location',
                'B',
                2,
                [5, 10]
            ]
        )
    ]
)
def test_dynamic_cli_parser(options, commandline_input, expected):
    """Test if the parser creates the arguments properly.

    Parameters
    ----------
    options : dict
        A Python dict with key being the full name of the option. The value is
        a kwargs dict that corresponds to input arguments of the
        ArgumentParser.add_argument function. Note: type argument values must be
        surrounded by quotes.
    commandline_input : list
        A list containing commandline inputs.
    expected : list
        Containing the expected option input values.

    Raises
    -------
    AssertionError
        If the performed test failed.

    """
    parser = argparse.ArgumentParser()
    parser = dynamic_cli_options(parser=parser, options=options)
    parsed_arguments = parser.parse_args(commandline_input)
    assert parsed_arguments.input == expected[0]
    assert parsed_arguments.output == expected[1]
    assert parsed_arguments.choice == expected[2]
    assert parsed_arguments.option_1 == expected[3]
    assert parsed_arguments.option_2 == expected[4]
