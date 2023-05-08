# ULang > Register Management

Each expression allocs and frees registers as needed.
* If at any point there would be no free registers, then the expression still gets a register and adds a push/pop operation to restore it before/after using it.  
  This can be optimized by not popping if the next expression also needs this register.  
  It can also be optimized by having the preserved registers be pushed/popped by the function expression.  
  WARNING! Stack alignment on calls.
