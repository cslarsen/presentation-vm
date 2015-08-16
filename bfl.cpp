#include <stdio.h>

extern "C" {
#include <lightning.h>
}

static jit_state_t *_jit;

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

int main(int argc, char *argv[])
{
  for ( size_t n=1; n<argc; ++n ) {
    if ( argv[n][0] == '-' )
      continue;
    FILE *f = fopen(argv[n], "rt");
    if ( f ) {
      compile(f);
      fclose(f);
    }
  }

  return 0;
}
