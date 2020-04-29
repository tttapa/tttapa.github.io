# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
export PATH

# set MANPATH so it includes user's private man if it exists
if [ -d "$HOME/.local/man" ] ; then
    MANPATH="$HOME/.local/man:"
fi
if [ -d "$HOME/.local/share/man" ] ; then
    MANPATH="$HOME/.local/share/man:$MANPATH"
fi
export MANPATH

# set PKG_CONFIG_PATH so it includes user's private pkgconfig if it exists
if [ -d "$HOME/.local/lib/pkgconfig" ] ; then
    PKG_CONFIG_PATH="$HOME/.local/lib/pkgconfig:$PKG_CONFIG_PATH"
fi
if [ -d "$HOME/.local/share/pkgconfig" ] ; then
    PKG_CONFIG_PATH="$HOME/.local/share/pkgconfig:$PKG_CONFIG_PATH"
fi
export PKG_CONFIG_PATH

# set CMAKE_PREFIX_PATH so it includes user's private prefix if it exists
if [ -d "$HOME/.local" ] ; then
    CMAKE_PREFIX_PATH="$HOME/.local:$CMAKE_PREFIX_PATH"
fi
export CMAKE_PREFIX_PATH
