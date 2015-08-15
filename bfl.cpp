#include <stdio.h>

extern "C" {
#include <lightning.h>
}

static jit_state_t *_jit;

typedef int (*pifi)(int);    /* Pointer to Int Function of Int */

int main(int argc, char *argv[])
{
  jit_node_t  *in;
  pifi         incr;

  init_jit(argv[0]);
  _jit = jit_new_state();

  jit_prolog();                    /*      prolog              */
  in = jit_arg();                  /*      in = arg            */
  jit_getarg(JIT_R0, in);          /*      getarg R0           */
  jit_addi(JIT_R0, JIT_R0, 1);     /*      addi   R0, R0, 1    */
  jit_retr(JIT_R0);                /*      retr   R0           */

  incr = (pifi)jit_emit();
  jit_clear_state();

  /* call the generated code, passing 5 as an argument */
  printf("%d + 1 = %d\n", 5, incr(5));

  jit_destroy_state();
  finish_jit();
  return 0;
}
