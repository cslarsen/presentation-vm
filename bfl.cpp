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
    memset(memory, 0, sizeof(uint8_t)*memsize);
  }

  ~Program()
  {
    free(memory);
  }

  void compile(FILE *f)
  {
    jit_prolog();

    // V0 -- base pointer to memory
    jit_movi(JIT_V0, reinterpret_cast<jit_word_t>(memory));

    // V1 -- offset pointer to memory
    jit_movi(JIT_V1, 0);

    for ( int c=fgetc(f); c != EOF; c = fgetc(f) ) {
      switch ( c ) {
        case '<':
          jit_addi(JIT_V1, JIT_V1, -1);
          break;
        case '>':
          jit_addi(JIT_V1, JIT_V1, 1);
          break;
        case '+':
          jit_ldxr(JIT_V2, JIT_V0, JIT_V1);
          jit_addi(JIT_V2, JIT_V2, 1);
          jit_stxr(JIT_V0, JIT_V1, JIT_V2);
          break;
        case '-':
          jit_ldxr(JIT_V2, JIT_V0, JIT_V1);
          jit_addi(JIT_V2, JIT_V2, -1);
          jit_stxr(JIT_V0, JIT_V1, JIT_V2);
          break;
        case '.':
          jit_ldxr(JIT_V2, JIT_V0, JIT_V1);
          jit_prepare();
          jit_pushargr(JIT_V2);
          jit_finishi(reinterpret_cast<jit_pointer_t>(putchar));
          break;
        case ',':
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
