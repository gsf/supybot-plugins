# integer number to english word conversion
# can be used for numbers as large as 999 vigintillion
# (vigintillion --> 10 to the power 60)
# tested with Python24      vegaseat      07dec2006

def int2word(n):
    """
    convert an integer number n into a string of english words
    """
    # break the number into groups of 3 digits using slicing
    # each group representing hundred, thousand, million, billion, ...
    n3 = []
    r1 = ""
    # create numeric string
    ns = str(n)
    for k in range(3, 33, 3):
        r = ns[-k:]
        q = len(ns) - k
        # break if end of ns has been reached
        if q < -2:
            break
        else:
            if  q >= 0:
                n3.append(int(r[:3]))
            elif q >= -1:
                n3.append(int(r[:2]))
            elif q >= -2:
                n3.append(int(r[:1]))
        r1 = r
    
    #print n3  # test
    
    # break each group of 3 digits into
    # ones, tens/twenties, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100)//10
        b3 = (x % 1000)//100
        #print b1, b2, b3  # test
        if x == 0:
            continue  # skip
        else:
            t = thousands[i]
        if b2 == 0:
            nw = ones[b1] + t + nw
        elif b2 == 1:
            nw = tens[b1] + t + nw
        elif b2 > 1:
            nw = twenties[b2] + ones[b1] + t + nw
        if b3 > 0:
            nw = ones[b3] + "hundred " + nw
    return nw

############# globals ################

ones = ["", "one ","two ","three ","four ", "five ",
    "six ","seven ","eight ","nine "]

tens = ["ten ","eleven ","twelve ","thirteen ", "fourteen ",
    "fifteen ","sixteen ","seventeen ","eighteen ","nineteen "]

twenties = ["","","twenty ","thirty ","forty ",
    "fifty ","sixty ","seventy ","eighty ","ninety "]

thousands = ["","thousand ","million ", "billion ", "trillion ",
    "quadrillion ", "quintillion ", "sextillion ", "septillion ","octillion ",
    "nonillion ", "decillion ", "undecillion ", "duodecillion ", "tredecillion ",
    "quattuordecillion ", "sexdecillion ", "septendecillion ", "octodecillion ",
    "novemdecillion ", "vigintillion "]

if __name__ == '__main__':
    # select an integer number n for testing or get it from user input
    #n = 4321234567890
    #n = 1111111111111
    #n = 1234567890123
    n = 1001000100100111
    #n = 1
    
    print n
        
    print "-"*50
    print int2word(n)
    print "-"*50
