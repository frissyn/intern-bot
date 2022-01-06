import re


res = "```{hl}\n {data}\n```"
text = lambda x: open(x, "r").read()
result = lambda hl, data: res.format(hl=hl, data=data)


def _line(file: str, lnum: int, hl: str="txt"):
    soup = text(file)

    for i, line in enumerate(soup.split("\n")):
        if i == int(lnum) - 1:
            return result(hl, line)
    
    return result(hl, "Error: NOT FOUND") 


def _from(file: str, keyword: str, last=None, hl: str="txt"):
    soup = text(file)

    if not last:
        index = soup.rfind(keyword, 0)
        cap = len(soup)
    else:
        indices = [m.start() for m in re.finditer(keyword, soup)]
        index = indices[-int(last)]
        cap = indices.index(index) + 1

        if cap < len(indices):
            cap = indices[cap]
        else:
            cap = len(soup)

    if index == -1:
        return result(hl, "Error: NOT FOUND")
    else:
        return result(hl, soup[index:cap])


SUBS = {
    "line": {
        "exec": _line,
        "def": "_line(file, lnum, hl='txt')"
    },
    "from": {
        "exec": _from,
        "def": "_from(file, keyword, last=None, hl='txt')"
    }
}
