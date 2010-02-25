from supybot.commands import *
import supybot.callbacks as callbacks


def dameraulevenshtein(seq1, seq2):
    """Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.

    >>> dameraulevenshtein('ba', 'abc')
    2
    >>> dameraulevenshtein('fee', 'deed')
    2

    It works with arbitrary sequences too:
    >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
    2

    From http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]

def levenshtein_distance(first, second):
    """
    Find the Levenshtein distance between two strings.
    By Stavros

    From http://www.korokithakis.net/node/87
    """
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
       distance_matrix[i][0] = i
    for j in range(second_length):
       distance_matrix[0][j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

class Levenshtein(callbacks.Privmsg):
    def levenshtein(self, irc, msg, args):
        """<string> <string>

        Calculates the Levenshtein distance between any two strings.
        """
        if len(args) != 2:
            irc.reply("usage: levenshtein <string> <string>", prefixNick=True)
            return
        distance = levenshtein_distance(args[0], args[1])
        answer = "The Levenshtein distance between %s and %s is %s." % \
            (args[0], args[1], distance)

        irc.reply(answer, prefixNick=True)

    def damlev(self, irc, msg, args):
        """<string> <string>

        Calculates the Damerau-Levenshtein distance between any two strings.
        """
        if len(args) != 2:
            irc.reply("usage: damlev <string> <string>", prefixNick=True)
            return
        distance = dameraulevenshtein(args[0], args[1])
        answer = "The Damerau-Levenshtein distance between %s and %s is %s." % \
            (args[0], args[1], distance)

        irc.reply(answer, prefixNick=True)

Class = Levenshtein

