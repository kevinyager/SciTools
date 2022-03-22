#!/bin/bash



FROM_LOC="/home/kyager/doit/elgato/main/*"

TO_LOC="xf11bm-ws2:/nsls2/xf11bm/software/ui/deck/run06/"




#rsync -rlpt --progress --partial -e "ssh " $FROM_LOC $TO_LOC
#rsync -rlpt --progress --partial -e "ssh -o ProxyCommand='ssh kyager@box64-2.nsls2.bnl.gov nc -w 10 %h %p' " $FROM_LOC $TO_LOC
rsync -rlpt --copy-links --progress --partial -e "ssh -o ProxyCommand='ssh kyager@box64-2.nsls2.bnl.gov nc -w 10 %h %p' " $FROM_LOC $TO_LOC
