import re


class RegexEqual(str):

    def __init__(self, string, sep='_'):
        self.string = string
        self.sep = sep

    def __eq__(self, pattern):
        match = re.search(pattern, self.string)
        return match is not None


def validate(name, value):
    msg = None

    match RegexEqual(name):

        case '^segs_[crs]$':
            if type(value) is int and value >= 3:
                return
            msg = 'must be integer. minimum is 3'

        case '^segs_[awdh]$':
            if type(value) is int and value >= 1:
                return
            msg = 'must be integer. minimum is 1'

        case '^segs_':
            if type(value) is int and value >= 0:
                return
            msg = 'must be integer and more than 0'

        case '_deg$':
            if 0 <= value <= 360:
                return
            msg = 'must be in the range from 0 to 360'

        case '^delta_radius$':
            if value < 0:
                return
            msg = 'top radius must be smaller than bottom radius'

        case '(_|^)inner_radius$' | '^top_radius$':
            if value >= 0:
                return
            msg = 'must be greater than or equal to 0'

        case '(_|^)radius$':
            if value > 0:
                return
            msg = 'must be greater than 0'

        case '(_|^)thickness$':
            if value >= 0:
                return
            msg = 'inner radius must be in the range from 0 to radius'

        case '^invert$':
            if isinstance(value, bool):
                return
            msg = 'must be bool'

        case '^(height|width|depth)$':
            if value > 0:
                return
            msg = 'must be greater than 0'

    if msg:
        raise ValueError(f'{name}: {msg}.')