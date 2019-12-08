#pragma once

#define DEBUG 1

#define TRY(expr) if(!(expr)) goto catch;
#define CATCH(statements) catch: statements
#define THROW 0

#include <stdio.h>
#define DEBUG_PRINT(...) if (DEBUG) { printf(__VA_ARGS__); printf("\n"); }