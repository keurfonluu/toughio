def to_float(s):
    """Convert variable string to float."""
    try:
        return float(s.replace("d", "e"))

    except ValueError:
        # It's probably something like "0.0001-001"
        significand, exponent = s[:-4], s[-4:]
        return float("{}e{}".format(significand, exponent))


def to_str(x, fmt):
    """Convert variable to string."""
    x = "" if x is None else x

    if not isinstance(x, str):
        # Special handling for floating point numbers
        if "f" in fmt:
            # Number of decimals is specified
            if "." in fmt:
                n = int(fmt[3:].split(".")[0])
                tmp = fmt.format(x)

                if len(tmp) > n:
                    return fmt.replace("f", "e").format(x)

                else:
                    return tmp

            # Let Python decides the format
            else:
                n = int(fmt[3:].split("f")[0])
                tmp = str(float(x))

                if len(tmp) > n:
                    fmt = "{{:>{}.{}e}}".format(n, n - 7)

                    return fmt.format(x)

                else:
                    fmt = "{{:>{}}}".format(n)

                    return fmt.format(tmp)

        else:
            return fmt.format(x)

    else:
        return fmt.replace("g", "").replace("e", "").replace("f", "").format(x)
