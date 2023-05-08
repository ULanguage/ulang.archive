# ULang > Data Structures

## Alignment
To make U compatible with C, data structures are also aligned.  
The struct's fields are sorted to minimize it's size.  
This way the following structure:
```ulang
type Example = struct {
  char c
  int32 i
  char d
}
```
Will have the following C header
```c
struct Example {
  int32 i;
  char c;
  char d;
};
```

## Methods
```ulang
type Example = struct {
  int32 a, b
}

fun (*Example e) add() int32 {
  return e.a + a.b
}
```

```c
struct Example {
  int32 a;
  int32 b;
};

struct Example__add__rets_t {
  int32 ret0;
};

void Example__add(struct Example__add__rets *rets, struct Example *on);
```

```c
#include "example.h"

int main() {
  struct Example e = {6, 7};

  struct Example__add__rets rets;
  Example__add(&rets, &e);

  /* Use rets... */
}
```
