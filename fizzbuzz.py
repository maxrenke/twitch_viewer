def fizzbuzz(n):
    """
    Determine which number to play in a fizzbuzz round (1 to 10).

    Args:
        n (int): Number to play in the round.

    Returns:
        str: "Fizz" or "Buzz" or the number itself.
    """
    if n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return n
