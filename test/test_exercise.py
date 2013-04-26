# -*- coding: utf-8 -*-
# Copyright 2013 Michael Helmling
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation

from __future__ import unicode_literals

import datetime
import unittest

from exdb.exercise import Exercise, VersionMismatchError

validXML="""<?xml version='1.0' encoding='utf-8'?>
<exercise xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaversion="1" xsi:noNamespaceSchemaLocation="exercise.xsd">
  <creator>jemand</creator>
  <number>1</number>
  <description>eine langweilige Aufgabe</description>
  <modified>2002-05-30T09:30:10</modified>
  <tex_preamble>\\usepackage[utf8]{inputenc}</tex_preamble>
  <tex_exercise lang="DE">$x$</tex_exercise>
  <tex_solution lang="DE">$y$</tex_solution>
  <tex_solution lang="EN">$z$ö</tex_solution>
  <tag>aabc</tag>
  <tag>Revised Simplex</tag>
</exercise>
"""

class XMLImportExportTest(unittest.TestCase):
    
    def test_importValidXML(self):
        exercise = Exercise.fromXMLString(validXML.encode('utf-8'))
        self.assertEqual(exercise.schemaversion, 1)
        self.assertEqual(len(exercise.tags), 2)
        self.assertIn('aabc', exercise.tags)
        self.assertIsInstance(exercise.modified, datetime.datetime)
        self.assertIn('DE', exercise.tex_exercise)
        self.assertIn('DE', exercise.tex_solution)
        self.assertIn('EN', exercise.tex_solution)
        self.assertNotIn('EN', exercise.tex_exercise)
        self.assertIsInstance(exercise.number, int)
        
    def test_importInvalidXML(self):
        vlines = validXML.splitlines()
        vlines[6:6] = ["<unspecifiedElement>bla</unspecifiedElement>"]
        invalidXML = "\n".join(vlines)
        from lxml.etree import XMLSyntaxError
        self.assertRaisesRegexp(XMLSyntaxError, "not expected",
                                lambda : Exercise.fromXMLString(invalidXML.encode('utf-8')))
        del vlines[6]
        vlines[7:7] = ['<tex_exercise lang="DE">double german</tex_exercise>']
        invalidXML2 = "\n".join(vlines)
        self.assertRaisesRegexp(XMLSyntaxError, "Duplicate key-sequence",
                                lambda : Exercise.fromXMLString(invalidXML2.encode('utf-8')))
        
    def test_importTooRecentSchema(self):
        invalidXML = validXML.replace('schemaversion="1"', 'schemaversion="1000"')
        self.assertRaises(VersionMismatchError,
                          lambda : Exercise.fromXMLString(invalidXML.encode('utf-8')))

    def test_xmlExport(self):
        self.maxDiff = None
        self.assertEqual(Exercise.fromXMLString(validXML.encode('utf-8')).toXML(), validXML)