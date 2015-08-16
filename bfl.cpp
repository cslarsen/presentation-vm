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
    : memory(new uint8_t[memsize])
  {
    memset(&memory[0], 0, sizeof(uint8_t)*memsize);
  }

  ~Program()
  {
    delete[](memory);
  }

  void compile(FILE *f)
  {
    jit_prolog();

    // Registers:
    // R0 -- base pointer to memory
    jit_movi(JIT_R0, 0);

    // R1 -- offset pointer to memory
 //   jit_movi(JIT_R1, 0);

    for ( int c=0; c != EOF; c = fgetc(f) ) {
      switch ( c ) {
        case '<':
          break;
        case '>':
          break;
        case '+':
          break;
        case '-':
          break;
        case '[':
          break;
        case ']':
          break;
        default:
          break;
      }
    }

    code = reinterpret_cast<vfptr>(jit_emit());
  }

  void run()
  {
    printf("running\n");
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
