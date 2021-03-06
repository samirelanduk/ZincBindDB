"""Contains functions for dealing with chains and chain sequences."""

import subprocess
import re

def get_all_chains(sites):
    """Takes a list of site dicts, and gets all chains with unique IDs."""

    chains = set()
    for site in sites:
        for chain in site["chains"]:
            if chain.id not in [c.id for c in chains]:
                chains.add(chain)
    return chains


def get_all_residues(sites):
    """Gets all residues from a list of sites."""

    residues = set()
    for site in sites:
        residues.update(site["residues"])
    return residues


def get_chain_sequence(chain, residues):
    """Gets a chain's sequence as it should appear in the database - all
    lowercase but with certain residues (those given) in upper case."""

    full = "".join(res.code for res in chain)
    alignment = align_sequences(full, chain.sequence)
    seq, indices, dash_count = "", [], 0
    for i, char in enumerate(alignment[0]):
        if char == "-":
            dash_count += 1
        elif chain[i - dash_count].id in [r.id for r in residues]:
            indices.append(i)
    for i, char in enumerate(chain.sequence):
        seq += char.upper() if i in indices else char.lower()
    return seq


def match_score(alpha, beta, match_award, mismatch_penalty, gap_penalty):
    """Adapted from github.com/alevchuk/pairwise-alignment-in-python/"""

    if alpha == beta:
        return match_award
    elif alpha == "-" or beta == "-":
        return gap_penalty
    else:
        return mismatch_penalty


def align_sequences(seq1, seq2):
    """Adapted from github.com/alevchuk/pairwise-alignment-in-python/"""

    match_award      = 10
    mismatch_penalty = -5
    gap_penalty      = -5
    m, n = len(seq1), len(seq2)
    score = [[0 for y in range(n + 1)] for x in range(m + 1)]
    for i in range(0, m + 1): score[i][0] = gap_penalty * i
    for j in range(0, n + 1): score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(
             seq1[i-1], seq2[j-1], match_award, mismatch_penalty, gap_penalty
            )
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)
    align1, align2 = "", ""
    i, j = m, n
    while i > 0 and j > 0:
        score_current = score[i][j]
        score_diagonal = score[i-1][j - 1]
        score_up = score[i][j - 1]
        score_left = score[i - 1][j]
        if score_current == score_diagonal + match_score(
         seq1[i-1], seq2[j-1], match_award, mismatch_penalty, gap_penalty
        ):
            align1 += seq1[i - 1]
            align2 += seq2[j - 1]
            i -= 1
            j -= 1
        elif score_current == score_left + gap_penalty:
            align1 += seq1[i - 1]
            align2 += "-"
            i -= 1
        elif score_current == score_up + gap_penalty:
            align1 += "-"
            align2 += seq2[j - 1]
            j -= 1
    while i > 0:
        align1 += seq1[i - 1]
        align2 += "-"
        i -= 1
    while j > 0:
        align1 += "-"
        align2 += seq2[j - 1]
        j -= 1
    return align1[::-1], align2[::-1]


def get_all_chains_fasta():
    """Gets the text of a FASTA file representing all chains in the database."""

    from core.models import Chain
    lines = []
    for chain in Chain.objects.all():
        lines.append(">lcl|" + str(chain.id))
        sequence = chain.sequence
        while sequence:
            lines.append(sequence[:80])
            sequence = sequence[80:]
    return "\n".join(lines)


def get_chain_clusters(sequence_identity):
    """Uses the CD-Hit binary to cluster chains into chain clusters, and returns
    these clusters as lists of chain IDs."""
    
    subprocess.call(
     "cd-hit -i chains.fasta -d 0 -o temp -c {} -n 5 -G 1 -g 1 -b 20 -s 0.0 -aL "
     "0.0 -aS 0.0 -T 4 -M 32000".format(sequence_identity),
     shell=True, stdout=subprocess.PIPE
    )
    with open("temp.clstr") as f: data = f.read()
    clusters = data.split(">Cluster ")[1:]
    clusters = [re.compile(r">(.+?)\.\.\.").findall(c) for c in clusters]
    return [[chain.split("|")[1] for chain in cluster] for cluster in clusters]
