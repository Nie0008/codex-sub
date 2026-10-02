#!/usr/bin/env python3
"""Initialize sub and think through the existing transactional installer."""
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    raise SystemExit('Codex Sub requires Python 3.11 or newer.')

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_adaptive_agents.cli import main, parser


def initialize(argv):
    arguments = ['install', '--skill', *argv]
    result = main(arguments)
    if result or '--yes' not in argv:
        return result
    args = parser().parse_args(arguments)
    options = [value for name in ('codex_home', 'codex') if getattr(args, name)
               for value in ('--' + name.replace('_', '-'), getattr(args, name))]
    return main(['doctor', *options])


if __name__ == '__main__':
    raise SystemExit(initialize(sys.argv[1:]))
