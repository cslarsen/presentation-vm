#include <errno.h>
#include <stdint.h>
#include <stdio.h>

#include <stack>

extern "C" {
#include <lightning.h>
}

typedef void (*vfptr)(void);

static jit_state_t *_jit;

struct Loop {
  jit_node_t *body;
  jit_node_t *end;

  Loop(jit_node_t* body_ = NULL, jit_node_t* end_ = NULL):
    body(body_), end(end_)
  {
  }

  Loop(const Loop& l):
    body(l.body), end(l.end)
  {
  }

  Loop& operator=(const Loop& l) {
    if ( this != &l ) {
      body = l.body;
      end = l.end;
    }
    return *this;
  }
};

jit_pointer_t compile(FILE *f, uint8_t *memory)
{
  jit_prolog();
  jit_movi(JIT_V0, reinterpret_cast<jit_word_t>(memory)); // base
  jit_movi(JIT_V1, 0); // offset

  std::stack<Loop> loops;

  for ( int c=0; c != EOF; c = fgetc(f) ) {
    switch ( c ) {
      case '<':
        jit_subi(JIT_V1, JIT_V1, 1);
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
        jit_subi(JIT_V2, JIT_V2, 1);
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
        Loop loop;

        // if ( *value == 0 ) goto loop.end;
        loop.end = jit_forward();
        jit_ldxr(JIT_V2, JIT_V0, JIT_V1);
        jit_node_t *j = jit_beqi(JIT_V2, 0);
        jit_patch_at(j, loop.end);

        // mark loop body
        loop.body = jit_label();
        loops.push(loop);
      } break;
      case ']': {
        Loop loop = loops.top();
        loops.pop();

        // if ( *value != 0 ) goto loop.body;
        jit_ldxr(JIT_V2, JIT_V0, JIT_V1);
        jit_node_t *j = jit_bnei(JIT_V2, 0);
        jit_patch_at(j, loop.body);

        // mark loop end
        jit_link(loop.end);
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

  for ( int n=1; n<argc; ++n ) {
    if ( argv[n][0] == '-' && argv[n][1] != '\0' )
      continue;

    FILE *f = !strcmp(argv[n], "-")? stdin : fopen(argv[n], "rt");

    if ( !f ) {
      perror(argv[n]);
      return 1;
    } else {
      Machine p;
      p.compile(f);
      fclose(f);
      jit_clear_state();
      p.run();
    }
  }

  jit_destroy_state();
  finish_jit();
  return 0;
}
