#!/usr/bin/python

#---------------------------------------------------#
# File: $TORQUE_HOMEDIR/sbin/qsub_filter.py
# Auth: Matthew Flister <maflister@mcw.edu>
# Desc: This is a filter for Torque's qsub command.
#---------------------------------------------------#


import sys, re, os, pwd, grp

# max nodes for queues
stdnodes = 1
computenodes = 3
largenodes = 8
medmemnodes = 1
bigmemnodes = 1
devnodes = 1

# cores per node type
stdcores = 24
medmemcores = 48
bigmemcores = 40
devcores = 1

# max memory for queues in gb
stdmem = 120
stdMemPerCore = 5
medmem = 380
medMemPerCore = 8
bigmem = 3000
bigMemPerCore = 75
devmem = 5
interMem = 16

# max walltimes for queues
sharedwtime = 168
computewtime = 120
largewtime = 48
medmemwtime = 168
bigmemwtime = 168
devwtime = 1
interwtime = 8

# mail command
sendmailCommand = "/usr/sbin/sendmail -t"

# username
username = pwd.getpwuid(os.geteuid())[0]
exemptUsers = ["akrruser"]
exemptJobs = ["ansys"]

### DO NOT CHANGE ANYTHING BELOW THIS ###
# get default account or list of accounts
def get_accounts_cli(user):
    accounts = {}
    command = 'mam-list-accounts -u %s --show "Name,Active,Description" --format csv' % user
    cli_data = os.popen(command, "r").readlines()[1:]
    for i in cli_data:
        account,isactive,description = i.strip().split(',')
        if isactive == 'True':
            accounts[account] = description
    return accounts

# get accounts from mamws rest api
# requires mam user and password
def get_accounts_rest(user):
    request = urllib2.Request("https://mam.test.edu/mamws/v1/accounts?constraint-filter=user=%s" % user)
    base64string = base64.encodestring('user:password').replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    context = ssl._create_unverified_context()
    result = urllib2.urlopen(request, context=context)
    json_data = json.load(result)
    accounts = {}
    for i in json_data['data']:
        isactive = i['active']
        if isactive:
            accounts[i['name']] = i['description']
    return accounts

def getgroups(user):
    gids = [g.gr_gid for g in grp.getgrall() if user in g.gr_mem]
    gid = pwd.getpwnam(user).pw_gid
    gids.append(grp.getgrgid(gid).gr_gid)
    return [grp.getgrgid(gid).gr_name for gid in gids]

def checkPBS(lines):
    pbs = False
    for line in lines:
        if "#PBS" in line:
            pbs = True
            break
    return pbs

errors = []
warnings = []

# grab lines from stdin
lines = sys.stdin.readlines()
pbs = checkPBS(lines)

if len(sys.argv) == 2:
    if pbs:
        for line in lines:
            if not line.strip(): # skip blank lines between shabang and first #PBS line
                continue
            if "#" in line and "#PBS" not in line:
                continue
            m = re.search('(?<=#PBS -N )(\w+)', line)
            if (m):
                jobname = m.group(0)
            m = re.search('(?<=#PBS -A )(\w+)', line)
            if (m):
                account = m.group(0)
            m = re.search('#PBS\s*\-l\s*\S*nodes\=(\w+)', line)
            if (m):
                nodes = m.group(1)
                try:
                    int(nodes)
                    nodes = int(nodes)
                except:
                    nodes = 1
            m = re.search('#PBS\s*\-l\s*\S*ppn\=(\d+)', line)
            if (m):
                ppn = m.group(1)
            m = re.search('#PBS\s*\-l\s*\S*mem\=(\w+)', line)
            if (m):
                mem = m.group(1)
            m = re.search('#PBS\s*\-l\s*\S*walltime\=(\d+(:\d+)*)', line)
            if (m):
                walltime = m.group(1)
            m = re.search('#PBS\s*\-l\s*\S*feature\=(\w+)', line)
            if (m):
                features = m.group(1)
            m = re.search('(?<=#PBS -q )(\w+)', line)
            if (m):
                queue = m.group(0)

