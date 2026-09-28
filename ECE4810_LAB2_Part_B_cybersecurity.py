# ============================================================
# ECE4810 IoT - Activity 3
# ============================================================

import time, itertools, string

def human_time(seconds):
    if seconds < 1:
        return f"{seconds*1000:.1f} milliseconds"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    if seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    if seconds < 31536000:
        return f"{seconds/86400:.1f} days"
    return f"{seconds/31536000:,.1f} years"

print("#" * 60)
print("# PART 1 - Given code: Caesar Cipher")
print("#" * 60)

def caesar_encrypt(realText, step):
    outText = []
    cryptText = []
    uppercase = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
                 'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    lowercase = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                 'n','o','p','q','r','s','t','u','v','w','x','y','z']
    for eachLetter in realText:
        if eachLetter in uppercase:
            index = uppercase.index(eachLetter)
            crypting = (index + step) % 26
            cryptText.append(crypting)
            newLetter = uppercase[crypting]
            outText.append(newLetter)
        elif eachLetter in lowercase:
            index = lowercase.index(eachLetter)
            crypting = (index + step) % 26
            cryptText.append(crypting)
            newLetter = lowercase[crypting]
            outText.append(newLetter)
    return outText

code = caesar_encrypt('ABC', 3)
print("caesar_encrypt('ABC', 3) =", code)


print("\n" + "#" * 60)
print("# PART 2 - Given code: Reverse-digit password check")
print("#" * 60)

def reverse_password(message):
    # (input() replaced with a fixed value so it runs non-interactively)
    message1 = int(message)
    translated = ''
    i = len(message) - 1
    # mirror the number, e.g. 123 -> 321
    while i >= 0:
        translated = translated + message[i]
        i = i - 1
    print('The cipher text is :', translated)
    number = int(translated)
    # key: only allow if reversed number is greater (ascending)
    if number > message1:
        print('access granted')
    else:
        print('access denied')

print("Input '123' ->")
reverse_password('123')
print("Input '321' ->")
reverse_password('321')


print("\n" + "#" * 60)
print("# PART 4 - MY DESIGNED CIPHER: Keyed Vigenere + Reversal")
print("#" * 60)

ALPHA_U = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
ALPHA_L = [chr(c) for c in range(ord('a'), ord('z') + 1)]

def _shift_letter(letter, amount):
    if letter in ALPHA_U:
        return ALPHA_U[(ALPHA_U.index(letter) + amount) % 26]
    if letter in ALPHA_L:
        return ALPHA_L[(ALPHA_L.index(letter) + amount) % 26]
    return letter  # non-letters unchanged

def _key_shifts(key):
    # convert key letters to shift amounts 0..25
    return [ord(k.lower()) - ord('a') for k in key if k.isalpha()]

def my_encrypt(plaintext, key):
    shifts = _key_shifts(key)
    out = []
    ki = 0
    # Step 1: Vigenere shift (each letter shifted by next key letter)
    for ch in plaintext:
        if ch.isalpha():
            out.append(_shift_letter(ch, shifts[ki % len(shifts)]))
            ki += 1
        else:
            out.append(ch)
    # Step 2: reverse the whole string (transposition)
    return ''.join(out)[::-1]

def my_decrypt(ciphertext, key):
    shifts = _key_shifts(key)
    # Step 1: undo the reversal
    text = ciphertext[::-1]
    out = []
    ki = 0
    # Step 2: shift each letter BACK by the key
    for ch in text:
        if ch.isalpha():
            out.append(_shift_letter(ch, -shifts[ki % len(shifts)]))
            ki += 1
        else:
            out.append(ch)
    return ''.join(out)

msg = "Hello World"
key = "KEY"
ct = my_encrypt(msg, key)
pt = my_decrypt(ct, key)

print("Plaintext :", msg)
print("Key       :", key)
print("Ciphertext:", ct)
print("Decrypted :", pt)
print("Match      :", pt == msg)


print("\n" + "#" * 60)
print("# PART 5 - SECOND CIPHER: XOR Stream Cipher (keyed)")
print("#" * 60)

# A different method from Cipher A.
# Cipher A shifted LETTERS along the alphabet.
# Cipher B works on the raw BYTE VALUE of every character using XOR,
# so it also encrypts digits, spaces and symbols. Output is shown as hex.

def xor_encrypt(plaintext, key):
    key_bytes = [ord(c) for c in key]
    out = bytearray()
    for i, ch in enumerate(plaintext):
        # XOR each character's byte with the next key byte (repeating)
        out.append(ord(ch) ^ key_bytes[i % len(key_bytes)])
    return out.hex()                       # print safely as hex

