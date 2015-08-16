#include <stdio.h>
#include <stdint.h>

extern "C" {
#include <lightning.h>
}

static jit_state_t *_jit;
typedef void (*vfptr)(void);

struct Program {
  uint8_t *memory;
  vfptr code;

  Program(const size_t memsize = 100000)
    : memory(static_cast<uint8_t*>(malloc(sizeof(uint8_t)*memsize)))
  {
    memset(&memory[0], 0, sizeof(uint8_t)*memsize);
  }

  ~Program()
  {
    free(memory);
  }

  void compile(FILE *f)
  {
    jit_prolog();

    // R0 -- base pointer to memory
    jit_movi(JIT_R0, reinterpret_cast<jit_word_t>(&memory[0]));

    // R1 -- offset pointer to memory
    jit_movi(JIT_R1, 0);

    for ( int c=0; c != EOF; c = fgetc(f) ) {
      switch ( c ) {
        case '<':
          jit_addi(JIT_R1, JIT_R1, -1);
          break;
        case '>':
          jit_addi(JIT_R1, JIT_R1, 1);
          break;
        case '+':
          jit_ldxr(JIT_R2, JIT_R0, JIT_R1);
          jit_addi(JIT_R2, JIT_R2, 1);
          jit_stxr(JIT_R0, JIT_R1, JIT_R2);
          break;
        case '-':
          jit_ldxr(JIT_R2, JIT_R0, JIT_R1);
          jit_addi(JIT_R2, JIT_R2, -1);
          jit_stxr(JIT_R0, JIT_R1, JIT_R2);
          break;
        case '.':
          jit_ldxr(JIT_R2, JIT_R0, JIT_R1);
          jit_pushargr(JIT_R2);
          jit_prepare();
          jit_finishi(reinterpret_cast<jit_pointer_t>(putchar));
          jit_retr(JIT_R2);
 //         jit_ret();
          // call putchar with JIR_R2 as arg
          break;
        case ',':
          jit_movi(JIT_R2, 0); // should be result of getchar
          jit_prepare();
          jit_finishi(reinterpret_cast<jit_pointer_t>(getchar));
          jit_ret();
          jit_stxr(JIT_R0, JIT_R1, JIT_R2);
          break;
        case '[':
          break;
        case ']':
          break;
        default:
          break;
      }
    }

    jit_epilog();
    code = reinterpret_cast<vfptr>(jit_emit());
  }

  void run()
  {
    code();
  }
};

int main(int argc, char *argv[])
{
  init_jit(argv[0]);
  _jit = jit_new_state();

  for ( size_t n=1; n<argc; ++n ) {
    if ( argv[n][0] == '-' )
      continue;
    FILE *f = fopen(argv[n], "rt");
    if ( f ) {
      Program p;
      p.compile(f);
      fclose(f);
      p.run();
    }
  }

  jit_clear_state();
  jit_destroy_state();
  finish_jit();
  return 0;
}
