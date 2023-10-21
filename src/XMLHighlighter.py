#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class XMLHighlighter(QSyntaxHighlighter):
    '''
    Class for highlighting xml text inherited from QSyntaxHighlighter
    reference:
        http://www.yasinuludag.com/blog/?p=49
    '''

    def __init__(self, parent=None):

        super(XMLHighlighter, self).__init__(parent)

        self.highlightingRules = []

        xmlElementFormat = QTextCharFormat()
        xmlElementFormat.setForeground(QColor("#000070"))  # blue
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=[\s/>])"), xmlElementFormat))

        xmlAttributeFormat = QTextCharFormat()
        xmlAttributeFormat.setFontItalic(True)
        xmlAttributeFormat.setForeground(QColor("#177317"))  # green
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\=)"), xmlAttributeFormat))
        self.highlightingRules.append((QRegExp("="), xmlAttributeFormat))

        self.valueFormat = QTextCharFormat()
        self.valueFormat.setForeground(QColor("#e35e00"))  # orange
        self.valueStartExpression = QRegExp("\"")
        self.valueEndExpression = QRegExp("\"(?=[\s></])")

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(QColor("#a0a0a4"))  # grey
        self.highlightingRules.append((QRegExp("<!--[^\n]*-->"), singleLineCommentFormat))
        self.highlightingRules.append((QRegExp("'''[^\n]*'''"), singleLineCommentFormat))

        textFormat = QTextCharFormat()
        textFormat.setForeground(QColor("#000000"))  # black
        # (?<=...)  - lookbehind is not supported
        self.highlightingRules.append((QRegExp(">(.+)(?=</)"), textFormat))

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#000070"))  # blue
        keywordFormat.setFontWeight(QFont.Bold)
        keywordPatterns = ["\\b?xml\\b", "/>", ">", "<", "</"]
        self.highlightingRules += [(QRegExp(pattern), keywordFormat)
                                   for pattern in keywordPatterns]

    # VIRTUAL FUNCTION WE OVERRIDE THAT DOES ALL THE COLLORING
    def highlightBlock(self, text):
        # for every pattern
        for pattern, format in self.highlightingRules:
            # Create a regular expression from the retrieved pattern
            expression = QRegExp(pattern)
            # Check what index that expression occurs at with the ENTIRE text
            index = expression.indexIn(text)
            # While the index is greater than 0
            while index >= 0:
                # Get the length of how long the expression is true, set the format from the start to the length with the text format
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                # Set index to where the expression ends in the text
                index = expression.indexIn(text, index + length)

                # HANDLE QUOTATION MARKS NOW.. WE WANT TO START WITH " AND END WITH ".. A THIRD " SHOULD NOT CAUSE THE WORDS INBETWEEN SECOND AND THIRD TO BE COLORED
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.valueStartExpression.indexIn(text)
        while startIndex >= 0:
            endIndex = self.valueEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.valueEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.valueFormat)
            startIndex = self.valueStartExpression.indexIn(text, startIndex + commentLength)
