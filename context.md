This library is an ORM built around the database called rayforce. The rayforce had 2 versions: v1 and v2. Python speaks the rayforce via the C API bus, explore C files in this repo.
We need to migrate the library from using the v1 core to use the v2 core. This is a hard task to accomplish, which requires extra consideration and attention.

The rayforce database source code can be found in ~/rayforce. To get the v1 core code, navigate to the 6f6be332 commit (this is the last v1 commit). To get the v2 source code, just get latest master from the folder.

Most of the work has already been done - tests are passing.

Do not use any historical memory, speak only of what you have seen in here and in rayforce core.


Your target here is to inspect the source code of this library, and rayforce, see the things which have been not working the same way since v1. (like table and vector operations), and fix those issues.

The special attention has to be paid towards code quality. Acknowledge CLAUDE.md. Make code readable, slim, having the rayforce-py v1 version as a greatest reference you ever had.

Ask me questions if uncertain.

Performance here is a key, so while you are developing, you also need to make the shim as small as possible, so we can achieve native performance.

Also, the v2 core doesn't have a raykx plugin, which was a part of v1 core. The v2 takes another approach of delegating the KDB IPC to the Python layer. Ensure the integration works properly.

Also, ensure the namings for things are correct and aligning with v1 standards.

propose comperehsive solution and start work
