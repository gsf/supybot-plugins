from __future__ import generators
from types import UnicodeType
import traceback
import sys
import array

convertArray = []
dConvert = {}

if len(convertArray) == 0:
  append = convertArray.append
  for x in range(65535):
    append('')

  convertArray[ord(u'\u2070')] = '0'
  convertArray[ord(u'\u2080')] = '0'
  convertArray[ord(u'\u00b9')] = '1'
  convertArray[ord(u'\u2071')] = '1'
  convertArray[ord(u'\u2081')] = '1'
  convertArray[ord(u'\u00b2')] = '2'
  convertArray[ord(u'\u2072')] = '2'
  convertArray[ord(u'\u2082')] = '2'
  convertArray[ord(u'\u00b3')] = '3'
  convertArray[ord(u'\u2073')] = '3'
  convertArray[ord(u'\u2083')] = '3'
  convertArray[ord(u'\u2074')] = '4'
  convertArray[ord(u'\u2084')] = '4'
  convertArray[ord(u'\u2075')] = '5'
  convertArray[ord(u'\u2085')] = '5'
  convertArray[ord(u'\u2076')] = '6'
  convertArray[ord(u'\u2086')] = '6'
  convertArray[ord(u'\u2077')] = '7'
  convertArray[ord(u'\u2087')] = '7'
  convertArray[ord(u'\u2078')] = '8'
  convertArray[ord(u'\u2088')] = '8'
  convertArray[ord(u'\u2079')] = '9'
  convertArray[ord(u'\u2089')] = '9'
  convertArray[ord(u'\u03b1')] = 'a'      #alpha
  convertArray[ord(u'\u0391')] = 'A'	
  convertArray[ord(u'\u03b2')] = 'b'      #beta
  convertArray[ord(u'\u0392')] = 'B'
  convertArray[ord(u'\u03b3')] = 'g'      #gamma
  convertArray[ord(u'\u0393')] = 'G'
  convertArray[ord(u'\u00c6')] = 'ae'     #ae digraph
  convertArray[ord(u'\u00e6')] = 'ae'
  convertArray[ord(u'\u0152')] = 'oe'     #oe digraph
  convertArray[ord(u'\u0153')] = 'oe'
  convertArray[ord(u'\u0110')] = 'd'      #crossed d, eth
  convertArray[ord(u'\u0111')] = 'd'
  convertArray[ord(u'\u00f0')] = 'd'
  convertArray[ord(u'\u0131')] = 'i'      #turkish (small dotless) i
  convertArray[ord(u'\u2113')] = 'l'      #script l, polish l
  convertArray[ord(u'\u0141')] = 'l'
  convertArray[ord(u'\u0142')] = 'l'
  convertArray[ord(u'\u01a0')] = 'o'      #hooked o, slashed o
  convertArray[ord(u'\u01a1')] = 'o'
  convertArray[ord(u'\u00d8')] = 'o'
  convertArray[ord(u'\u00f8')] = 'o'
  convertArray[ord(u'\u00de')] = 'th'     #icelandic thorn
  convertArray[ord(u'\u00fe')] = 'th'   
  convertArray[ord(u'\u01af')] = 'u'      #hooked u
  convertArray[ord(u'\u01b0')] = 'u'
  convertArray[ord(u'\u266f')] = '#'      #musical sharp
  convertArray[ord(u'\u266d')] = 'F'      # musical flat
  ### chars to delete
  convertArray[ord('\'')] = ''
  convertArray[ord('|')] = ''
  convertArray[ord('[')] = ''
  convertArray[ord(']')] = ''
  ### chars to convert to blanks
  convertArray[ord(u'\u00ae')] =  ' '  # patent sign
  convertArray[ord(u'\u2117')] =  ' '  # phonorecord symbol
  convertArray[ord(u'\u00a9')] =  ' '  # copyright symbol
  convertArray[ord(u'\u00b1')] =  ' '  # plus and minus
  convertArray[ord(u'\u00a3')] =  ' '  # british pound
  convertArray[ord(u'\u207a')] =  ' '  # superscript/subscript + - ( )
  convertArray[ord(u'\u208a')] =  ' '  # 
  convertArray[ord(u'\u207b')] =  ' '  #
  convertArray[ord(u'\u208b')] =  ' '  #
  convertArray[ord(u'\u207d')] =  ' '  #
  convertArray[ord(u'\u207e')] =  ' '  #
  convertArray[ord(u'\u208d')] =  ' '  #
  convertArray[ord(u'\u208e')] =  ' '  #
  convertArray[ord(' ')] = ' '
  convertArray[ord(',')] = ','     
  convertArray[ord('!')] = ' '
  convertArray[ord('\"')] = ' '
  convertArray[ord('$')] = ' '
  convertArray[ord('%')] = ' '
  convertArray[ord('-')] = ' '
  convertArray[ord('.')] = ' '
  convertArray[ord('/')] = ' '
  convertArray[ord('\\')] = ' '
  convertArray[ord(':')] = ' '
  convertArray[ord(';')] = ' '
  convertArray[ord('<')] = ' '
  convertArray[ord('=')] = ' '
  convertArray[ord('>')] = ' '
  convertArray[ord('^')] = ' '
  convertArray[ord('_')] = ' '
  convertArray[ord('`')] = ' '
  convertArray[ord('~')] = ' '
  convertArray[ord('(')] = ' '
  convertArray[ord(')')] = ' '
  convertArray[ord('{')] = ' '
  convertArray[ord('}')] = ' '
  convertArray[ord('?')] = ' '
  convertArray[ord('*')] = ' '
  convertArray[ord('@')] = ' '
  convertArray[ord(u'\u00b0')] = ' '    # degree sign
  convertArray[ord(u'\u00bf')] = ' '    # inverted question mark
  convertArray[ord(u'\u00a1')] = ' '    # inverted exclamation mark
  convertArray[ord('#')] = '#'
  convertArray[ord('&')] = '&'
  convertArray[ord('+')] = '+'
  convertArray[ord('0')] = '0'
  convertArray[ord('1')] = '1'
  convertArray[ord('2')] = '2'
  convertArray[ord('3')] = '3'
  convertArray[ord('4')] = '4'
  convertArray[ord('5')] = '5'
  convertArray[ord('6')] = '6'
  convertArray[ord('7')] = '7'
  convertArray[ord('8')] = '8'
  convertArray[ord('9')] = '9'
  convertArray[ord('A')] = 'a'
  convertArray[ord('B')] = 'b'
  convertArray[ord('C')] = 'c'
  convertArray[ord('D')] = 'd'
  convertArray[ord('E')] = 'e'
  convertArray[ord('F')] = 'f'
  convertArray[ord('G')] = 'g'
  convertArray[ord('H')] = 'h'
  convertArray[ord('I')] = 'i'
  convertArray[ord('J')] = 'j'
  convertArray[ord('K')] = 'k'
  convertArray[ord('L')] = 'l'
  convertArray[ord('M')] = 'm'
  convertArray[ord('N')] = 'n'
  convertArray[ord('O')] = 'o'
  convertArray[ord('P')] = 'p'
  convertArray[ord('Q')] = 'q'
  convertArray[ord('R')] = 'r'
  convertArray[ord('S')] = 's'
  convertArray[ord('T')] = 't'
  convertArray[ord('U')] = 'u'
  convertArray[ord('V')] = 'v'
  convertArray[ord('W')] = 'w'
  convertArray[ord('X')] = 'x'
  convertArray[ord('Y')] = 'y'
  convertArray[ord('Z')] = 'z'
  convertArray[ord('a')] = 'a'
  convertArray[ord('b')] = 'b'
  convertArray[ord('c')] = 'c'
  convertArray[ord('d')] = 'd'
  convertArray[ord('e')] = 'e'
  convertArray[ord('f')] = 'f'
  convertArray[ord('g')] = 'g'
  convertArray[ord('h')] = 'h'
  convertArray[ord('i')] = 'i'
  convertArray[ord('j')] = 'j'
  convertArray[ord('k')] = 'k'
  convertArray[ord('l')] = 'l'
  convertArray[ord('m')] = 'm'
  convertArray[ord('n')] = 'n'
  convertArray[ord('o')] = 'o'
  convertArray[ord('p')] = 'p'
  convertArray[ord('q')] = 'q'
  convertArray[ord('r')] = 'r'
  convertArray[ord('s')] = 's'
  convertArray[ord('t')] = 't'
  convertArray[ord('u')] = 'u'
  convertArray[ord('v')] = 'v'
  convertArray[ord('w')] = 'w'
  convertArray[ord('x')] = 'x'
  convertArray[ord('y')] = 'y'
  convertArray[ord('z')] = 'z'
  convertArray[31] = '\\'

  empties = [''] * 65000
  for x in range(65535):
    convertArray[x] = convertArray[x].encode('ascii')
    if len(convertArray[x]): dConvert[unichr(x)] = convertArray[x]

