from supybot.commands import *
import supybot.callbacks as callbacks


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

        Calculates the levenshtein distance between any two strings
        """
        if len(args) != 2:
            irc.reply("usage: levenshtein <string> <string>", prefixNick=True)
            return
        distance = levenshtein_distance(args[0], args[1])
        answer = "The levenshtein distance between %s and %s is %s." % \
            (args[0], args[1], distance)

        irc.reply(answer[0], prefixNick=True)

Class = Levenshtein

