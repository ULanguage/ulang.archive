# ULang > Calling Convention

## Functions with parameters and return values
All functions receive two arguments:
  * On `rdi` a pointer to the base of the params struct  
  * On `rsi` a pointer to the base of the returns struct  
And the return values are put on the returns struct.  

This way, the next function
```ulang
fun add(int64 a, b) (int64, bool) {
  int64 res = a + b
  return res, res == 42
}
```
Would have the following C header:
```c
struct ADDParams_t {
  int64 a,
        b;
};

struct ADDRets_t {
  int64 ret0;
  bool ret1;
};

void add(struct ADDParams_t *params, struct ADDRets_t *rets);
```
And would be called like this:
```c
#include "add.h"

int main() {
  struct ADDParams_t param = { 27, 15 };
  struct ADDRets_t rets;
  add(&param, &rets);

  /* Use rets */
}
```

## Plans
* I would like to also return an error code for error-checking
