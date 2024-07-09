from os import system
from pyuac import runAsAdmin, isUserAdmin

#CHANGES NETWORK DEFAULT TO IPV4 OR IPV6
def ipv_default(default):
    if int(default) == 4:# CHANGES IPV4 TO DEFAULT
        system('netsh interface ipv6 set prefix ::/96 60 3"')
        system('netsh interface ipv6 set prefix ::ffff:0:0/96 55 4"')
        system('exit') #Closes Terminal Window
        #system('netsh interface ipv6 show prefixpolicies') # Checks to see what prefixes are prioritised

    elif int(default) == 6:# CHANGES IPV6 TO DEFAULT (RESET)
        system('netsh interface ipv6 set prefixpolicy ::1/128 50 0')
        system('netsh interface ipv6 set prefixpolicy ::/0 40 1')
        system('netsh interface ipv6 set prefixpolicy ::ffff:0:0/96 35 4')
        system('netsh interface ipv6 set prefixpolicy 2002::/16 30 2')
        system('netsh interface ipv6 set prefixpolicy 2001::/32 5 5')
        system('netsh interface ipv6 set prefixpolicy fc00::/7 3 13')
        system('netsh interface ipv6 set prefixpolicy fec0::/10 1 11')
        system('netsh interface ipv6 set prefixpolicy 3ffe::/16 1 12')
        system('netsh interface ipv6 set prefixpolicy ::/96 1 3')
        system('exit') #Closes Terminal Window
        #system('netsh interface ipv6 show prefixpolicies') # Checks to see what prefixes are prioritised


    else:
        print("Choose either 4 or 6")
def ipv_change(default):
    if not isUserAdmin():
        print("Re-launching as admin!")
        runAsAdmin()
    else:
        ipv_default(default)


#Example: TAKES EITHER 4 or 6
ipv_change(4)