else:
    # get qsub command line
    line = ' '.join(sys.argv[1:])
    if line:
        m = re.search('\-N\s*(\w+)', line)
        if (m):
            jobname = m[-1]
        m = re.search('(\-A\s*(\w+)', line)
        if (m):
            account = m.group(1)
        m = re.search('\-l\s*\S*nodes\=(\w+)', line)
        if (m):
            nodes = m.group(1)
            try:
                int(nodes)
                nodes = int(nodes)
            except:
                nodes = 1
        m = re.search('\-l\s*\S*ppn\=(\d+)', line)
        if (m):
            ppn = m.group(1)
        m = re.search('\-l\s*\S*mem\=(\w+)', line)
        if (m):
            mem = m.group(1)
        m = re.search('\-l\s*\S*walltime\=(\d+(:\d+)*)', line)
        if (m):
            walltime = m.group(1)
        m = re.search('\-l\s*\S*feature\=(\w+)', line)
        if (m):
            features = m.group(1)
        m = re.search('\-q\s*(\w+)', line)
        if (m):
            queue = m.group(1)
        m = re.search('\-I', line)
        if (m):
            interactive = m.group(0)

    # deal with script
    if pbs:
        for line in lines:
            if not line.strip(): # skip blank lines between shabang and first #PBS line
                continue
            if "#" in line and "#PBS" not in line:
                continue
            try:
                jobname
            except:
                m = re.search('(?<=#PBS -N )(\w+)', line)
                if (m):
                    jobname = m.group(0)
            try:
                account
            except:
                m = re.search('(?<=#PBS -A )(\w+)', line)
                if (m):
                    account = m.group(0)
            try:
                nodes
            except:
                m = re.search('#PBS\s*\-l\s*\S*nodes\=(\w+)', line)
                if (m):
                    nodes = m.group(1)
                    try:
                        int(nodes)
                        nodes = int(nodes)
                    except:
                        nodes = 1
            try:
                ppn
            except:
                m = re.search('#PBS\s*\-l\s*\S*ppn\=(\d+)', line)
                if (m):
                    ppn = m.group(1)
            try:
                mem
            except:
                m = re.search('#PBS\s*\-l\s*\S*mem\=(\w+)', line)
                if (m):
                    mem = m.group(1)
            try:
                walltime
            except:
                m = re.search('#PBS\s*\-l\s*\S*walltime\=(\d+(:\d+)*)', line)
                if (m):
                    walltime = m.group(1)
            try:
                features
            except:
                m = re.search('#PBS\s*\-l\s*\S*feature\=(\w+)', line)
                if (m):
                    features = m.group(1)
            try:
                queue
            except:
                m = re.search('(?<=#PBS -q )(\w+)', line)
                if (m):
                    queue = m.group(0)

##### MAIN START #####
# for each must-have attribute check if exists and exit if not
try:
    jobname
except:
    msg = 'PBS job name is missing. Please consider adding a job name to identify your work.\nExample: #PBS -N JobName.'
    warnings.append(msg)
    jobname = 'missing'
try:
    account
except:
    account = 'missing'
try:
    nodes = int(nodes)
except:
    msg = 'PBS node count is required.\nExample: #PBS -l nodes=1:ppn=1.'
    errors.append(msg)
    nodes = 'missing'
try:
    ppn = int(ppn)
except:
    msg = 'PBS processor per node count is required.\nExample: #PBS -l nodes=1:ppn=1.'
    errors.append(msg)
    ppn = 'missing'
try:
    mem
except:
    msg = 'PBS memory request is required.\nExample: #PBS -l mem=5gb.'
    errors.append(msg)
    mem = 'missing'
try:
    walltime
except:
    msg = 'PBS walltime request is required.\nExample: #PBS -l walltime=1:00:00.'
    errors.append(msg)
    walltime = 'missing'
