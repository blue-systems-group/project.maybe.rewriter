import re

ASSIGNMENT_PATTERN = re.compile(r"""(?xum)
                                ^(?P<variable>[^\S\n]*
                                .*?)
                                =\s*maybe\s*
                                \((?P<label>.+?)\)
                                (?P<alternatives>(?:[^,;]+,)+\s*
                                [^,]+)\s*
                                ;$""")
