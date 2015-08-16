#include <stdio.h>
#include <stdint.h>

extern "C" {
#include <lightning.h>
}

static jit_state_t *_jit;

struct Program {
  uint8_t *memory;

  Program(const size_t memsize = 100000)
    : memory(new uint8_t[memsize])
  {
  }

  ~Program()
  {
    delete[](memory);
  }

  void compile(FILE *f)
  {
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
  }

  void run()
  {
  }
};

int main(int argc, char *argv[])
{
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

  return 0;
}