def xor_decrypt(hex_ciphertext, key):
    key_bytes = [ord(c) for c in key]
    data = bytes.fromhex(hex_ciphertext)
    out = []
    for i, b in enumerate(data):
        out.append(chr(b ^ key_bytes[i % len(key_bytes)]))   # XOR again = original
    return ''.join(out)

msg2 = "Hello World"
key2 = "KEY"
ct2 = xor_encrypt(msg2, key2)
pt2 = xor_decrypt(ct2, key2)

print("\nPlaintext :", msg2)
print("Key       :", key2)
print("Ciphertext:", ct2, "(hex)")
print("Decrypted :", pt2)
print("Match     :", pt2 == msg2)


print("\n" + "-" * 60)
print("How hard is Cipher B (XOR) to hack? (brute force)")
print("-" * 60)

# The XOR key is made of BYTES. Each key position can be any of 256
# byte values, so the keyspace is 256^(key length).

def brute_force_xor(hex_ct, known_plaintext, key_len):
    tried = 0
    start = time.perf_counter()
    # try every possible key of this length (bytes 0..255)
    for combo in itertools.product(range(256), repeat=key_len):
        tried += 1
        key = ''.join(chr(b) for b in combo)
        try:
            if xor_decrypt(hex_ct, key) == known_plaintext:
                return key, tried, time.perf_counter() - start
        except Exception:
            pass
    return None, tried, time.perf_counter() - start

# Actually crack the short keys to prove the attack works
for kl in [1, 2]:
    secret = "AB"[:kl]
    c = xor_encrypt("Hello World", secret)
    found, tried, took = brute_force_xor(c, "Hello World", kl)
    print(f"    key length {kl}: keyspace = 256^{kl} = {256**kl:>10,} | "
          f"cracked after {tried:,} tries in {took:.3f}s")

# Benchmark the speed, then CALCULATE the longer key lengths
c_bench = xor_encrypt("Hello World", "AB")
N = 200000
t0 = time.perf_counter()
for _ in range(N):
    xor_decrypt(c_bench, "AB")
rate_xor = N / (time.perf_counter() - t0)

print(f"\n    Attack speed: {rate_xor:,.0f} keys/second")
print("\n    Estimated time to crack (keyspace / speed):")
print(f"    {'key len':<9}{'keyspace (256^n)':>26}{'estimated time':>20}")
for kl in [1, 2, 3, 4, 5, 6, 8]:
    space = 256 ** kl
    print(f"    {kl:<9}{space:>26,}{human_time(space / rate_xor):>20}")

print("\n    NOTE: XOR has a known weakness - if the attacker already knows")
print("    the plaintext, the key is found INSTANTLY with key = cipher XOR text,")
print("    with NO brute force. So a long, secret, non-reused key is essential.")


print("\n" + "#" * 60)
print("# PART 6 - COMBINED CIPHER (Cipher A then Cipher B)")
print("#" * 60)

# Encrypt with Cipher A (Vigenere + reversal), then encrypt the
# result again with Cipher B (XOR). Two different keys are used,
# so an attacker must guess BOTH keys - the keyspaces MULTIPLY.

def combined_encrypt(plaintext, key_a, key_b):
    step1 = my_encrypt(plaintext, key_a)   # 1) Vigenere + reversal
    step2 = xor_encrypt(step1, key_b)      # 2) XOR -> hex
    return step2

def combined_decrypt(hex_ct, key_a, key_b):
    step1 = xor_decrypt(hex_ct, key_b)     # undo XOR
    return my_decrypt(step1, key_a)        # undo Vigenere + reversal

key_a = "KEY"
key_b = "LOCK"
ct3 = combined_encrypt("Hello World", key_a, key_b)
pt3 = combined_decrypt(ct3, key_a, key_b)

print("\nPlaintext :", "Hello World")
print("Key A     :", key_a, "(Vigenere + reversal)")
print("Key B     :", key_b, "(XOR)")
print("Ciphertext:", ct3, "(hex)")
print("Decrypted :", pt3)
print("Match     :", pt3 == "Hello World")

print("\n" + "-" * 60)
print("How hard is the COMBINED cipher to hack? (brute force)")
print("-" * 60)

# Keyspace = (choices for key A) x (choices for key B)
#          = 26^La  x  256^Lb
# For equal key lengths L:  26^L x 256^L = (26 x 256)^L = 6656^L

