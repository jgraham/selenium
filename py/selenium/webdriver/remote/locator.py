from selenium.webdriver.common.by import By

def css_escape_ident(value):
    # http://dev.w3.org/csswg/cssom/#serialize-an-identifier
    def escape(char):
        return "\\%s" % hex(ord(char))[2:]

    rv = []
    for i, char in enumerate(value):
        if char == "\x00":
            raise InvalidSelectorException("Invalid locator values passed in")
        elif "\x01" <= char <= "\x1f":
            rv.append(escape(char))
        elif i == 0 and '0' <= char <= '9':
            rv.append(escape(char))
        elif i == 1 and value[0] == "-" and '0' <= char <= '9':
            rv.append(escape(char))
        elif (char >= "\x80" or char == "-" or char == "_" or
              '0' <= char <= '9' or 'a' <= char <= 'z' or 'A' <= char <= 'Z'):
            rv.append(char)
        else:
            rv.append(escape(char))
    return "".join(rv)

def normalise_locator(by, value):
    if not By.is_valid(by) or not isinstance(value, str):
        raise InvalidSelectorException("Invalid locator values passed in")

    if by == By.ID:
        by = By.CSS_SELECTOR
        value = '#%s' % css_escape_ident(value)
    elif by == By.TAG_NAME:
        by = By.CSS_SELECTOR
        value = css_escape_ident(value)
    elif by == By.CLASS_NAME:
        by = By.CSS_SELECTOR
        value = ".%s" % css_escape_ident(value)
    elif by == By.NAME:
        by = By.CSS_SELECTOR
        value = "*[name=%s]" % css_escape_ident(value)

    return by, value
