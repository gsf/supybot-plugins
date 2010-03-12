#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Conventions used:

From http://www.cdlib.org/inside/diglib/pairtree/pairtreespec.html version 0.1

This client handles all of the pairtree conventions, and provides a Pairtree object
to make it easier to interact with.

Usage
=====

>>> from pairtree import PairtreeStorageClient

To create a pairtree store in I{mystore/} to hold objects which have a URI base of
I{http://example.org/ark:/123}

>>> store = PairtreeStorageClient(store_dir='mystore', uri_base='http://example.org/ark:/123')

"""

import os, sys, shutil

import codecs

import string

import re

import hashlib

encode_regex = re.compile(r"[\"*+,<=>?\\^|]|[^\x21-\x7e]", re.U)
decode_regex = re.compile(r"\^(..)", re.U)

def char2hex(m):
        return "^%02x"%ord(m.group(0))

def hex2char(m):
        return chr(int(m.group(1), 16))


def id_encode(id):
    """
    The identifier string is cleaned of characters that are expected to occur rarely
    in object identifiers but that would cause certain known problems for file systems.
    In this step, every UTF-8 octet outside the range of visible ASCII (94 characters
    with hexadecimal codes 21-7e) [ASCII] (Cerf, “ASCII format for network interchange,”
    October 1969.), as well as the following visible ASCII characters::

        "   hex 22           <   hex 3c           ?   hex 3f
        *   hex 2a           =   hex 3d           ^   hex 5e
        +   hex 2b           >   hex 3e           |   hex 7c
        ,   hex 2c

    must be converted to their corresponding 3-character hexadecimal encoding, ^hh,
    where ^ is a circumflex and hh is two hex digits. For example, ' ' (space) is
    converted to ^20 and '*' to ^2a.

    In the second step, the following single-character to single-character conversions
    must be done::

            / -> =
            : -> +
            . -> ,

    These are characters that occur quite commonly in opaque identifiers but present
    special problems for filesystems. This step avoids requiring them to be hex encoded
    (hence expanded to three characters), which keeps the typical ppath reasonably
    short. Here are examples of identifier strings after cleaning and after
    ppath mapping::

        id:  ark:/13030/xt12t3
            ->  ark+=13030=xt12t3
            ->  ar/k+/=1/30/30/=x/t1/2t/3/
        id:  http://n2t.info/urn:nbn:se:kb:repos-1
            ->  http+==n2t,info=urn+nbn+se+kb+repos-1
            ->  ht/tp/+=/=n/2t/,i/nf/o=/ur/n+/n/bn/+s/e+/kb/+/re/p/os/-1/
        id:  what-the-*@?#!^!?
            ->  what-the-^2a@^3f#!^5e!^3f
            ->  wh/at/-t/he/-^/2a/@^/3f/#!/^5/e!/^3/f/

    (From section 3 of the Pairtree specification)

    @param id: Encode the given identifier according to the pairtree 0.1 specification
    @type id: identifier
    @returns: A string of the encoded identifier
    """
    # Unicode or bust
    if isinstance(id, unicode):
        # assume utf-8
        # TODO - not assume encoding
        id = id.encode('utf-8')

    second_pass_m = {'/':'=',
                        ':':'+',
                        '.':','
                    }
    # hexify the odd characters
    # Using Erik Hetzner's regex in place of my previous hack
    new_id = encode_regex.sub(char2hex, id)
    
    # 2nd pass
    second_pass = []
    for char in new_id:
        second_pass.append(second_pass_m.get(char, char))
    return "".join(second_pass)

def id_decode(id):
    """
    This decodes a given identifier from its pairtree filesystem encoding, into
    its original form:
    @param id: Identifier to decode
    @type id: identifier
    @returns: A string of the decoded identifier
    """
    second_pass_m = {'=':'/',
                        '+':':',
                        ',':'.'
                    }
    second_pass = []
    for char in id:
        second_pass.append(second_pass_m.get(char, char))
    dec_id = "".join(second_pass)
    #dec_id = id.translate(string.maketrans(u'=+,',u'/:.'))
    # Using Erik Hetzner's regex in place of my previous hack
    #ppath_s = re.sub(r"\^(..)", self.__hex2char, dec_id)
    ppath_s = decode_regex.sub(hex2char, dec_id)
    # Again, drop the assumption of utf-8
    return ppath_s.decode('utf-8')

def id_to_path(id):
    enc_id = id_encode(id)
    dirpath = []
    while enc_id:
        dirpath.append(enc_id[:2])
        enc_id = enc_id[2:]
    return dirpath
