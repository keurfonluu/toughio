def to_str(x, fmt):
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