try:
    features
except:
    features = 'missing'
try:
    interactive
except:
    interactive = 'missing'

# rewrite memory to gb
if mem == 'missing':
    pass
else:
    m = re.search('(\d*)(\w*)', mem)
    memval = float(m.group(1))
    memsuff = m.group(2)
    if memsuff.lower() == "b":
        memval = memval/(1000**3)
    if memsuff.lower() in ("kb", "k"):
        memval = memval/(1000**2)
    if memsuff.lower() in ("mb", "m"):
        memval = memval/(1000)
    if memsuff.lower() in ("gb", "g"):
        memval = memval
    if memsuff.lower() in ("tb", "t"):
        memval = memval*(1000)

# rewrite walltime to hours
if walltime == 'missing':
    pass
else:
    time = walltime.split(':')
    units = len(time)
    if units == 1:
        wtime = float(time[0])/(60**2)
    if units == 2:
        wtime = float(time[0])/(60)+float(time[1])/(60**2)
    if units == 3:
        wtime = float(time[0])+float(time[1])/60+float(time[2])/(60**2)
    if units == 4:
        wtime = float(time[0])*24+float(time[1])+float(time[2])/60+float(time[3])/(60**2)

# this section is based on queue
try:
    queue
except NameError:
    queue = ""
if queue == "bigmem":
    if nodes == 'missing':
        pass
    else:
        nodes = int(nodes)
        if nodes > bigmemnodes:
            msg = 'Nodes request must be equal to %s for bigmem queue.' % (bigmemnodes)
            errors.append(msg)
    if ppn == 'missing':
        pass
    else:
        if ppn > bigmemcores:
            msg = 'PPN request must be less than or equal to %s for bigmem queue.' % (bigmemcores)
            errors.append(msg)
    if mem == 'missing':
        pass
    else:
        memPerCore = memval/ppn
        if memPerCore <= stdMemPerCore:
            msg = 'Memory request should be greater than %sgb per core for bigmem queue.' % (stdMemPerCore)
            warnings.append(msg)
        if memval > bigmem:
            msg = 'Memory request must be less than or equal to %sgb for bigmem queue.' % (bigmem)
            errors.append(msg)
    if walltime == 'missing':
        pass
    else:
        if wtime > bigmemwtime:
            msg = 'Walltime request must be less than %shrs for bigmem queue.' % (bigmemwtime)
            errors.append(msg)
elif queue == "medmem":
    if nodes == 'missing':
        pass
    else:
        nodes = int(nodes)
        if nodes > medmemnodes:
            msg = 'Nodes request must be equal to %s for medmem queue.' % (medmemnodes)
            errors.append(msg)
    if ppn == 'missing':
        pass
    else:
        if ppn > medmemcores:
            msg = 'PPN request must be less than or equal to %s for medmem queue.' % (medmemcores)
            errors.append(msg)
    if mem == 'missing':
        pass
    else:
        memPerCore = memval/ppn
        if memPerCore <= stdMemPerCore:
            msg = 'Memory request should be greater than %sgb per core for medmem queue.' % (stdMemPerCore)
            warnings.append(msg)
        if memval > medmem:
            msg = 'Memory request must be less than or equal to %sgb for medmem queue.' % (medmem)
            errors.append(msg)
    if walltime == 'missing':
        pass
    else:
        if wtime > medmemwtime:
            msg = 'Walltime request must be less than %shrs for medmem queue.' % (medmemwtime)
            errors.append(msg)
elif queue == "dev":
    if nodes == 'missing':
        pass
    else:
        if nodes > devnodes:
            msg = 'Nodes request must be equal to %s for dev queue.' % (devnodes)
            errors.append(msg)
    if ppn == 'missing':
        pass
    else:
        if ppn > devcores:
            msg = 'PPN request must be equal to %s for dev queue.' % (devcores)
            errors.append(msg)
    if mem == 'missing':
        pass
    else:
        if memval > devmem:
            msg = 'Memory request must be less than or equal to %sgb for dev queue.' % (devmem)
            errors.append(msg)
    if walltime == 'missing':
        pass
    else:
        if wtime > devwtime:
            msg = 'Walltime request must be less than or equal to %shrs for dev queue.' % (devwtime)
            errors.append(msg)
