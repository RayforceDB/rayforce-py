%module rayforce

/* Tell SWIG this is a C module */
#define SWIGWORDSIZE64
%{
#define SWIG_FILE_WITH_INIT
#define _GNU_SOURCE
#include <Python.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include "rayforce.h"
#include "math.h"
#include "vary.h"
%}

%begin %{
#define _GNU_SOURCE
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
%}

/* Ignore the flexible array member */
%ignore obj_t::arr;

/* Include the header */
%include "rayforce.h"
%include "math.h"
%include "vary.h"
