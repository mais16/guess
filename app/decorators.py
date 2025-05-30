def guess_decorator(function):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        if isinstance(result, str):
            return f"<h2 style='color:yellow'>{result}</h2>"
        return result
    return wrapper 