# no queue 
else:
    if nodes == 'missing':
        pass
    else:
        maxmem = nodes*stdmem
        if nodes > largenodes:
            msg = 'Max nodes request must be less than or equal to %s for standard compute nodes.' % (largenodes)
            errors.append(msg)
    if ppn == 'missing':
        pass
    else:
        if ppn > stdcores:
            msg = 'PPN request must be less than or equal to %s for standard compute nodes.' % (stdcores)
            errors.append(msg)
            if ppn == medmemcores:
                msg = 'Consider using medmem queue for jobs needing %s cores.' % (medmemcores)
                warnings.append(msg)
    if mem == 'missing':
        pass
    else:
        maxmem = nodes*stdmem
        if memval > maxmem:
            msg = 'Memory request must be less than %sgb per standard compute node.' % (stdmem)
            errors.append(msg)
        cores = nodes*ppn
        memPerCore = memval/cores
        if memPerCore > stdMemPerCore:
            msg = 'Consider using medmem or bigmem queue for jobs needing greater than %sgb of memory per core.' % (stdMemPerCore)
            warnings.append(msg)
    if nodes == 'missing' or walltime == 'missing':
        pass
    else:
        if nodes == stdnodes and wtime > sharedwtime:
            msg = 'Max walltime request with %s node(s) is %shrs.' % (nodes,sharedwtime)
            errors.append(msg)
        if nodes > stdnodes and nodes <= computenodes and wtime > computewtime:
            msg = 'Max walltime request with %s node(s) is %shrs' % (nodes,computewtime)
            errors.append(msg)
        if nodes > computenodes and nodes <= largenodes and wtime > largewtime:
            msg = 'Max walltime request with %s node(s) is %shrs.' % (nodes,largewtime)
            errors.append(msg)
    if interactive != 'missing':
        if nodes > stdnodes:
            msg = 'Max nodes request must be less than or equal to %s for interactive jobs.' % (stdnodes)
            errors.append(msg)
        if ppn > 4:
            msg = 'Max ppn request must be less than or equal to 4 for interactive jobs.'
            errors.append(msg)
        if mem == "missing":
            pass
        else:
            if memval > interMem:
                msg = 'Max memory request must be less than or equal to %sgb for interactive jobs.' % (interMem)
                errors.append(msg)
        if walltime == 'missing':
            pass
        else:
            if wtime > interwtime:
                msg = 'Max walltime request for interactive job is %shrs.' % (interwtime)
                errors.append(msg)

##accounts = get_accounts_rest(username)
#accounts = get_accounts_cli(username)
#if account == 'missing':
#    if accounts:
#        msg = 'PBS account string is required. No account string provided.\nAdd a valid account string. Example #PBS -A myaccount.\nAvailable accounts:'
#        for name, desc in accounts.items():
#            acctType = desc.split(' ')[-1]
#            #msg = msg + '\n' + name + ': "' + desc +'"'
#            msg = msg + '\n' + 'Account: ' + name + '\nDescription: ' + desc + '\nType: ' + acctType + '\nLimit: None\n'
#        errors.append(msg)
#    else:
#        msg = 'PBS account string is required. No valid account string for your user. Contact rcc_admin@mcw.edu'
#        errors.append(msg)
#else:
#    if account not in accounts.keys():
#        msg = 'PBS account string is required. Requested account string is not valid.\nAdd a valid account string. Example: #PBS -A myaccount.\nAvailable accounts:'
#        for name, desc in accounts.items():
#            acctType = desc.split(' ')[-1]
#            #msg = msg + '\n' + name + ': "' + desc +'"'
#            msg = msg + '\n' + 'Account: ' + name + '\nDescription: ' + desc + '\nType: ' + acctType + '\nLimit: None\n'
#        errors.append(msg)
#        errors.append(msg)
#    elif not accounts:
#        msg = 'PBS account string is required. No valid account string for your user. Contact rcc_admin@mcw.edu'
#        errors.append(msg)