'''
Remove subfield indicator from leading subfield.
Remove trailing commas.
Condense multiple blanks to single blanks.
Convert subfield indicators to blank.
Remove subfield codes.
'''
def withBlanks(strBuf):
    ## strip leading subfield delimiter
    strBuf = strBuf.strip()
    if strBuf.startswith('\\'): strBuf = strBuf[2:]
    if strBuf.endswith(','): strBuf = strBuf[:-1]
    strBuf = strBuf.strip()

    ## ONLY THIS SECTION IS DIFFERENT BETWEEN NORMALIZE & NORMALIZEWITHBANG
    strBuf = strBuf.strip()
    if strBuf.endswith(','): strBuf = strBuf[:-1].strip()
    if strBuf.startswith('\\'):
      strBuf = ' '.join([c[1:].strip() for c in strBuf.split('\\')])
    elif strBuf.find('\\') > 0:
      strBuf = '%s%s' % ('x', strBuf)
      strBuf = ' '.join([c[1:].strip() for c in strBuf.split('\\')])

    while strBuf.find('  ') != -1:
      strBuf = strBuf.replace('  ', ' ')
    strBuf = strBuf.replace(' ,\\', '\\')
    strBuf = strBuf.replace(',\\', '\\')
    strBuf = strBuf.replace('\\, ', '\\')
    strBuf = strBuf.replace('\\,', '\\')

    return strBuf.strip()

