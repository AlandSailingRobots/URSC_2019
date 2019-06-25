import subprocess

def getGPS():
    python3_command = "python2 gpsPython2.py"

    process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)

    output, error = process.communicate()
    lista = output.decode("utf-8").split()
    return float(lista[0]), float(lista[1])
