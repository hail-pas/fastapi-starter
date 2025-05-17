import random
import string


def generate_random_string(
    length: int,
    all_digits: bool = False,
    excludes: list[str] | None = None,
) -> str:
    """生成任意长度字符串."""
    if excludes is None:
        excludes = []
    all_char = string.digits if all_digits else string.ascii_letters + string.digits
    if excludes:
        for char in excludes:
            all_char = all_char.replace(char, "")
    # return "".join(random.sample(all_char, length))
    return "".join(random.SystemRandom().choice(all_char) for _ in range(length))
