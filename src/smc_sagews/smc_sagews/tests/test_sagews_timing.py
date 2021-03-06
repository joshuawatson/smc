# test_sagews_timing.py
# tests of sage worksheet that measure test duration

# at present I don't see a pytest api feature for this
# other than --duration flag which is experimental and
# for profiling only
import pytest
import socket
import conftest
import os
import re
import time

def test_basic_timing():
    start = time.time()
    os.system('sleep 1')
    tick = time.time()
    elapsed = tick - start
    assert 1.0 == pytest.approx(elapsed, abs = 0.1)

def test_load_sage():
    start = time.time()
    # maybe put first load into fixture
    os.system("echo '2+2' | /usr/local/bin/sage -python")
    tick = time.time()
    elapsed = tick - start
    print("elapsed 1: %s"%elapsed)
    # second load after things are cached
    start = time.time()
    os.system("echo '2+2' | /usr/local/bin/sage -python")
    tick = time.time()
    elapsed = tick - start
    print("elapsed 2: %s"%elapsed)
    assert elapsed < 2.0

def test_import_sage_server():
    start = time.time()
    os.system("echo 'import sage_server' | /usr/local/bin/sage -python")
    tick = time.time()
    elapsed = tick - start
    print("elapsed %s"%elapsed)
    assert elapsed < 10.0

@pytest.mark.no_session
def test_2plus2_timing(test_id):
    if('no_session' not in pytest.config.option.markexpr):
        pytest.skip("this test requires pytest -m no_session")

    import sys

    # if sage_server is running, stop it
    os.system("smc-sage-server stop")

    # start the clock
    start = time.time()

    # start a new sage_server process
    os.system("smc-sage-server start")
    print("sage_server start time %s sec"%(time.time() - start))
    # add pause here because sometimes the log file isn't ready immediately
    time.sleep(0.5)

    # setup connection to sage_server TCP listener
    host, port = conftest.get_sage_server_info()
    print("host %s  port %s"%(host, port))

    # multiple tries at connecting because there's a delay between
    # writing the port number and listening on the socket for connections
    for attempt in range(10):
        attempt += 1
        print("attempt %s"%attempt)
        try:

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            break
        except:
            print(sys.exc_info()[0])
            pass
        time.sleep(0.5)
    else:
        pytest.fail("Could not connect to sage_server at port %s"%port)
    print("connected to socket")

    # unlock
    conftest.client_unlock_connection(sock)
    print("socket unlocked")
    conn = conftest.ConnectionJSON(sock)
    c_ack = conn._recv(1)
    assert c_ack == 'y',"expect ack for token, got %s"%c_ack

    # start session
    msg = conftest.message.start_session()
    msg['type'] = 'sage'
    conn.send_json(msg)
    print("start_session sent")
    typ, mesg = conn.recv()
    assert typ == 'json'
    pid = mesg['pid']
    print("sage_server PID = %s" % pid)

    code = "2+2\n"
    output = "4\n"

    m = conftest.message.execute_code(code = code, id = test_id)
    m['preparse'] = True

    # send block of code to be executed
    conn.send_json(m)

    # check stdout
    typ, mesg = conn.recv()
    assert typ == 'json'
    assert mesg['id'] == test_id
    assert mesg['stdout'] == output

    # teardown connection
    conn.send_json(conftest.message.terminate_session())
    print("\nExiting Sage client.")

    # check timing
    elapsed = time.time() - start
    print("elapsed 2+2 %s"%elapsed)
    assert elapsed < 15.0

    return



##
