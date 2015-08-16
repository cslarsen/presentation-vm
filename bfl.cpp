#include <stdio.h>
#include <stdint.h>
#include <stack>

extern "C" {
#include <lightning.h>
}

static jit_state_t *_jit;
typedef void (*vfptr)(void);
typedef std::pair<jit_node_t*, jit_node_t*> label_pair;

jit_pointer_t compile(FILE *f, uint8_t *memory)
{
  jit_prolog();
  jit_movi(JIT_V0, reinterpret_cast<jit_word_t>(memory)); // base
  jit_movi(JIT_V1, 0); // offset

  std::stack<label_pair> loops;

  for ( int c=0; c != EOF; c = fgetc(f) ) {
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
        jit_prepare();
        jit_finishi(reinterpret_cast<jit_pointer_t>(getchar));
        jit_retval(JIT_V2);
        jit_stxr(JIT_V0, JIT_V1, JIT_V2);
        break;
      case '[': {
        label_pair pair;
        pair.first = jit_label();
        pair.second = jit_forward();
        jit_ldxr(JIT_V2, JIT_V0, JIT_V1);
        jit_node_t* jump = jit_beqi(JIT_V2, 0);
        jit_patch_at(jump, pair.second);

        loops.push(pair);
      } break;
      case ']': {
        label_pair pair = loops.top();
        loops.pop();

        jit_node_t* p = jit_movi(JIT_V2, 0);
        jit_jmpr(JIT_V2);
        jit_patch_at(p, pair.first);
        jit_link(pair.second);

        break;
      }
      default:
        break;
    }
  }

  jit_epilog();
  return jit_emit();
}

struct Machine {
  uint8_t *memory;
  vfptr program;

  Machine(const size_t memsize = 100000)
    : memory(static_cast<uint8_t*>(malloc(sizeof(uint8_t)*memsize))),
      program(NULL)
  {
    memset(memory, 0, sizeof(uint8_t)*memsize);
  }

  void compile(FILE* f)
  {
    program = reinterpret_cast<vfptr>(::compile(f, memory));
  }

  ~Machine()
  {
    free(memory);
  }

  void run()
  {
    program();
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
      Machine p;
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
