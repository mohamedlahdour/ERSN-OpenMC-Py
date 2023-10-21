# syntax.py
# adapted from = https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting

import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

quote = "%s%s%s" % (chr(39), chr(39), chr(39))
dquote = "%s%s%s" % (chr(34), chr(34), chr(34))

def format(color, style=''):
    '''Return a QTextCharFormat with the given attributes.
    '''
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    if 'italicbold' in style:
        _format.setFontItalic(True)
        _format.setFontWeight(QFont.Bold)
    return _format

# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('#2C2CC8', 'bold'),
    'operator': format('darkred'),
    'brace': format('darkred'),
    'defclass': format('#cc0000', 'bold'),
    'classes': format('#cc0000', 'bold'),
    'Qtclass': format('black', 'bold'),
    'string': format('#8B3E2F', 'italic'),
    'string2': format('#42923b', 'italic'),
    'comment': format('#42923b', 'italic'),
    'self': format('#D63030', 'italicbold'),
    'selfnext': format('#2e3436', 'bold'),
    'Qnext': format('#2e3436', 'bold'),
    'numbers': format('#DC143C'),
    'Key': format('darkgreen', 'italic'),
    'Key_1': format('brown', 'italic'),
    'component': format('red', 'italic'),
    'openmc': format('blue', 'italic'),
    'openmc1': format('green', 'italic'),
}

class Highlighter(QSyntaxHighlighter):
    '''Syntax highlighter for the Python language.
    '''
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'super', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    openmcs = ['openmc', 'id', 'universes', 'surface', 'cell', 'hex_lattice', 'lattice', 'material', 'run_mode', 'keff_trigger',
               'source', 'space', 'trigger', 'filter', 'tally', 'plot', '\.Materials']
    components = [
        'materials', 'geometry', 'settings', 'tallies', 'plots', 
    ]

    Keys = [
        'region', 'fill', 'name', 'enrichment', 'temperature', 'percent_type', 'surface_id', 'cell_id', 'universe_id',
        'tally_id', 'lattice_id', 'mesh_id', 'filter_id', 'universe', 'type', 'coeffs', 'boundary', 'n_axial', 'n_rings',
        'dimension', 'outer', 'pitch', 'center', 'depletable', 'units', 'value', 'ao', 'wo', 'particles', 'batches', 'inactive',
        'threshold', 'strength', 'parameters', 'active', 'max_batches', 'track', 'bins', 'filters', 'scores', 'basis', 'color_by',
        'filename', 'origin', 'pixels', 'width', 'lower_left', 'upper_right', 'n_dimension',
    ]

    Keys_1 = ['nuclide', 'density', 'sab',
        ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        tri = (quote)
        trid = (dquote)
        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp(tri), 1, STYLES['string2'])
        self.tri_double = (QRegExp(trid), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in Highlighter.keywords]
        
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in Highlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in Highlighter.braces]
        
        rules += [(r'\b%s\b' % openm, 0, STYLES['openmc'])    for openm in Highlighter.openmcs]
        rules += [(r'\b%s\b' % comp, 0, STYLES['component']) for comp in Highlighter.components]
        rules += [(r'\b%s\b' % k, 0, STYLES['Key'])
            for k in Highlighter.Keys]

        # All other rules
        rules += [

            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences ### "\"([^\"]*)\"" ### "\"(\\w)*\""
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an word
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']), ### (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),

            # 'self.' followed by an word
            (r'\bself\b)', 1, STYLES['selfnext']), ### (r'\bself.\b\s*(\w+)', 1, STYLES['selfnext']),

            # 'Q' followed by an word
            (r'\b[Q.]\b\s*(\w+)', 1, STYLES['Qnext']),

            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['classes']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # 'Q'  word
            #(r'\\bQ[A-Za-z]+\\b', 1, STYLES['Qtclass']), #(QRegExp("\\bQ[A-Za-z]+\\b"),

            # 'openmc.' followed by a word
            (r'\b[openmc.]\b\s*(\w+)', 1, STYLES['openmc']), 
            (r'\b[.]\b\s*(\w+)', 1, STYLES['openmc1']), 
            (r'\\bopenmc\b', 1, STYLES['classes']), 

            
            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):

#        Apply syntax highlighting to the given block of text.
        self.sectionFormat = QtGui.QTextCharFormat()
        self.sectionFormat.setForeground(QtCore.Qt.darkGreen)
        self.errorFormat = QtGui.QTextCharFormat()
        self.errorFormat.setForeground(QtCore.Qt.red)
        lines = text.split('\n')
        for line in lines:
            if "[VALID]" in line:
                self.setFormat(120, len(line), self.sectionFormat)
            elif "[NOT VALID]" in line or "[XML ERROR]" in line:
                self.setFormat(120, len(line), self.errorFormat)

        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        '''Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        '''
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