# check for matlab licensing if matlab is going to run
groups = getgroups(username)
group_member = True
if "matlab_users" in groups:
    group_member = False
lic_matlab = False
matlab = False
for line in lines:
    if "software=matlab" in line:
        lic_matlab = True
    if "PBS" not in line and "matlab " in line:
        matlab = True
if lic_matlab or matlab:
    if not group_member:
        msg = 'You are not authorized to use MATLAB on this cluster. Please contact rcc_admin@mcw.edu'
        errors.append(msg)
    elif not lic_matlab:
        msg = 'You are attempting to run MATLAB but have not requested a license. Example: #PBS -l software=matlab:1'
        errors.append(msg)
    elif not matlab:
        msg = 'You have specified a MATLAB license but are not running MATLAB in your job.'
        errors.append(msg)
    elif queue != "bigmem":
        msg = 'MATLAB is only enabled on the large memory server. Use the bigmem queue. Example: #PBS -q bigmem.'
        errors.append(msg)

##### MAIN END #####

# pass the input through
for line in lines:
    sys.stdout.write(line)

# check for duplicate errors or warnings
if username in exemptUsers or jobname in exemptJobs:
    errors = []
    warnings = []
elif pbs or interactive:
    errors = list(set(errors))
    warnings = list(set(warnings))
    numerr = str(len(errors))
    numwarn = str(len(warnings))
else:
    errors = []
    warnings = []
    msg = 'PBS options are missing. Please make sure you are submitting a Torque script.'
    errors.append(msg)

# prints errors for users
if errors or warnings:
    numerr = str(len(errors))
    m = os.popen(sendmailCommand, "w")
    m.write("To: Matt Flister <maflister@mcw.edu>\n")
    m.write("From: no-reply@rcc.mcw.edu>\n")
    m.write("Subject: Job Blocked by Torque Submit Filter\n")
    m.write('\nUser: ' + os.getlogin() + '\n')
    m.write('Submit Host: ' + os.uname()[1] + '\n')
    m.write('\nSubmit script has '+numerr+' error(s). Please see below.\n----------------------------------------------------------------------------------\n')
    if errors:
        sys.stderr.write('\nYour job submission script has '+numerr+' error(s). Please see below.\n----------------------------------------------------------------------------------\n')
        m.write('Errors:\n----------------------------------------------------------------------------------\n')
    for error in errors:
        sys.stderr.write(error)
        sys.stderr.write('\n----------------------------------------------------------------------------------\n')
        m.write(error)
        m.write('\n----------------------------------------------------------------------------------\n')
    if warnings:
        if int(numwarn) == 1:
            sys.stderr.write('\nYour job submission script has '+numwarn+' advisory. Please see below.\n----------------------------------------------------------------------------------\n')
        else:
            sys.stderr.write('\nYour job submission script has '+numwarn+' advisories. Please see below.\n----------------------------------------------------------------------------------\n')
        m.write('Advisory:\n')
    for warning in warnings:
        sys.stderr.write(warning)
        sys.stderr.write('\n----------------------------------------------------------------------------------\n')
        m.write(warning)
        m.write('\n----------------------------------------------------------------------------------\n')
    sys.stderr.write('\nFor more information please see http://wiki.rcc.mcw.edu/Torque_Submission_Scripts\nand http://wiki.rcc.mcw.edu/Carley_MPI_Cluster.\n----------------------------------------------------------------------------------\n')
    m.write('Torque job script:\n')
    for line in lines:
        m.write(line)
    m.write('\n----------------------------------------------------------------------------------\n')
    m.close()
    if errors:
        sys.exit(-1)

