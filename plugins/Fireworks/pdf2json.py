#!/usr/bin/env python

from pyPdf import PdfFileReader
import re
import simplejson as json

if __name__ == '__main__':

    pdffile = 'fw_list_2005.pdf'
    reader = PdfFileReader(file(pdffile, 'rb'))

    fireworks = []
    for num in xrange(len(reader.pages)):
        page = reader.getPage(num)
        rawtext = page.extractText()
        # skip to first /n to ignore header
        skipto = rawtext.find("\n")
        rawtext = rawtext[skipto:].encode('utf8')
        entries = re.split('\n', rawtext)
        for e in entries:
            fireworks.extend(re.split('\s{2,}', e))
    fireworks = [x.strip() for x in fireworks if len(x.strip())]

    # last item is miscellania
    fireworks.pop()
    print json.dumps(fireworks, indent=1)
