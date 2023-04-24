import collections
import hashlib
import random
import binascii
import sys
import libnum

EllipticCurve = collections.namedtuple('EllipticCurve', 'name p a b g n h')

curve = EllipticCurve(
    'secp256k1',
    # Field characteristic.
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f,
    # Curve coefficients.
    a=0,
    b=7,
    # Base point.
    g=(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
       0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8),
    # Subgroup order.
    n=0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141,
    # Subgroup cofactor.
    h=1,
)

def is_curve_point(point):
    if point is None:
        return True
    x, y = point
    return (y * y - x * x * x - curve.a * x - curve.b) % curve.p == 0

def add_points(point1, point2):
    assert is_curve_point(point1)
    assert is_curve_point(point2)

    if point1 is None:
        return point2
    if point2 is None:
        return point1

    x1, y1 = point1
    x2, y2 = point2

    if x1 == x2 and y1 != y2:
        return None

    if x1 == x2:
        m = (3 * x1 * x1 + curve.a) * libnum.invmod(2 * y1, curve.p)
    else:
        m = (y1 - y2) * libnum.invmod(x1 - x2, curve.p)

    x3 = m * m - x1 - x2
    y3 = y1 + m * (x3 - x1)
    result = (x3 % curve.p, -y3 % curve.p)
    assert is_curve_point(result)
    return result


def scalar_mult(k, point):
    assert is_curve_point(point)

    if k % curve.n == 0 or point is None:
        return None

    if k < 0:
        return scalar_mult(-k, point_neg(point))

    result = None
    addend = point

    while k:
        if k & 1:
            result = add_points(result, addend)
        addend = add_points(addend, addend)
        k >>= 1

    assert is_curve_point(result)
    return result



def gen_keypair():
    private_key = random.randrange(1, curve.n) #should use a HD wallet BIP32 model in practice for generation
    public_key = scalar_mult(private_key, curve.g)
    return private_key, public_key

