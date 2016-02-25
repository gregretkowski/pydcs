def loads(tablestr):

    class Parser():

        def __init__(self, buffer):
            self.buffer = buffer
            self.buflen = len(buffer)
            self.pos = 0
            self.lineno = 1

        def value(self):
            self.eat_ws()

            if self.buffer[self.pos] == '{':
                return self.object()
            elif self.buffer[self.pos] == '"':
                return self.string()
            elif self.char().isnumeric() or self.char() == '-':
                return self.number()
            else:  # varname
                varname = self.eatvarname()
                if varname == 'false' or varname == 'true':
                    return varname == 'true'
                self.eat_ws()
                if not self.eob() and self.buffer[self.pos] == '=':
                    self.pos += 1
                    return {varname: self.value()}
                else:
                    se = SyntaxError()
                    se.text = varname + " '" + self.char() + "'"
                    se.lineno = self.lineno
                    se.offset = self.pos
                    raise se

            return {}

        def string(self):
            if self.char() != '"':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character '\"', got '{char}'".format(char=self.char())
                raise se

            state = 0
            s = ''
            while state != 1:
                if self.advance():
                    raise self.eob_exception()

                c = self.char()
                if state == 0:
                    if c == '"':
                        state = 1
                        self.advance()
                    elif c == '\\':
                        state = 2
                    else:
                        s += c
                if state == 2:
                    s += c
                    state = 0
            return s

        def number(self):
            n = ''
            sign = 1
            if self.char() == '-':
                sign = -1
                if self.advance():
                    raise self.eob_exception()

            while (not self.eob() and
                    (self.char().isnumeric() or self.char() == '.' or
                        self.char().lower() == 'e')):
                n += self.char()
                self.advance()

            num = float(n) * sign
            if num.is_integer():
                return int(num)
            return num

        def object(self):
            d = {}
            if self.char() != '{':
                se = SyntaxError()
                se.lineno = self.lineno
                se.offset = self.pos
                se.text = "Expected character '{', got '{char}'".format(char=self.char())
                raise se

            if self.advance():
                raise self.eob_exception()

            self.eat_ws()

            while self.char() != '}':
                self.eat_ws()

                if self.char() != '[':
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Expected character '[', got '{char}'".format(char=self.char())
                    raise se

                if self.advance():
                    raise self.eob_exception()

                self.eat_ws()
                if self.char() == '"':
                    key = self.string()
                else:
                    key = self.number()

                if self.eob():
                    raise self.eob_exception()

                self.eat_ws()

                if self.char() != ']':
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Expected character ']', got '{char}'".format(char=self.char())
                    raise se

                if self.advance():
                    raise self.eob_exception()

                self.eat_ws()

                if self.char() != '=':
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Expected character '=', got '{char}'".format(char=self.char())
                    raise se

                if self.advance():
                    raise self.eob_exception()

                val = self.value()

                self.eat_ws()

                d[key] = val
                # print(key, ':', val)

                if self.char() == '}':
                    break
                elif self.char() == ',':
                    if self.advance():
                        raise self.eob_exception()
                    self.eat_ws()
                else:
                    se = SyntaxError()
                    se.lineno = self.lineno
                    se.offset = self.pos
                    se.text = "Unexpected character '{char}'".format(char=self.char())
                    raise se

            self.advance()

            return d

        def eatvarname(self):
            varname = ''
            while (not self.eob()) and self.buffer[self.pos].isalnum():
                varname += self.buffer[self.pos]
                self.pos += 1

            return varname

        def eat_comment(self):
            if (self.char() == '-' and
                self.pos + 1 < self.buflen and
                self.buffer[self.pos + 1] == '-'):
                while not self.eob() and self.char() != '\n':
                    self.advance()

        def eat_ws(self):
            self.eat_comment()
            while not self.eob() and self.char().isspace():
                if self.char() == '\n':
                    self.lineno += 1
                self.pos += 1
                self.eat_comment()

        def eob(self):
            return self.pos >= self.buflen

        def eob_exception(self):
            se = SyntaxError()
            se.lineno = self.lineno
            se.offset = self.pos
            se.text = "Unexpected end of buffer"
            return se

        def char(self):
            return self.buffer[self.pos]

        def advance(self):
            self.pos += 1
            return self.eob()

    p = Parser(tablestr)
    return p.value()
