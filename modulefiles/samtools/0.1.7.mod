#%Module -*- tcl -*-
##
## modulefile
##
proc ModulesHelp { } {

  puts stderr "\tAdds SAMtools to your environment variables,"
}

module-whatis "adds SAMtools to your environment variables."

set              version           0.1.7.mod
set              root              /cm/shared/apps/samtools/$version

prepend-path      PATH              $root
