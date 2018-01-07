import subprocess
try:
    salida = subprocess.check_output("java RaspberryClientWS",stderr= subprocess.STDOUT,shell=True)
    
    print(salida)
except subprocess.CalledProcessError, ex:
    print(ex.cmd)
    print(ex.message)
    print(ex.returncode)
    print(ex.output)
