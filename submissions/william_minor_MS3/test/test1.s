.globl main
.import berkeley_utils.s
.import read_int.s

.data
input_file_ptr: .word 0

.text

main:
  lw t0, 4(a1)
  la t1, input_file_ptr
  sw t0, 0(t1)
  addi sp, sp, -32
  addi t3, sp, 32
  sw ra, -4(t3)
  sw s0, -8(t3)
  mv s0, t3
  li t0, 5
  sw t0, -16(s0)
  lw t0, -16(s0)
  sw t0, -12(s0)
  lw t0, -12(s0)
  sw t0, -20(s0)
  lw t0, -20(s0)
  mv a0, t0
  j _main_exit
_main_exit:
  li a0, 10
  ecall