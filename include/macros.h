#pragma once

#define DEBUG 1

#define TRY(expr) if(!(expr)) goto catch;
#define CATCH(statements) catch: statements
#define THROW 0

#define DEBUG_PRINT(str) if (DEBUG) { printf(str); printf("\n"); }