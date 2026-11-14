# Transforms IR into RV32IM files
import re


class RV32Transformer:
    def __init__(self, ir_body):
        self.lines = [l.strip() for l in ir_body.splitlines() if l.strip()]
        self.out = []
        self.slots = {}
        self.globals = []
        self.fields = {}
        self.frame = 0
        self.is_main = False

    def emit(self, s):
        self.out.append("  " + s)

    def field_offset(self, name):
        if name not in self.fields:
            raise ValueError(f"Unknown field '{name}' (known: {list(self.fields)})")
        return self.fields[name]

    @staticmethod
    def extra_arg_index(x):
        """If x is a8, a9, ... return its index into stack_args (0, 1, ...), else None."""
        m = re.fullmatch(r"a(\d+)", x)
        if m and int(m.group(1)) >= 8:
            return int(m.group(1)) - 8
        return None

    def load(self, reg, x):
        if x in self.slots:
            self.emit(f"lw {reg}, {self.slots[x]}(s0)")
        elif x.startswith("@"):
            self.emit(f"la {reg}, g_{x[1:]}")
            self.emit(f"lw {reg}, 0({reg})")
        elif re.fullmatch(r"-?\d+", x):
            self.emit(f"li {reg}, {x}")
        else:
            self.emit(f"mv {reg}, {x}")

    def store(self, reg, x):
        if x in self.slots:
            self.emit(f"sw {reg}, {self.slots[x]}(s0)")
        elif x.startswith("@"):
            self.emit(f"la t1, g_{x[1:]}")
            self.emit(f"sw {reg}, 0(t1)")
        else:
            self.emit(f"mv {x}, {reg}")

    def run(self):
        for l in self.lines:
            if l.startswith("global @"):
                self.globals.append(l.split()[1][1:])
            elif l.startswith("field "):
                self.fields.setdefault(l.split()[1], 4 * len(self.fields))

        # How many extra (a8+) argument words are needed anywhere in the program?
        max_arg = -1
        for l in self.lines:
            m = re.match(r"(?:mv|sw) a(\d+)\b", l)
            if m:
                max_arg = max(max_arg, int(m.group(1)))
        n_extra = max(0, max_arg - 7)

        self.out += [".globl main", ".import berkeley_utils.s", ".import read_int.s", "",
                     ".data", "input_file_ptr: .word 0"]
        self.out += [f"g_{g}: .word 0" for g in self.globals]
        if n_extra:
            self.out.append("stack_args: .word 0")
            self.out += [".word 0"] * (n_extra - 1)
        self.out += ["", ".text"]

        for i, l in enumerate(self.lines):
            t = l.replace(",", " ").split()
            op = t[0]

            if op == "function":
                name = t[1].rstrip(":")
                j = i + 1
                while j < len(self.lines) and not self.lines[j].startswith("function "):
                    j += 1
                body = self.lines[i + 1:j]
                names = [x.split()[1] for x in body if x.startswith("alloc ")]
                names += [x.split()[-1] for x in body if re.match(r"sw a\d", x)]
                names += list(dict.fromkeys(re.findall(r"%t\d+", "\n".join(body))))
                self.slots = {n: -(12 + 4 * k) for k, n in enumerate(names)}
                self.frame = (8 + 4 * len(self.slots) + 15) // 16 * 16
                self.is_main = name == "main"

                F = self.frame
                self.out += ["", f"{name}:"]
                self.emit(f"addi sp, sp, -{F}")
                self.emit(f"sw ra, {F - 4}(sp)")
                self.emit(f"sw s0, {F - 8}(sp)")
                self.emit(f"addi s0, sp, {F}")
                if self.is_main:
                    # ORIGINAL setup restored: store argv[1] pointer
                    self.emit("lw t0, 4(a1)")
                    self.emit("la t1, input_file_ptr")
                    self.emit("sw t0, 0(t1)")

            elif op in ("struct", "field", "global", "alloc") \
                    or l.startswith(("#", "addi")) or "(sp)" in l:
                continue

            elif l.endswith(":"):
                self.out.append(l)

            elif op == "ret":
                if self.is_main:
                    self.emit("li a0, 10")
                    self.emit("ecall")
                else:
                    for s in ["lw ra, -4(s0)", "mv t0, s0", "lw s0, -8(s0)", "mv sp, t0", "ret"]:
                        self.emit(s)

            elif op == "li":
                self.emit(f"li t0, {t[2]}")
                self.store("t0", t[1])

            elif op == "lw":
                self.load("t0", t[2])
                self.store("t0", t[1])

            elif op == "sw":
                idx = self.extra_arg_index(t[1])
                if idx is not None:
                    # callee: copy incoming a8+ param out of the shared buffer
                    self.emit("la t0, stack_args")
                    self.emit(f"lw t0, {4 * idx}(t0)")
                else:
                    self.load("t0", t[1])
                self.store("t0", t[2])

            elif op == "mv":
                self.load("t0", t[2])
                idx = self.extra_arg_index(t[1])
                if idx is not None:
                    # caller: place outgoing a8+ argument into the shared buffer
                    self.emit("la t1, stack_args")
                    self.emit(f"sw t0, {4 * idx}(t1)")
                else:
                    self.store("t0", t[1])

            elif op in ("add", "sub", "mul", "div", "and", "or", "slt",
                        "sgt", "sle", "sge", "seq", "sne"):
                self.load("t0", t[2])
                self.load("t1", t[3])
                if op == "sgt":
                    self.emit("slt t2, t1, t0")
                elif op == "sle":
                    self.emit("slt t2, t1, t0")
                    self.emit("xori t2, t2, 1")
                elif op == "sge":
                    self.emit("slt t2, t0, t1")
                    self.emit("xori t2, t2, 1")
                elif op == "seq":
                    self.emit("sub t2, t0, t1")
                    self.emit("seqz t2, t2")
                elif op == "sne":
                    self.emit("sub t2, t0, t1")
                    self.emit("snez t2, t2")
                else:
                    self.emit(f"{op} t2, t0, t1")
                self.store("t2", t[1])

            elif op == "seqz":
                self.load("t0", t[2])
                self.emit("seqz t2, t0")
                self.store("t2", t[1])

            elif op == "neg":
                self.load("t0", t[2])
                self.emit("sub t2, zero, t0")
                self.store("t2", t[1])

            elif op == "beqz":
                self.load("t0", t[1])
                self.emit(f"beqz t0, {t[2]}")

            elif op == "j":
                target = t[1]
                self.emit(f"j {target}")

            elif op == "jal":
                self.emit(f"jal {t[1]}")

            elif op == "call":
                self.emit(f"jal {t[1]}")
                # restore frame pointer in case the callee clobbered s0
                self.emit(f"addi s0, sp, {self.frame}")
                self.store("a0", t[2])

            elif op in ("print", "println"):
                self.load("a1", t[1])
                self.emit("li a0, 1")
                self.emit("ecall")
                if op == "println":
                    self.emit("li a1, 10")
                    self.emit("li a0, 11")
                    self.emit("ecall")

            elif op == "new":                         # new %t, Struct
                self.emit(f"li a1, {4 * max(1, len(self.fields))}")
                self.emit("li a0, 9")
                self.emit("ecall")
                self.store("a0", t[1])

            elif op == "delete":
                pass                                  # Venus has no free

            elif op == "load_field":                  # load_field %t, obj, field
                self.load("t0", t[2])
                self.emit(f"lw t2, {self.field_offset(t[3])}(t0)")
                self.store("t2", t[1])

            elif op == "store_field":                 # store_field src, obj, field
                self.load("t0", t[1])
                self.load("t1", t[2])
                self.emit(f"sw t0, {self.field_offset(t[3])}(t1)")

            else:
                self.emit(f"# UNHANDLED: {l}")

        return "\n".join(self.out)