def brute_force_combined(hex_ct, known, la, lb):
    tried = 0
    start = time.perf_counter()
    for ca in itertools.product(string.ascii_lowercase, repeat=la):
        ka = ''.join(ca)
        for cb in itertools.product(range(256), repeat=lb):
            kb = ''.join(chr(b) for b in cb)
            tried += 1
            try:
                if combined_decrypt(hex_ct, ka, kb) == known:
                    return (ka, kb), tried, time.perf_counter() - start
            except Exception:
                pass
    return None, tried, time.perf_counter() - start

# Actually crack the smallest case (both keys length 1) to prove it works
c = combined_encrypt("Hello World", "a", "b")
found, tried, took = brute_force_combined(c, "Hello World", 1, 1)
print(f"    both keys length 1: keyspace = 26 x 256 = {26*256:,} | "
      f"cracked after {tried:,} tries in {took:.3f}s")

# Benchmark speed, then CALCULATE the larger key lengths
c_bench = combined_encrypt("Hello World", "a", "b")
N = 100000
t0 = time.perf_counter()
for _ in range(N):
    combined_decrypt(c_bench, "a", "b")
rate_comb = N / (time.perf_counter() - t0)

print(f"\n    Attack speed: {rate_comb:,.0f} keys/second")
print("\n    Estimated time to crack (both keys length L):")
print(f"    {'key len L':<11}{'keyspace (6656^L)':>26}{'estimated time':>20}")
for L in [1, 2, 3, 4, 5, 6]:
    space = (26 * 256) ** L
    print(f"    {L:<11}{space:>26,}{human_time(space / rate_comb):>20}")

print("\n    The combined keyspace is MUCH larger than either cipher alone,")
print("    because the two independent keys multiply together.")


print("\n" + "#" * 60)
print("# BRUTE-FORCE TEST (does the cipher resist attack?)")
print("#" * 60)

import time, itertools, string

# --- (a) Caesar is trivially broken: only 26 keys ---
print("\n(a) Brute forcing the Caesar cipher (only 26 possible keys):")
target = ''.join(caesar_encrypt('HELLO', 3))  # ciphertext = KHOOR
for guess in range(26):
    # decrypt = shift back
    dec = ''.join(ALPHA_U[(ALPHA_U.index(c) - guess) % 26] for c in target)
    if dec == "HELLO":
        print(f"    key found = {guess}  -> '{dec}'   (cracked instantly)")

# --- (b) My cipher: attacker tries every key, checks against known plaintext ---
def brute_force_mycipher(ciphertext, known_plaintext, key_len, alphabet="abcdefghijklmnopqrstuvwxyz"):
    tried = 0
    start = time.perf_counter()
    for combo in itertools.product(alphabet, repeat=key_len):
        k = ''.join(combo)
        tried += 1
        if my_decrypt(ciphertext, k) == known_plaintext:
            return k, tried, time.perf_counter() - start
    return None, tried, time.perf_counter() - start

print("\n(b) Brute forcing MY cipher (attacker knows plaintext 'Hello World'):")
# Actually brute force only the SHORT keys, just to prove the attack works
for kl in [1, 2, 3]:
    secret = "abcdefghijklmnopqrstuvwxyz"[:kl]  # a, ab, abc
    c = my_encrypt("Hello World", secret)
    found, tried, took = brute_force_mycipher(c, "Hello World", kl)
    space = 26 ** kl
    print(f"    key length {kl}: keyspace = 26^{kl} = {space:>12,} | "
          f"found '{found}' after {tried:,} tries in {took:.3f}s")

# ------------------------------------------------------------
# Measure the attack SPEED with a quick benchmark (no full crack),
# so the longer key lengths can be CALCULATED, not brute forced.
# ------------------------------------------------------------
c_bench = my_encrypt("Hello World", "abc")
N = 200000
t0 = time.perf_counter()
for _ in range(N):
    my_decrypt(c_bench, "abc")
rate = N / (time.perf_counter() - t0)   # keys tested per second

# ------------------------------------------------------------
# ESTIMATED TIME TO CRACK (calculated from the measured speed)
# time = number of keys / keys-tested-per-second
# ------------------------------------------------------------

def human_time(seconds):
    if seconds < 1:
        return f"{seconds*1000:.1f} milliseconds"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    if seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    if seconds < 31536000:
        return f"{seconds/86400:.1f} days"
    return f"{seconds/31536000:,.1f} years"

print(f"\n    Attack speed measured on this computer: {rate:,.0f} keys/second")
print("\n    Estimated time to crack (keyspace / speed):")
print(f"    {'key len':<9}{'keyspace (26^n)':>22}{'estimated time':>22}")
for kl in [4, 5, 6, 7, 8, 10, 12]:
    space = 26 ** kl
    est = human_time(space / rate)
    print(f"    {kl:<9}{space:>22,}{est:>22}")
