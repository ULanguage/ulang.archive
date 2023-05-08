# ULang > Calling Convention

## Functions with parameters and return values
All functions receive two arguments:
  * A pointer to the base of the params struct  
  * A pointer to the base of the returns struct  
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
struct add__params_t {
  int64 param0;
  int64 param1;
};

struct add__rets_t {
  int64 ret0;
  bool ret1;
};

void add(struct add__params_t *params, struct add__rets_t *rets);
```
And would be called like this:
```c
#include "add.h"

int main() {
  struct add__params_t param = { 27, 15 };
  struct add__rets_t rets;
  add(&param, &rets);

  /* Use rets */
}
```

### Functions without parameters or return values
If a function doesn't have parameters or return values, it doesn't expect anything:
```ulang
fun paramsOnly(int64 a) {
 /* ... */
}

fun retsOnly() int64 {
 /* ... */
}

fun neither() {
 /* ... */
}
```

```c
void paramsOnly(struct paramsOnly__params_t *params);
void retsOnly(struct retsOnly__rets_t *rets);
void neither();
```

### Struct methods
Struct methods also receive the data structure as an extra argument.  
See more in `data_structures.md`.  

## Plans
* I would like to also return an error code for error-checking