'''
Remove subfield indicator from leading subfield.
Remove trailing commas.
Condense multiple blanks to single blanks.
Convert subfield indicators to 0x1f.
Remove subfield codes.
'''
def strict(strBuf):
    ## strip leading subfield delimiter
    strBuf = strBuf.strip()
    if strBuf.startswith('\\'): strBuf = strBuf[2:]
    if strBuf.endswith(','): strBuf = strBuf[:-1]
    strBuf = strBuf.strip()

    ## Gets rid of the subfield codes and leading/trailing blanks in sfs
    if strBuf.startswith('\\'):
       strBuf = chr(31).join([c[1:].strip() for c in strBuf.split('\\')])
    elif strBuf.find('\\') > 0:
      strBuf = '%s%s' % ('x', strBuf)
      strBuf = chr(31).join([c[1:].strip() for c in strBuf.split('\\')])

    while strBuf.find('  ') != -1:
      strBuf = strBuf.replace('  ', ' ')
    strBuf = strBuf.replace(' ,'+chr(31), chr(31))
    strBuf = strBuf.replace(','+chr(31), chr(31))
    strBuf = strBuf.replace(chr(31)+' ,', chr(31))
    strBuf = strBuf.replace(chr(31)+',', chr(31))

    return strBuf

def normalizeSimplified(input):
   return normalize(input, False, withBlanks)

def normalize(input, leaveFirstComma, cleanUp=strict):
    lconvert = convertArray
    
    if len(input) < 1:
      return input

    # put it back to unicode so that we can match chars
    # input = unicode(input.decode('utf-8'))
    if type(input) != UnicodeType:
      input = unicode(input, 'utf-8')

    ## ADD SUBFIELD CODE TO CONVERT TABLE -- map it to \\
    ## ALSO ADDED COMMA BACK TO TABLE TO STAY AS IS
    strBuf = ''.join(map(dConvert.get, input, empties[:len(input)])) #8222

    ## handle commas
    if not leaveFirstComma:
	strBuf = strBuf.replace(',', ' ')   # convert all to blanks
    else:
        firstSFa = strBuf.find('\\a')
	if firstSFa != -1:
	   firstComma = strBuf.find(',', firstSFa)
        else:
	   firstComma = strBuf.find(',')
        strBuf = strBuf.replace(',', ' ') # maybe a preceeding comma
	if firstComma > -1:   # found one to restore
	    prevSFC = strBuf.rfind('\\', 0, firstComma)
	    if prevSFC == -1 or (firstSFa != -1 and firstSFa == prevSFC):
	       # restore the first comma
	       strBuf = strBuf[:firstComma] + ',' + strBuf[firstComma+1:]

    return cleanUp(strBuf)
      
if __name__=='__main__':

  def nextScriptAnswer(script, check):
     for s in script:
	c = check.readline()
	yield(s.strip(), c.strip())

  if len(sys.argv) < 3 or len(sys.argv) > 5:
    print >>sys.stderr, "usage: %s scriptFile checkFile [no]Commas errFile" % sys.argv[0]
  else:
    script = file(sys.argv[1], 'rb', 10000)
    check = file(sys.argv[2], 'rb', 10000)
    if len(sys.argv) > 4:
      errFile = file(sys.argv[4], 'wb', 10000)
    else:
      errFile = sys.stderr
    commaFlag = 1
    if len(sys.argv) > 3:
       if sys.argv[3].lower() == 'noCommas':
	  commaFlag = 0

    for (s, c) in nextScriptAnswer(script, check):
       norm = normalize(s, commaFlag)
       if c != norm:
	  errFile.write('Script Error\ninput: %s\nexpected: %s\ngot: %s\n' %
	     s, c, norm)
      
    errFile.close()
