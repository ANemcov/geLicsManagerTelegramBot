import subprocess

utilsPath = ''
rootPassword = ''
bitmobileHost = ''


def get_sp(sn):
    sp = None
    try:
        cmd = utilsPath 
        args = f' -sgp -host {bitmobileHost} -p {rootPassword} -sn {sn}'
        output = subprocess.run(cmd + args, capture_output=True)
        sp = str(output.stdout.decode().replace("\r\n", ''))
    except Exception as e:
        print(f"io error : {e}")

    return sp


def get_lics(sn, sp):
    output = ""
    try:
        cmd = utilsPath
        args = f' -glicc -host {bitmobileHost} -sp {sp} -sn {sn}'
        output = subprocess.run(cmd + args, capture_output=True)
        output = output.stdout
    except Exception as e:
        print(f"io error : {e}")

    return output


def slic(sn, lic_num):
    output = ""
    try:
        cmd = utilsPath
        args = f' -slic -host {bitmobileHost} -p {rootPassword} -sn {sn} -slic {lic_num}'
        output = subprocess.run(cmd + args, capture_output=True) 
        output = output.stdout 
    except Exception as e:
        print(f"io error: {e}")

    return output


if __name__ == '__main__':
    # print(getSP('demo'))
    pass
