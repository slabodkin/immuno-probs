# ImmunoProbs Python package able to calculate the generation probability of
# V(D)J and CDR3 sequences. Copyright (C) 2018 Wout van Helvoirt

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


import re as regex

import numpy
import pandas

from immuno_probs.util.conversion import string_array_to_list


def extract_best_aligns(aligns_df):
    """Extracts alignments with highest score from the provided alignments
    dataframe.

    """
    mask = aligns_df.groupby('seq_index').agg({'score': 'idxmax'})  # get /!\ FIRST /!\ index of max align score for each sequence
    aligns_df_best = aligns_df.loc[mask['score']].reset_index(drop=True)
    return aligns_df_best


def get_misinsdel_asarray(misinsdel_str):
    """Convert a string with comma separated mismatches indices to an array
    of integers.

    """
    return string_array_to_list(misinsdel_str, dtype=int, l_bound='{', r_bound='}')


def read_alignments(filename):
    """Reads IGoR's alignments file as a panda DataFrame."""
    aligns = pandas.read_csv(filename, delimiter=';')
    # Convert the string of insertions into an array of integers
    tmp = aligns.apply(lambda x: get_misinsdel_asarray(x.insertions), axis=1)
    aligns.insertions = tmp
    # Convert the string of deletions into an array of integers
    tmp = aligns.apply(lambda x: get_misinsdel_asarray(x.deletions), axis=1)
    aligns.deletions = tmp
    # Convert the string of mismatches into an array of integers
    tmp = aligns.apply(lambda x: get_misinsdel_asarray(x.mismatches), axis=1)
    aligns.mismatches = tmp

    return aligns


def read_best_alignments(filename):
    """Reads IGoR's top score alignments from file as a panda DataFrame."""
    # Not efficient just faster to code
    aligns = pandas.read_csv(filename, delimiter=';')
    aligns = extract_best_aligns(aligns)

    # Convert the string of insertions into an array of integers
    tmp = aligns.insertions.apply(get_misinsdel_asarray)
    aligns.insertions = tmp
    # Convert the string of deletions into an array of integers
    tmp = aligns.deletions.apply(get_misinsdel_asarray)
    aligns.deletions = tmp
    # Convert the string of mismatches into an array of integers
    tmp = aligns.mismatches.apply(get_misinsdel_asarray)
    aligns.mismatches = tmp

    return aligns


# Import genomic template sequences
def read_fasta_strings(filename):
    """Returns a dictionary whose entry keys are sequence labels and values
    are sequences.

    """
    seq = regex.compile('>')
    line = regex.compile('\n')
    with open(filename) as f:
        tmp = seq.split(f.read())
        final = {}
        for i in range(1, len(tmp)):
            split_seq = line.split(tmp[i])
            final[split_seq[0]] = split_seq[1].upper()
        return final


def has_mismatches(x):
    """Assess whether the SW alignment contains mismatches. Because IGoR's
    inference module uses mismatches outside the best SW alignment, not all
    reported mismatches are contained in the SW alignment. This function
    filters them before assessing whether the actual SW alignment contains any
    mismatch.

    """
    tmp = numpy.asarray(x.mismatches)
    return any(numpy.multiply(tmp >= x["5_p_align_offset"],
                              tmp <= x["3_p_align_offset"]))