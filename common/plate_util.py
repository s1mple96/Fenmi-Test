import random
import string


def random_plate_letter():
    # 车牌字母不含I/O
    return random.choice([c for c in string.ascii_uppercase if c not in 'IO'])

def random_plate_number():
    # 5位数字+字母组合
    chars = [random_plate_letter() for _ in range(2)]
    nums = [str(random.randint(0, 9)) for _ in range(3)]
    return ''.join(chars + nums) 