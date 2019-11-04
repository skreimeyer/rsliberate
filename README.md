This is a mostly unsuccessful attempt at creating a tool that can automatically make all private objects in a rust source code directory public and then address common errors that occur.

Unfortunately, source with custom macros cannot be handled reliably because the syntax within a macro invocation does not have to be consistent with syntax in the rest of the language.

This could potentially be useful to some, but expect difficult to manage errors.
