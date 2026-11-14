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
  la t0, input_file_ptr
  lw a0, 0(t0)
  jal read_int
  addi s0, sp, 32
  sw a0, -16(s0)
  lw t0, -16(s0)
  sw t0, -12(s0)
  lw t0, -12(s0)
  sw t0, -20(s0)
  lw a1, -20(s0)
  li a0, 1
  ecall
  li a1, 10
  li a0, 11
  ecall
  li t0, 0
  sw t0, -24(s0)
  lw t0, -24(s0)
  mv a0, t0
  j _main_exit
_main_exit:
  li a0, 10
  ecall