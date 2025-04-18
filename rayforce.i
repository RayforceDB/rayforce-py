%module rayforce

%{
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "rayforce.h"
%}

%ignore obj_t::arr; // Ignore the flexible array member

%include "rayforce.h"