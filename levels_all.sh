#!/usr/bin/env bash
# Both level sets, in order: 4 English then 4 Russian.
# Each runner pushes its own results, so a failure in one does not lose the other.
#
# Detached (safe to close the laptop):
#   bash bg.sh levels_all.sh
#   tail -f logs/levels_all.log
set -u
cd "$(dirname "$0")"

echo "################ ENGLISH (levels_en) ################"
bash levels_en/run.sh
en=$?

echo
echo "################ RUSSIAN (levels) ################"
bash levels/run.sh
ru=$?

echo
echo "################ SUMMARY ################"
echo "  levels_en: $([ $en -eq 0 ] && echo OK || echo "FAILED (exit $en)")"
echo "  levels:    $([ $ru -eq 0 ] && echo OK || echo "FAILED (exit $ru)")"
[ $en -eq 0 ] && [ $ru -eq 0 ]
