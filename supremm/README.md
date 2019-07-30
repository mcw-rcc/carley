# SUPReMM Setup

Follow https://supremm.xdmod.org/8.0/supremm-overview.html

# Changes
Download PCP files from https://bintray.com/pcp/el6/pcp/3.11.10#files 
or
copy files in "/rcc/stor1/installers/pcp-bintray-el6" to software image  

yum install pcp-* perl-PCP-PMDA-* python-pcp-*

edit cron job - pcp-pmlogger
```
#
# Performance Co-Pilot crontab entries for a monitored site
# with one or more pmlogger instances running
#
# daily processing of archive logs (with compression enabled)
10     0  *  *  *  root  /usr/libexec/pcp/bin/pmlogger_daily -M -k forever
# every 30 minutes, check pmlogger instances are running
0,30  *  *  *  *  root  /usr/libexec/pcp/bin/pmlogger_check -C
```


