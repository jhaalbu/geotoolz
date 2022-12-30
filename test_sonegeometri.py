# import sys
# sys.path.append('../')
import math
from sonegeometri import sonegeometri

def test_sonegeometri():
    b0 = 1
    qv = 500
    qh = 200
    tan_ro = 0.577
    ro = math.atan(tan_ro)
    r = 0.5

    beta1, beta2, beta3, beta4, theta, r1, r2 = sonegeometri(b0, qv, qh, ro, r)

    assert int(math.degrees(beta1)) == 35
    assert int(math.degrees(beta2)) == 84
    assert int(math.degrees(beta3)) == 60
    assert int(math.degrees(beta4)) == 30
    assert int(math.degrees(theta)) == 65
    assert int(math.degrees(r1)) == 38
    assert int(math.degrees(r2)) == 73

