import serial
import time
import signal
import sys
import datetime


def send_command(cmd):
    port.write((cmd + '\n').encode('ASCII'))


def read_response():
    # last character is LF so omit that
    return port.read_until(expected=serial.LF).decode("ASCII")[0:-1]


def signal_handler(sig, frame):
    if port:
        port.close()
        print('disconnected')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

port = serial.Serial('/dev/ttyUSB0', 
        baudrate=19200, 
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE, 
        stopbits=serial.STOPBITS_ONE,
        timeout=2,
        xonxoff=False,
        rtscts=True,
        dsrdtr=True,
        exclusive=True)

if port:
    print('connected')
    # check if device is a CSA803C
    send_command('ID?')
    id_response = read_response()
    print('id response: %s' % id_response)
    is_csa803c = (len(id_response) >= 15) and (id_response[0:14] == 'ID TEK/CSA803C')
    if not is_csa803c:
        print('not a CSA803C')
    else:
        # show sampling heads
        send_command('SAM? M')
        sam_response = read_response()
        print('sampling heads: %s' % sam_response)
        print('listening for hardcopy...')
        buf = []
        while True:
            # try to read 10K, it will time out with less data
            incoming = port.read(size=10240)
            if len(incoming) == 0:
                # if there is data in buf, save that, this is the screenshot
                if len(buf) > 0:
                    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                    print('saving buffer %d to %s' % (len(buf), now))
                    with open('/home/ubuntu/sambashare/%s.tiff' % now, 'wb') as f:
                        for i in range(0, len(buf)):
                            f.write(buf[i])
                    buf = []
            else:
                # save incoming to buffer
                print('incoming %d/%d' % (len(incoming), len(buf)))
                buf.append(incoming)
            time.sleep(1)
    print('disconnected')
else:
    print('cannot connect')
